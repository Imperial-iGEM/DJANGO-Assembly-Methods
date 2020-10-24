import plateo
import plateo.containers
import plateo.tools
import warnings
import pandas as pd
import numpy as np
import os
from typing import List, Dict, Tuple, Union
from rdflib import URIRef
from sbol2 import *
from collections import deque
from random import sample
from plateo.exporters import plate_to_platemap_spreadsheet


class ParserSBOL:
    def __init__(
        self,
        sbol_document: Document,
        outdir: str = os.getcwd(),
        linker_file: Document = Document(os.path.join(os.getcwd(), "basic_linkers_standard.xml"))
    ):
        self.doc = sbol_document
        self.outdir = outdir
        self.linker_file = linker_file
        self.construct_csv_paths = []
        self.part_csv_paths = []
        self.assembly_types = ["basic", "moclo", "bio_bricks"]

    def generate_csv(
            self,
            assembly: str,
            part_info: Dict[str, Dict[str, Union[str, int, float]]] = None,
            repeat: bool = False,
            max_construct_wells: int = 96,
            num_runs: int = 1
    ) -> Dict[str, List[str]]:
        """Create construct and parts/linkers CSVs for DNABot input
        Args:
            assembly(str): Assembly type.
            part_info (Dict[str, Dict[str, Union[str, int, float]]]): 
                Dictionary of information regarding parts to be assembled.
                Structure:
                {<display ID>: {'concentration':..., 'plate':..., 'well':...}}
            repeat (bool): If False, removes constructs that contain repeated
                components. (default: False)
            max_construct_wells (int): Number of wells to be filled in the
                constructs plate. (default: 96)
            num_runs (int): Number of runs (i.e. construct plates) to be
                created. (default: 1)
        Returns:
            Dict[str,List[str]]: Dictionary containing lists of paths to csvs
                generated.
        Raises:
            ValueError: If `assembly` is invalid.
        """
        if assembly not in self.assembly_types:
            raise ValueError("Invalid assembly type: %s" % assembly)
        num_samples = max_construct_wells * num_runs
        all_constructs = []
        print("Assembly Method: %s" % assembly)
        # Get list of constructs
        all_constructs = self.get_constructs()
        # Remove constructs with repeated parts using a filter
        if not repeat:
            all_constructs = self.filter_constructs(all_constructs)
        # Sample constructs
        if len(all_constructs) < num_samples:
            num_samples = len(all_constructs)
            print(
                "Number of constructs specified is greater than number "
                "of constructs contained within SBOL Document provided."
            )
            print("All constructs will be assembled.")
        sampled = sample(all_constructs, num_samples)
        # Display number of Component Definitions to be constructed
        num_designs = len(sampled)
        print(num_designs, "construct(s) will be assembled.")
        # Create plateo construct plates
        construct_plates = self.fill_plates(
            sampled,
            "Construct",
            num_runs,
            plateo.containers.Plate96,
            max_construct_wells
        )
        for plate in construct_plates:
            # Create construct CSV
            self.get_construct_csv_from_plate(plate, assembly)
            # Write parts/linkers csv
            self.get_part_linker_csv_from_plate(
                plate,
                assembly,
                part_info
            )
        filepaths = {}
        filepaths['construct_path'] = self.construct_csv_paths
        filepaths['part_path'] = self.part_csv_paths
        return filepaths

    def get_root_compdefs(
            self,
            sbol_document: Document = None
    ) -> List[ComponentDefinition]:
        """Get the root component definitions of an SBOL document.
        Args:
            sbol_document (Document): SBOL document from
                which to get root component definitions (default: self.doc)
        Returns:
            list: List of root component definitions.
        """
        sbol_document = self.doc if sbol_document is None else sbol_document
        compdefs = list(sbol_document.componentDefinitions)
        # Remove child components of component definitions
        for obj in sbol_document.componentDefinitions:
            for component in obj.components:
                child_def = \
                    sbol_document.getComponentDefinition(component.definition)
                if(child_def
                        is not None and child_def in compdefs):
                    compdefs.remove(child_def)
        # Remove child components of combinatorial derivations
        for obj in sbol_document.combinatorialderivations:
            for varcomp in obj.variableComponents:
                for variant in varcomp.variants:
                    child_def = sbol_document.getComponentDefinition(variant)
                    if(child_def is not None and child_def in compdefs):
                        compdefs.remove(child_def)
        # Remove Templates
        for obj in sbol_document.combinatorialderivations:
            template = sbol_document.getComponentDefinition(obj.masterTemplate)
            if (template is not None and template in compdefs):
                compdefs.remove(template)
        return list(compdefs)

    def get_root_combderivs(
        self,
        sbol_document: Document = None
    ) -> List[CombinatorialDerivation]:
        """Get the root combinatorial derivations of an SBOL Document.
        Args:
            sbolDocument (Document): SBOL document from
                which to get root combinatorial derivations (default: self.doc)
        Returns:
            list: List of root combinatorial derivations.
        """
        sbol_document = self.doc if sbol_document is None else sbol_document
        combderivs = list(sbol_document.combinatorialderivations)
        for obj in sbol_document.combinatorialderivations:
            for vc in obj.variableComponents:
                if vc.variantDerivations is not None:
                    for vd in vc.variantDerivations:
                        child_deriv = sbol_document.combinatorialderivations.get(vd)
                        if (child_deriv
                                is not None and child_deriv in combderivs):
                            combderivs.remove(child_deriv)
        return combderivs

    def get_constructs(
            self,
            non_comb_uris: List[str] = [],
            comb_uris: List[str] = []
    ) -> List[ComponentDefinition]:
        """Get the list of constructs (component definitions) specified by
        the list of non-combinatorial URIs and combinatorial derivation URIs.
        Expands combinatorial derivations.
        Args:
            non_comb_uris (list): List of component definition
                URIs pointing to non-combinatorial designs.
            comb_uris (list): List of combinatorial derivation
                URIs pointing to combinatorial designs.
        Returns:
            list: List of component definitions specifying constructs
                to be assembled
        """
        constructs = []
        print("Obtaining constructs from SBOL Document...")
        # Add non-combinatorial constructs to list
        if non_comb_uris == []:
            # Get all root component definitions and append to list
            constructs.extend(self.get_root_compdefs())
        else:
            for uri in non_comb_uris:
                constructs.append(self.doc.getComponentDefinition(uri))
        # Add combinatorial constructs to list
        print("Enumerating Combinatorial Derivations...")
        if comb_uris == []:
            # Get all root combinatorial derivations
            combderivs = self.get_root_combderivs()
            # Enumerate all root combinatorial derivations and append to list
            for combderiv in combderivs:
                constructs.extend(self.enumerator(combderiv))
        else:
            for uri in comb_uris:
                # Enumerate Combinatorial Derivations and add to allConstructs
                constructs.extend(self.enumerator(
                    self.doc.combinatorialderivations.get(uri)))
        print("Completed.")
        return constructs

    def enumerator(
        self,
        derivation: CombinatorialDerivation
    ) -> List[ComponentDefinition]:
        """Get the list of constructs enumerated from a combinatorial derivation..
        Args:
            derivation (CombinatorialDerivation): Combinatorial derivation
                to be enumerated.
        Returns:
            list: List of component definitions specifying the
                enumerated constructs.
        """
        parents = []
        template = self.doc.getComponentDefinition(derivation.masterTemplate)
        template_copy =\
            self.create_template_copy(template, template.displayId + "_Var", "1")
        parents.append(template_copy)
        for vc in derivation.variableComponents:
            new_parents = []
            for parent in parents:
                for children in self.group(
                        self.collect_variants(vc),
                        "http://sbols.org/v2#one"):
                    var_displayid = self.conc_children_displayid(children)
                    if parent.persistentIdentity + "_" + var_displayid + "/1" \
                            not in [cd.identity for cd in self.doc.componentDefinitions]:
                        # Create parent copy
                        unique_id = self.get_unique_displayid(
                            None,
                            None,
                            parent.displayId + "_" + var_displayid,
                            parent.version,
                            "CD",
                            self.doc
                        )
                        new_parent = self.create_template_copy(
                            parent,
                            unique_id,
                            "1"
                        )
                        self.doc.add(new_parent)
                    else:
                        # Set newParent to existing CD
                        new_parent = self.doc.getComponentDefinition(
                            parent.persistentIdentity + "_" + var_displayid + "/1"
                        )
                    # Add children
                    self.add_children(
                        template,
                        template.components[vc.variable],
                        new_parent,
                        children
                    )
                    # Add to newParents
                    new_parents.append(new_parent)
            parents = new_parents
        return parents

    def add_children(
        self,
        orig_template: ComponentDefinition,
        orig_comp: Component,
        new_parent: ComponentDefinition,
        children: List[ComponentDefinition]
    ):
        """Adds children to new parent component definition based on the
        original template.
        Args:
            orig_template (ComponentDefinition): Original template
                describing the design of the new parent
            orig_comp (Component): Variable component in the
                original template to be replaced in new parent
            new_parent (ComponentDefinition): New component definition
                describing an enumerated design
            children (List[ComponentDefinition]): Children to be added
                to the new parent based on the variants
        """
        new_comp = new_parent.components[orig_comp.displayId]
        new_comp.wasDerivedFrom = orig_comp.identity
        if children is None:
            self.remove_constr_refs(new_parent, new_comp)
            for sa in new_parent.sequenceAnnotations:
                if sa.component \
                        is not None and sa.component == new_comp.identity:
                    new_parent.sequenceAnnotations.remove(sa.identity)
            new_parent.components.remove(new_comp.identity)
            return
        first = True
        for child in children:
            if first:
                # Take over definition of
                # newParent's version of original component
                new_comp.definition = child.identity
                first = False
            else:
                # Create new component
                unique_id = self.get_unique_displayid(
                    new_parent,
                    None,
                    child.displayId + "_Component", "1",
                    "Component",
                    None)
                link = new_parent.components.create(unique_id)
                link.definition = child.persistentIdentity
                link.access = SBOL_ACCESS_PUBLIC
                link.version = child.version
                link.wasDerivedFrom = orig_comp.identity
                # Create a new 'prev precedes link' constraint
                if orig_template.hasUpstreamComponent(orig_comp):
                    old_prev = orig_template.getUpstreamComponent(orig_comp)
                    if old_prev.identity in new_parent.components:
                        new_prev = new_parent.components[old_prev.identity]
                        unique_id = self.get_unique_displayid(
                            new_parent,
                            None,
                            new_parent.displayId + "_SequenceConstraint",
                            None,
                            "SequenceConstraint",
                            None
                        )
                        new_seqconstr = \
                            new_parent.sequenceConstraints.create(unique_id)
                        new_seqconstr.subject = new_prev.identity
                        new_seqconstr.object = link.identity
                        new_seqconstr.restriction = SBOL_RESTRICTION_PRECEDES
                # Create new 'link precedes next' constraint
                if orig_template.hasDownstreamComponent(orig_comp):
                    old_next = orig_template.getDownstreamComponent(orig_comp)
                    if old_next.identity in new_parent.components:
                        new_next = new_parent.components[old_next.identity]
                        unique_id = self.get_unique_displayid(
                            new_parent,
                            None,
                            new_parent.displayId + "_SeqeunceConstraint",
                            None,
                            "SequenceConstraint",
                            None
                        )
                        new_seqconstr = \
                            new_parent.sequenceConstraints.create(unique_id)
                        new_seqconstr.subject = link.identity
                        new_seqconstr.object = new_next.identity
                        new_seqconstr.restriction = SBOL_RESTRICTION_PRECEDES

    def remove_constr_refs(
        self,
        new_parent: ComponentDefinition,
        new_comp: Component
    ):
        """Remove sequence constraints of the component in the component definition
        Args:
            new_parent (ComponentDefinition): Component definition containing
                the new component.
            new_comp (Component): Component to remove sequence
                constraints from.
        """
        subj = None
        obj = None
        for sc in new_parent.sequenceConstraints:
            if sc.subject == new_comp.identity:
                obj = new_parent.components[sc.object]
                if subj is not None:
                    sc.subject = subj
                    obj = None
                    subj = None
                else:
                    new_parent.sequenceConstraints.remove(sc.identity)
            if sc.object == new_comp.identity:
                subj = new_parent.components[sc.subject]
                if obj is not None:
                    sc.object = obj
                    obj = None
                    subj = None
                else:
                    new_parent.sequenceConstraints.remove(sc.identity)

    def create_template_copy(
        self,
        template: ComponentDefinition,
        displayid: str,
        version: str
    ) -> ComponentDefinition:
        """Create a copy of the template of the combinatorial derivation.
        Args:
            template (ComponentDefinition): Template of the
                combinatorial derivation.
            displayid (str): Display ID to be assigned to the copy.
            version (str): Version of the copy.
        Returns:
            ComponentDefinition: Copy of template.
        """
        new_displayid = URIRef(displayid)
        template_copy = ComponentDefinition(
            new_displayid,
            template.types,
            version
        )
        template_copy.roles = template.roles
        pri_struct = template.getPrimaryStructureComponents()
        curr = None
        prev = None
        for c in pri_struct:
            curr = template_copy.components.create(c.displayId)
            curr.access = c.access
            curr.definition = c.definition
            if prev is not None:
                unique_id = self.get_unique_displayid(
                    template_copy,
                    None,
                    template_copy.displayId + "_SequenceConstraint",
                    None,
                    "SequenceConstraint",
                    None
                )
                sc = template_copy.sequenceConstraints.create(unique_id)
                sc.subject = prev.identity
                sc.object = curr.identity
                sc.restriction = SBOL_RESTRICTION_PRECEDES
            prev = curr
        template_copy.wasDerivedFrom = [template.identity]
        for c in template_copy.components:
            component = template.components[c.displayId]
            c.wasDerivedFrom = component.identity
        return template_copy

    def get_unique_displayid(
        self,
        comp: ComponentDefinition = None,
        derivation: CombinatorialDerivation = None,
        displayid: str = None,
        version: str = None,
        data_type: str = None,
        doc: Document = None
    ) -> str:
        """Create a unique display ID for an SBOL object.
        Args:
            comp (ComponentDefinition): Component definition containing
                the SBOL object
            derivation (CombinatorialDerivation): Combinatorial derivation
                containing the SBOL object
            displayid (str): Base display ID for SBOL object.
            version (str): Version of SBOL object.
            data_type (str): Type of SBOL object.
            doc (str): SBOL Document containing the SBOL object.
        Returns:
            str: Unique display ID of SBOL object.
        Raises:
            ValueError: Invalid data type.
        """
        i = 1
        if data_type == "CD":
            unique_uri = getHomespace() + displayid + "/" + version
            # while doc.find(uniqueUri):
            while unique_uri \
                    in [cd.displayId for cd in doc.componentDefinitions]:
                i += 1
                unique_uri = \
                    getHomespace() + "%s_%d/%s" % (displayid, i, version)
            if i == 1:
                return displayid
            else:
                return displayid + "_" + str(i)
        elif data_type == "SequenceAnnotation":
            while displayid \
                    in [sa.displayId for sa in comp.sequenceAnnotations]:
                i += 1
                displayid = displayid + str(i)
            if i == 1:
                return displayid
            else:
                return displayid
        elif data_type == "SequenceConstraint":
            while displayid \
                    in [sc.displayId for sc in comp.sequenceConstraints]:
                i += 1
                displayid = displayid + str(i)
            if i == 1:
                return displayid
            else:
                return displayid
        elif data_type == "Component":
            while displayid in [c.displayId for c in comp.components]:
                i += 1
                displayid = displayid + str(i)
            if i == 1:
                return displayid
            else:
                return displayid
        elif data_type == "Sequence":
            unique_uri = getHomespace() + displayid + "/" + version
            while doc.find(unique_uri):
                i += 1
                unique_uri = \
                    getHomespace() + "%s_%d/%s" % (displayid, i, version)
            if i == 1:
                return displayid
            else:
                return displayid + str(i)
        # TODO: Range
        elif data_type == "CombinatorialDerivation":
            unique_uri = getHomespace() + displayid + "/" + version
            while doc.find(unique_uri):
                i += 1
                unique_uri = \
                    getHomespace() + "%s_%d/%s" % (displayid, i, version)
            if i == 1:
                return displayid
            else:
                return displayid + str(i)
        elif data_type == "VariableComponent":
            while displayid + str(i) \
                    in [vc.displayId for vc in derivation.variableComponents]:
                i += 1
                displayid = displayid + str(i)
            if i == 1:
                return displayid
            else:
                return displayid
        else:
            raise ValueError("Invalid data type.")

    def conc_children_displayid(
        self,
        children: List[ComponentDefinition]
    ) -> str:
        """Concatenate the names of the variant child components.
        Args:
            children (List[ComponentDefinition]): List of variant
                child components of an enumerated design (as
                component definition).
        Returns:
            str: Concanated names of variant child components.
        """
        conc_displayid = ""
        for child in children:
            conc_displayid = conc_displayid + child.displayId
        return conc_displayid

    def collect_variants(
        self,
        vc: VariableComponent
    ) -> List[ComponentDefinition]:
        """Collect all variants within a variable component
        of a combinatorial derivation.
        Args:
            vc (VariableComponent): Variable component of a
                combinatorial derivation.
        Returns:
            List[ComponentDefinition]: List of variants (as
                component definitions) contained within a
                variable component of a combinatorial derivation.
        """
        variants = []
        # Add all variants
        for v in vc.variants:
            variant = self.doc.componentDefinitions.get(v)
            variants.append(variant)
        # Add all variants from Variant Collections
        for c in vc.variantCollections:
            for m in c.members:
                tl = self.doc.get(m)
                if type(tl) == ComponentDefinition:
                    variants.add(tl)
        for derivation in vc.variantDerivations:
            variants.extend(self.enumerator(self.doc.get(derivation)))
        return variants

    def group(
        self,
        variants: List[ComponentDefinition],
        repeat: str
    ) -> List[List[ComponentDefinition]]:
        """Groups variants based on combinatorial strategy.
        Args:
            variants (List[ComponentDefintiion]): List of variants
                in a variable component.
        Returns:
            List[List[ComponentDefinition]]: Groups of variants.
        """
        groups = []
        for cd in variants:
            group = []
            group.append(cd)
            groups.append(group)
        if repeat == "http://sbols.org/v2#one":
            return groups
        if repeat == "http://sbols.org/v2#zeroOrOne":
            groups.append([])
            return groups
        groups.clear()
        self.generate_combinations(groups, variants, 0, [])
        if repeat == "http://sbols.org/v2#oneOrMore":
            return groups
        if repeat == "http://sbols.org/v2#zeroOrMore":
            groups.append([])
            return groups

    def generate_combinations(
        self,
        groups: List[List[ComponentDefinition]],
        variants: List[ComponentDefinition],
        i: int,
        sets: List[ComponentDefinition]
    ):
        """Generate all possible subsets in a set of variants.
        Args:
            groups (List[List[ComponentDefintiion]]): Groups of variants.
            variants (List[ComponentDefinition]): List of variants (as
                component definitions).
            i (int): Iterator.
            sets (List[ComponentDefinition]): Sets of variants.
        """
        if i == len(variants):
            if not sets:
                groups.add(sets)
            return
        no = sets.copy()
        self.generate_combinations(groups, variants, i + 1, no)
        yes = sets.copy()
        yes.add(variants[i])
        self.generate_combinations(groups, variants, i + 1, yes)

    def filter_constructs(
        self,
        all_constructs: List[ComponentDefinition]
    ) -> List[ComponentDefinition]:
        """Removes constructs with repeated components.
        Args:
            all_constructs (List[ComponentDefinition]): List of constructs
                to filter.
        Returns:
            List[ComponentDefinition]: List of filtered constructs.
        """
        # TODO: Filter constructs based on more user specifications
        filtered = []
        print("Removing designs with repeated parts...")
        for construct in all_constructs:
            # Flatten construct
            flattened = self.flatten(construct)
            # Get list of displayIds
            ids = [cd.displayId for cd in flattened]
            # Check for repeats
            if len(ids) == len(set(ids)):
                filtered.append(construct)
        print("Completed.")
        return filtered

    def flatten(
        self,
        construct: ComponentDefinition
    ) -> List[ComponentDefinition]:
        """Flattens a heirarchical component definition.
        Args:
            construct (ComponentDefinition): Component definition to
                flatten.
        Returns:
            List[ComponentDefinition]: Returns a list of component
                definitions corresponding to the components contained
                within the component definition including all
                nested components.
        """
        d = deque(construct.getPrimaryStructure())
        all_comps = []
        while(d):
            comp = d.popleft()
            if(comp.components):
                d.extendleft(reversed(comp.getPrimaryStructure()))
            else:
                all_comps.append(comp)
        return all_comps

    def display_parts(
        self,
    ) -> List[str]:
        # TODO: Test if robust to multiple nested variant derivations
        """Displays list of parts used in the assembly of the constructs
        in the SBOL document used to initialize the parser.
        Returns:
            List[str]: List of display IDs of parts.
        """

        def get_ext_displayid(
            combderiv: CombinatorialDerivation
        ) -> List[str]:
            """Get the display ID extensions of an enumerated combinatorial derivation.
            Args:
                combderiv: Combinatorial derivation to be enumerated.
            Returns:
                List[str]: List of display ID extensions.
            """
            ext_displayids = []
            for vc in combderiv.variableComponents:
                for v in vc.variants:
                    cd = self.doc.getComponentDefinition(v)
                    ext_displayids.append("_Var_" + cd.displayId)
                for c in vc.variantCollections:
                    for m in c.members:
                        tl = self.doc.get(m)
                        if type(tl) == ComponentDefinition:
                            ext_displayids.append("_Var_" + tl.displayId)
                for vd in vc.variantDerivations:
                    combderiv = self.doc.get(vd)
                    template = combderiv.masterTemplate
                    ext_displayids.extend(
                        [template.displayId + edi
                            for edi in get_ext_displayid(combderiv)]
                    )
            return ext_displayids

        parts = []
        root_compdefs = []
        # Get all root component definitions from document
        root_compdefs.extend(self.get_root_compdefs())
        # Add all parts in each root cds
        for cd in root_compdefs:
            for c in cd.components:
                compdef = self.doc.getComponentDefinition(c.definition)
                parts.append(compdef.displayId)
        # Get all root combinatorial derivations
        root_combderivs = self.get_root_combderivs()
        for combderiv in root_combderivs:
            # Get master template
            template = \
                self.doc.getComponentDefinition(combderiv.masterTemplate)
            variables = \
                [vc.variable for vc in combderiv.variableComponents]
            # Add components of template that are not variables
            for c in template.components:
                if c.identity not in variables:
                    cd = self.doc.getComponentDefinition(c.definition)
                    parts.append(cd.displayId)
            # Append variants
            for vc in combderiv.variableComponents:
                for v in vc.variants:
                    cd = self.doc.getComponentDefinition(v)
                    parts.append(cd.displayId)
                for c in vc.variantCollections:
                    for m in c.members:
                        tl = self.doc.get(m)
                        if type(tl) == ComponentDefinition:
                            parts.append(tl.displayId)
                for vd in vc.variantDerivations:
                    deriv = self.doc.get(vd)
                    template = \
                        self.doc.getComponentDefinition(deriv.masterTemplate)
                    parts.extend(
                        [template.displayId + ext_displayid
                            for ext_displayid in get_ext_displayid(deriv)]
                    )
        parts = list(dict.fromkeys(parts))
        # Get list of linkers from linkerfile
        linkers = self.get_root_compdefs(self.linker_file)
        # Convert linkers into linker suffix and prefix and add to new list
        new_parts = []
        for part in parts:
            if part in [linker.displayId for linker in linkers]:
                new_parts.append(part + "_Suffix")
                new_parts.append(part + "_Prefix")
            else:
                new_parts.append(part)
        return sorted(new_parts)

    def get_parts(
        self,
        all_constructs: List[ComponentDefinition] = []
    ) -> List[ComponentDefinition]:
        """Get list of parts (component defintions) from the list of
        all constructs.
        Args:
            all_constructs (list): List of all constructs to be assembled.
        Returns:
            list: List of component definitions specifying parts used across
                all constructs to be assembled.
        """
        parts = []
        # Add components from all component definitions in allConstructs
        for construct in all_constructs:
            for component in construct.components:
                parts.append(
                    self.doc.getComponentDefinition(component.definition)
                )
        # Remove duplicate components
        parts = list(dict.fromkeys(parts))
        return parts

    def get_sorted_parts(
        self,
        parts: List[ComponentDefinition]
    ) -> List[ComponentDefinition]:
        """Get a sorted list of parts (str) from the list of parts.
        Sort by sbol2 displayId
        Args:
            parts (list): List of parts to be sorted. (generated
                by getListOfConstructs)
        Returns:
            list: List of sorted parts (str)
        """
        parts.sort(key=lambda x: x.displayId)
        return parts

    def get_comp_dict(
        self,
        constructs: List[ComponentDefinition]
    ) -> Dict[str, ComponentDefinition]:
        """Get a dictionary of components (as component definitions)
        from the list of constructs as
        {construct.displayId: construct.components (as component definitions)}
        Args:
            constructs (list): List of constructs
        Returns:
            dict: Dictionary of components
        """
        return {x.displayId: x.getPrimaryStructure() for x in constructs}

    def fill_plates(
        self,
        all_content: List[ComponentDefinition],
        content_name: str,
        num_plate: int = None,
        plate_class: plateo.Plate = None,
        max_construct_wells: int = None,
        part_info: Dict[str, Dict[str, Union[str, int, float]]] = None
    ) -> List[plateo.Plate]:
        """Generate a list of plateo plate objects from list of constructs
        Args:
            all_content (list): List of constructs.
            content_name (str): Name of content (construct or part).
            num_plate (int): Number of plates to be generated (default = 1).
            plate_class (plateo.Plate):
                Class of plateo plate (default = Plate96).
            max_construct_wells (int): Maximum number of filled wells on a plate.
            part_info (Dict[str, Dict[str, Union[str, int, float]]]):
                Dictionary of parts and associated information
        Returns:
            list: List of plates
        Raises:
            ValueError: If parameters are not feasible.
        """

        def _first_empty_well(
            plates: List[plateo.Plate],
            plate_num: int = None
        ) -> plateo.Well:
            """Finds the first empty well in a list of plates or
            specified plate.
            Args:
                plates (List[plateo.Plate]): List of plates.
            Returns:
                plate.Well: First empty well.
            Raises:
                ValueError: If there are no empty wells in
                    the plates or plate specified.
            """
            selected_well = None
            if plate_num is None:
                # Find first empty well in ordered list of plates
                for plate in plates:
                    for well in plate.iter_wells(direction='row'):
                        if well.data == {}:
                            selected_well = well
                            break
                    if selected_well:
                        break
            else:
                # Find first empty well in plate specified
                plate = plates[plate_num - 1]
                for well in plate.iter_wells(direction='row'):
                    if well.data == {}:
                        selected_well = well
                        break
            if selected_well is None:
                raise ValueError("No empty wells in plates or plate specified")
            return selected_well

        # TODO: Infer numPlate or plate_class?
        # TODO: Input well content vol and qty
        all_content_copy = all_content.copy()
        num_plate = 1 if num_plate is None else num_plate
        plate_class = (
            plateo.containers.Plate96 if plate_class is None else plate_class)
        num_wells = plate_class.num_rows * plate_class.num_columns
        max_construct_wells = (
            num_wells if max_construct_wells is None
            else max_construct_wells)
        # Check if maxwells more than num_wells of plates
        if max_construct_wells > num_wells:
            raise ValueError(
                "ValueError: max_construct_wells must be less than"
                " plate_class.num_wells")
        # Check if numPlate*maxWellsFilled less than len(allContent)
        if num_plate * max_construct_wells < len(all_content):
            raise ValueError(
                "ValueError: Length of all_content must be"
                " less than num_plate*max_construct_wells")
        # Check if there will be empty plates
        if len(all_content) < (num_plate - 1) * max_construct_wells:
            warnings.warn("Number of " + content_name + "s \
                            cannot fill all plates.")
        plates = [
            plate_class(name="Plate %d" % index)
            for index in range(1, num_plate + 1)]
        if part_info is None:
            for plate in plates:
                for i in range(1, max_construct_wells + 1):
                    if all_content_copy:
                        well = plate.wells[
                            plateo.tools.index_to_wellname(i, plate.num_wells)]
                        well.data = {content_name: all_content_copy.pop(0)}
        else:
            for content in all_content_copy:
                # TODO: Test all cases
                name = content.displayId
                listed = \
                    True if name in part_info.keys() else False
                plated = \
                    True if listed and part_info[name]['plate'] else False
                welled = \
                    True if listed and part_info[name]['well'] else False
                if listed and plated and welled:
                    plate_num = part_info[name]['plate']
                    plate = plates[plate_num - 1]
                    well_name = part_info[name]['well']
                    well = plate.wells[well_name]
                    conc = part_info[name]['concentration']
                    well.data = {content_name: content, "concentration": conc}
                elif listed and welled and not plated:
                    selected_plate = None
                    well_name = part_info[name]['well']
                    # Find suitable plate
                    for plate in plates:
                        well = plate.wells[well_name]
                        if well.data == {}:
                            selected_plate = plate
                            break
                    if selected_plate is None:
                        return ValueError(
                            "Specified well is "
                            "not empty in all plates"
                        )
                    else:
                        well = selected_plate.wells[well_name]
                        conc = part_info[name]['concentration']
                        well.data = \
                            {content_name: content, "concentration": conc}
                elif listed and plated and not welled:
                    plate_num = part_info[name]['plate']
                    plate = plates[plate_num - 1]
                    # Find first empty well in plate
                    selected_well = _first_empty_well(plates, plate_num)
                    conc = part_info[name]['concentration']
                    selected_well.data = \
                        {content_name: content, "concentration": conc}
                else:
                    # Find first empty well in ordered list of plates
                    selected_well = _first_empty_well(plates)
                    selected_well.data = \
                        {content_name: content, "concentration": ''}
        return plates

    def get_all_content_from_plate(
        self,
        content_plate: plateo.Plate,
        content_name: str
    ) -> List[ComponentDefinition]:
        """Get a list of all content (as component definitions) from a
        Plateo plate.
        Args:
            content_plate (plateo.Plate): Plateo plate containing content.
            content_name (str): Name of content ("construct" or "part").
        Returns:
            list: List of all content (as component definitions).
        """
        all_content = []
        for well in content_plate.iter_wells():
            if well.data:
                all_content.append(well.data[content_name])
        return all_content

    def get_min_basic_parts(
        self,
        all_constructs: List[ComponentDefinition]
    ) -> int:
        """Get the minimum number of Part/Linker pairs required to perform
        BASIC assembly for all constructs.
        Args:
            all_constructs (list): List of all constructs as component
                definitions.
        Returns:
            int: Number of Part/Linker paris for BASIC assembly.
        """
        min_val = 0
        num_parts = 0
        for cd in all_constructs:
            components = cd.components
            num_parts = len(components) // 2
            if min_val < num_parts:
                min_val = num_parts
        return min_val

    def get_construct_csv_header(
        self,
        min_basic_parts: int
    ) -> List[str]:
        """Create header for Construct CSV for DNABot
        Args:
            min_basic_parts (int): Minimum number of of Part/Linker
                pairs required to perform BASIC assembly for all constructs.
        Returns:
            List[str]: List of strings describing header for Construct CSV.
        """
        header = ["Well"]
        for i in range(1, min_basic_parts + 1):
            header.extend(["Linker %d" % i, "Part %d" % i])
        return header

    def get_comp_dict_from_plate(
        self,
        construct_plate: plateo.Plate,
        assembly: str
    ) -> Dict[str, List[ComponentDefinition]]:
        """Get a dictionary of wells containing components comprising
        the final constructs (as component definitions). Structure of
        dictionary depends on assembly type.
        Args:
            construct_plate (plateo.Plate): Plateo plate containing constructs.
            assembly (str): Type of assembly.
        Returns:
            dict: Dictionary of wells containing components.
        """
        # TODO: Perform checks on all constructs instead of sampled?
        comp_dict = {}
        for wellname, well in construct_plate.wells.items():
            for key, value in well.data.items():
                # Move linker at last position to front of the list
                pri_struct = value.getPrimaryStructure()
                if assembly == "basic":
                    # Check part-linker order
                    if not self.is_linkers_order_correct(value):
                        # Shift linker to front
                        pri_struct.insert(0, pri_struct.pop())
                    comp_dict[wellname] = pri_struct
                elif assembly == "moclo":
                    comp_dict[wellname] = {
                        'construct': value,
                        'parts': pri_struct
                    }
                elif assembly == "bio_bricks":
                    # TODO: Confirm whether construct name is needed
                    # Check if valid biobrick construct
                    if self.validate_bio_bricks_construct(value):
                        # Check if first component is a plasmid vector:
                        plasmid_vector = "http://identifiers.org/so/SO:0000755"
                        if plasmid_vector in pri_struct[0].roles:
                            # Shift backbone to last component
                            pri_struct.insert(2, pri_struct.pop(0))
                        comp_dict[wellname] = {
                            'construct': value,
                            'parts': pri_struct
                        }
        return comp_dict

    def get_list_from_comp_dict(
        self,
        comp_dict: Dict[str, ComponentDefinition],
        assembly: str
    ) -> List[str]:
        """Get a concatenated list of wellname and components (as display ID)
        comprising the final construct from the dictionary of wells containing
        constructs.
        Args:
            comp_dict: Dictionary of wells containing constructs.
            assembly (str): Type of assembly.
        Returns:
            List[str]: List of wellnames and components (as display ID).
        """
        comp_list = []
        for k, v in comp_dict.items():
            if assembly == "bio_bricks":
                comp_list.append([
                    v['construct'].displayId,
                    k,
                    *(x.displayId for x in v['parts'])
                ])
            elif assembly == "basic":
                comp_list.append([k, *(x.displayId for x in v)])
            elif assembly == "moclo":
                comp_list.append([
                    k,
                    v['construct'].displayId,
                    *(x.displayId for x in v['parts'])
                ])
        return comp_list

    def get_construct_df_from_plate(
        self,
        construct_plate: plateo.Plate,
        assembly: str
    ) -> pd.DataFrame:
        """Get dataframe of constructs from Plateo plate containing constructs.
        Args:
            construct_plate (plateo.Plate): Plateo plate containing constructs.
            assembly (str): Type of assembly.
        Returns:
            pd.DataFrame: Dataframe of constructs.
        """
        all_comps = \
            self.get_all_content_from_plate(construct_plate, 'construct')
        comp_dict = \
            self.get_comp_dict_from_plate(construct_plate, assembly)
        comp_list = \
            self.get_list_from_comp_dict(comp_dict, assembly)
        # Create sparse array from list
        sparr = pd.arrays.SparseArray(comp_list)
        if assembly == "basic":
            min_basic_parts = \
                self.get_min_basic_parts(all_comps)
            header = self.get_construct_csv_header(min_basic_parts)
            # Create df from sparr
            df = pd.DataFrame(data=sparr, columns=header)
        elif assembly == "moclo":
            df = pd.DataFrame(data=sparr)
            df = df.iloc[:, 1:]
        elif assembly == "bio_bricks":
            header = ["Construct", "Well", "upstream", "downstream", "plasmid"]
            # Create df from sparr
            df = pd.DataFrame(data=sparr, columns=header)
        return df

    def get_construct_csv_from_plate(
        self,
        construct_plate: plateo.Plate,
        assembly: str
    ):
        """Convert construct dataframe into CSV and creates CSV file in the same
        directory.
        Args:
            construct_plate (plateo.Plate): Plateo plate containing constructs.
            uniqueId (str): Unique ID appended to filename.
            assembly (str): Type of assembly.
        """
        construct_df = \
            self.get_construct_df_from_plate(construct_plate, assembly)
        if assembly == "basic" or assembly == "bio_bricks":
            filepath = os.path.join(self.outdir, "construct.csv")
            construct_df.to_csv(
                filepath,
                index=False,
            )
            self.construct_csv_paths.append(filepath)
        elif assembly == "moclo":
            filepath = os.path.join(self.outdir, "construct.csv")
            construct_df.to_csv(
                filepath,
                index=False,
                header=False
            )
            self.construct_csv_paths.append(filepath)

    def is_linker(
        self,
        part: ComponentDefinition,
    ) -> bool:
        """Check whether a part is a linker.
        Args:
            part (ComponentDefinition): Part to check.
        Returns:
            bool: True if part is a linker. False otherwise.
        """
        linkers = self.get_root_compdefs(self.linker_file)
        if part.identity in [linker.identity for linker in linkers]:
            return True
        else:
            return False

    def get_linker_sp(
        self,
        linker: ComponentDefinition,
    ) -> List[ComponentDefinition]:
        """Get linker prefixes and suffixes.
        Args:
            linker (ComponentDefinition): Linker to get prefix and suffix.
        Returns:
            List[ComponentDefinition]: Linker prefix and suffix (as
                component definitions).
        """
        linkersp = []
        for component in linker.components:
            linkersp.append(
                self.doc.getComponentDefinition(component.definition))
        return linkersp

    def convert_linker_to_sp(
        self,
        part_list: List[ComponentDefinition],
    ) -> List[ComponentDefinition]:
        """Convert all linkers contained in a list of parts into linker
        prefixes and suffixes.
        Args:
            listOfParts (List[ComponentDefinition]): List of parts
                used in the assembly of all constructs.
        Returns:
            List[ComponentDefinition]: List of parts with linkers
                converted into linker prefixes and suffixes.
        """
        new_part_list = []
        for part in part_list:
            if self.is_linker(part):
                new_part_list.extend(self.get_linker_sp(part))
            else:
                new_part_list.append(part)
        return new_part_list

    def get_content_dict_from_plate(
        self,
        plate: plateo.Plate,
        content_name: str
    ) -> Dict[str, Tuple[ComponentDefinition, float]]:
        """Get the contents of a well based on well data.
        Args:
            plate (plate.Plate): Plate to get well
                content from.
            content_name (str): Type of content in well ("construct"
                or "part).
        Returns:
            Dict[str, Tuple[ComponentDefinition, float]]: Dictionary
                of well content with wellname as keys, and component
                definition of the part or construct and concentration
                as values.
        """
        # TODO: Add option to include content vol/qty?
        content_dict = {}
        for wellname, well in plate.wells.items():
            if content_name in well.data.keys():
                cd = well.data[content_name]
                if "concentration" in well.data.keys():
                    conc = well.data['concentration']
                    if conc == 0:
                        conc = np.nan
                else:
                    conc = np.nan
                content_dict[wellname] = (cd, conc)
        return content_dict

    def get_list_from_part_dict(
        self,
        part_dict: Dict[str, Tuple[ComponentDefinition, float]]
    ) -> List[str]:
        """Convert a dictionary of well contents into a list.
        Args:
            part_dict (Dict[str, Tuple[ComponentDefinition, float]]):
                Dictionary of well contents in a plate.
        Returns:
            List[str]: Formatted list of well contents.
        """
        part_list = []
        for k, v in part_dict.items():
            cd = v[0]
            conc = v[1]
            part_list.append([cd.displayId, k, conc])
        return part_list

    def get_part_linker_df_from_plate(
        self,
        part_plate: plateo.Plate
    ) -> pd.DataFrame:
        """Get part/linker dataframe from a plate.
        Args:
            part_plate (plateo.Plate): Plate containing parts used for the
                assembly of constructs.
        Returns:
            pd.DataFrame: Dataframe of part/linkers and their associated
                wellname and concentration.
        """
        header = ["Part/linker", "Well", "Part concentration (ng/uL)"]
        content_dict = self.get_content_dict_from_plate(
            part_plate,
            "part"
        )
        part_list = self.get_list_from_part_dict(content_dict)
        sparr = pd.arrays.SparseArray(part_list)
        df = pd.DataFrame(data=sparr, columns=header)
        return df

    def get_part_linker_csv_from_plate(
        self,
        construct_plate: plateo.Plate,
        assembly: str,
        part_info: Dict[str, Dict[str, Union[str, int, float]]] = None
    ):
        """Get part/linker CSV from plate.
        Args:
            construct_plate (plateo.Plate): Construct plates from which
                parts and linkers are derived.
            assembly (str): Type of assembly.
            part_info (Dict[str, Dict[str, Union[str, int, float]]]):
                Dictionary of parts and associated information.
        """
        def get_part_name(well: plateo.Well) -> str:
            if "part" in well.data.keys():
                cd = well.data["part"]
                name = cd.displayId
            else:
                name = ""
            return name

        # TODO: Determine plate class?
        # Obtain all constructs from plate
        all_constructs = \
            self.get_all_content_from_plate(construct_plate, 'construct')
        # Obtain parts and linkers from all constructs
        part_list = self.get_parts(all_constructs)
        # Change linker to linker-s and linker-p
        part_list = self.convert_linker_to_sp(part_list)
        # Sort list of parts and linkers
        self.get_sorted_parts(part_list)
        # Determine number of plates if dict is None
        if part_info is None:
            num_plates = len(part_list) // 96 + (len(part_list) % 96 > 0)
        else:
            # Determine number of plates from dict of parts
            plates = [info["plate"] for part, info in part_info.items()]
            plates = list(dict.fromkeys(plates))
            num_plates = len(plates)
        # Add parts and linkers to plate
        part_plates = self.fill_plates(
            part_list,
            "part",
            num_plates,
            plateo.containers.Plate96,
            96,
            part_info
        )
        for plate in part_plates:
            if assembly == "basic":
                # Create df
                part_linker_df = self.get_part_linker_df_from_plate(plate)
                filepath = \
                    os.path.join(
                        self.outdir,
                        "part_linker_" + str(part_plates.index(plate) + 1) + ".csv"
                    )
                part_linker_df.to_csv(
                    filepath,
                    index=False
                )
                self.part_csv_paths.append(filepath)
            elif assembly == "moclo":
                filepath = \
                    os.path.join(
                        self.outdir,
                        "parts_" + str(part_plates.index(plate) + 1) + ".csv"
                    )
                # Generate platemap
                plate_to_platemap_spreadsheet(
                    plate,
                    get_part_name,
                    filepath,
                    headers=False
                )
                self.part_csv_paths.append(filepath)
            elif assembly == "bio_bricks":
                # Create df
                part_linker_df = self.get_part_linker_df_from_plate(plate)
                filepath = \
                    os.path.join(
                        self.outdir,
                        "parts_" + str(part_plates.index(plate) + 1) + ".csv"
                    )
                part_linker_df.to_csv(
                    filepath,
                    index=False
                )
                self.part_csv_paths.append(filepath)

    def is_linkers_order_correct(
        self,
        construct: ComponentDefinition,
    ) -> bool:
        """Check input construct components has the
        order of -linker-part-linker...
        Args:
            construct (ComponentDefinition): Constructs to check.
        Returns:
            bool: True if linker order is correct.
        Raises:
            ValueError: If construct does not contain sufficient parts
                and linkers or order does not alternate
        """

        def _get_linker_names():
            """Open standard linker document and extract all displayIds
            of linkers.
            """
            # Get list of linkers from linkerfile
            linkers = self.get_root_compdefs(self.linker_file)
            linkers = [linker.displayId for linker in linkers]
            return linkers

        def _is_linker(
            comp: ComponentDefinition,
            linkers: List[str]
        ):
            """Compare each part displayId to available linkers.
            Args:
                comp (ComponentDefinition): Component definition to check
                linkers List[str]: List of linker display IDs
            """
            if comp.displayId in linkers:
                return True
            return False

        linkers = _get_linker_names()

        # Check if even number of parts
        if np.mod(len(construct.components), 2) != 0:
            raise ValueError(
                "Construct contains insufficient number"
                "of parts or linkers"
            )

        pri_struct = construct.getPrimaryStructure()

        is_first_comp_linker = False
        is_prev_comp_linker = False
        for i, comp in enumerate(pri_struct):
            is_curr_comp_linker = _is_linker(comp, linkers)
            # initialise
            if i == 0:
                is_first_comp_linker = is_curr_comp_linker
                is_prev_comp_linker = is_curr_comp_linker
                continue
            if is_prev_comp_linker == is_curr_comp_linker:
                raise ValueError("Order of components is not alternating")
            is_prev_comp_linker = is_curr_comp_linker
        if is_first_comp_linker:
            return True
        else:
            return False

    def validate_bio_bricks_construct(
        self,
        construct: ComponentDefinition
    ) -> bool:
        """Check that biobricks construct has the structure
        plasmid-prefix-suffix.
        Args:
            construct (ComponentDefinition): Construct to check.
        Returns:
            bool: True if construct structure is correct.
        Raises:
            ValueError: If number of components is not 3,
                construct does not contain plasmid vector, or
                backbone is between parts.
        """
        pri_struct = construct.getPrimaryStructure()
        # Check that there are only 3 parts in the construct
        if len(pri_struct) != 3:
            raise ValueError(
                "There can only be 3 components in each construct"
            )
        # Check that construct contains a backbone
        contains_plasmid = False
        plasmid_vector = "http://identifiers.org/so/SO:0000755"
        for cd in pri_struct:
            if plasmid_vector in cd.roles:
                contains_plasmid = True
        if not contains_plasmid:
            raise ValueError(
                "Construct must contain plasmid vector"
            )
        # Check that backbone is not between parts
        mid_comp = pri_struct[1]
        if plasmid_vector in mid_comp.roles:
            raise ValueError(
                "Backbone should not be between parts"
            )
        return True
