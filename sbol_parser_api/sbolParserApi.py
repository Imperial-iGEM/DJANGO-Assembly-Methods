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
        sbolDocument: Document,
        outdir: str = os.getcwd(),
        linkerFile: Document = Document(os.path.join(os.getcwd(), "sbol_parser_api/basic_linkers_standard.xml"))
    ):
        self.doc = sbolDocument
        self.outdir = outdir
        if linkerFile is None:
            filepath = os.path.join(os.getcwd(), "sbol_parser_api/basic_linkers_standard.xml")
            self.linkerFile = Document(filepath)
        else:
            self.linkerFile = linkerFile
        self.construct_csv_paths = []
        self.part_csv_paths = []
        self.assembly_types = ["basic", "moclo", "bio_bricks"]

    def generate_csv(
            self,
            assembly: str,
            dictOfParts: Dict[str, Dict[str, Union[str, int, float]]] = None,
            repeat: bool = False,
            maxWellsFilled: int = 96,
            numRuns: int = 1
    ) -> Dict[str, List[str]]:
        """Create construct and parts/linkers CSVs for DNABot input
        Args:
            assembly(str): Assembly type.
            dictOfParts (Dict[str, Dict[str, Union[str, int, float]]]): 
                Dictionary of information regarding parts to be assembled.
                Structure:
                {<display ID>: {'concentration':..., 'plate':..., 'well':...}}
            repeat (bool): If False, removes constructs that contain repeated
                components. (default: False)
            maxWellsFilled (int): Number of wells to be filled in the
                constructs plate. (default: 96)
            numRuns (int): Number of runs (i.e. construct plates) to be
                created. (default: 1)
        Returns:
            Dict[str,List[str]]: Dictionary containing lists of paths to csvs
                generated.
        """
        if assembly not in self.assembly_types:
            raise ValueError("Invalid assembly type: %s" % assembly)
        numSamples = maxWellsFilled * numRuns
        allConstructs = []
        print("Assembly Method: %s" % assembly)
        # Get list of constructs
        allConstructs = self.getListOfConstructs()
        # Remove constructs with repeated parts using a filter
        if not repeat:
            allConstructs = self.filterConstructs(allConstructs)
        # Sample constructs
        if len(allConstructs) < numSamples:
            numSamples = len(allConstructs)
            print(
                "Number of constructs specified is greater than number "
                "of constructs contained within SBOL Document provided."
            )
            print("All constructs will be assembled.")
        sampled = sample(allConstructs, numSamples)
        # Display number of Component Definitions to be constructed
        numberOfDesigns = len(sampled)
        print(numberOfDesigns, "construct(s) will be assembled.")
        # Create plateo construct plates
        constructPlates = self.fillPlateoPlates(
            sampled,
            "Construct",
            numRuns,
            plateo.containers.Plate96,
            maxWellsFilled
        )
        for plate in constructPlates:
            # Create construct CSV
            self.getConstructCsvFromPlateoPlate(plate, assembly)
            # Write parts/linkers csv
            self.getPartLinkerCsvFromPlateoPlate(
                plate,
                assembly,
                dictOfParts
            )
        filepaths = {}
        filepaths['construct_path'] = self.construct_csv_paths
        filepaths['part_path'] = self.part_csv_paths
        return filepaths

    def getRootComponentDefinitions(
            self,
            sbolDocument: Document = None
    ) -> List[ComponentDefinition]:
        """Get the root component definitions of an SBOL document.
        Args:
            sbolDocument (Document): SBOL document from
                which to get root component definitions (default: self.doc)
        Returns:
            list: List of root component definitions.
        """
        document = self.doc if sbolDocument is None else sbolDocument
        componentDefs = list(document.componentDefinitions)
        # Remove child components of component definitions
        for obj in document.componentDefinitions:
            for component in obj.components:
                childDefinition = \
                    document.getComponentDefinition(component.definition)
                if(childDefinition
                        is not None and childDefinition in componentDefs):
                    componentDefs.remove(childDefinition)
        # Remove child components of combinatorial derivations
        for obj in document.combinatorialderivations:
            for variableComponent in obj.variableComponents:
                for variant in variableComponent.variants:
                    childDefinition = document.getComponentDefinition(variant)
                    if(childDefinition
                            is not None and childDefinition in componentDefs):
                        componentDefs.remove(childDefinition)
        # Remove Templates
        for obj in document.combinatorialderivations:
            template = document.getComponentDefinition(obj.masterTemplate)
            if (template
                    is not None and template in componentDefs):
                componentDefs.remove(template)
        return list(componentDefs)

    def getRootCombinatorialDerivations(
        self,
        sbolDocument: Document = None
    ) -> List[CombinatorialDerivation]:
        """Get the root combinatorial derivations of an SBOL Document.
        Args:
            sbolDocument (Document): SBOL document from
                which to get root combinatorial derivations (default: self.doc)
        Returns:
            list: List of root combinatorial derivations.
        """
        document = self.doc if sbolDocument is None else sbolDocument
        combDerivs = list(document.combinatorialderivations)
        for obj in document.combinatorialderivations:
            for vc in obj.variableComponents:
                if vc.variantDerivations is not None:
                    for vd in vc.variantDerivations:
                        childDeriv = document.combinatorialderivations.get(vd)
                        if (childDeriv
                                is not None and childDeriv in combDerivs):
                            combDerivs.remove(childDeriv)
        return combDerivs

    def getListOfConstructs(
            self,
            listOfNonCombUris: List[str] = [],
            listOfCombUris: List[str] = []
    ) -> List[ComponentDefinition]:
        """Get the list of constructs (component definitions) specified by
        the list of non-combinatorial URIs and combinatorial derivation URIs.
        Expands combinatorial derivations.
        Args:
            listOfNonCombUris (list): List of component definition
                URIs pointing to non-combinatorial designs.
            listOfCombUris (list): List of combinatorial derivation
                URIs pointing to combinatorial designs.
        Returns:
            list: List of component definitions specifying constructs
                to be assembled
        """
        listOfConstructs = []
        print("Obtaining constructs from SBOL Document...")
        # Add non-combinatorial constructs to list
        if listOfNonCombUris == []:
            # Get all root component definitions and append to list
            listOfConstructs.extend(self.getRootComponentDefinitions())
        else:
            for uri in listOfNonCombUris:
                listOfConstructs.append(self.doc.getComponentDefinition(uri))
        # Add combinatorial constructs to list
        print("Enumerating Combinatorial Derivations...")
        if listOfCombUris == []:
            # Get all root combinatorial derivations
            combDerivs = self.getRootCombinatorialDerivations()
            # Enumerate all root combinatorial derivations and append to list
            for combDeriv in combDerivs:
                listOfConstructs.extend(self.enumerator(combDeriv))
        else:
            for uri in listOfCombUris:
                # Enumerate Combinatorial Derivations and add to allConstructs
                listOfConstructs.extend(self.enumerator(
                    self.doc.combinatorialderivations.get(uri)))
        print("Completed.")
        return listOfConstructs

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
        templateCopy =\
            self.createTemplateCopy(template, template.displayId + "_Var", "1")
        parents.append(templateCopy)
        for vc in derivation.variableComponents:
            newParents = []
            for parent in parents:
                for children in self.group(
                        self.collectVariants(vc),
                        "http://sbols.org/v2#one"):
                    varDisplayId = self.concatenateChildrenDisplayId(children)
                    if parent.persistentIdentity + "_" + varDisplayId + "/1" \
                            not in [cd.identity for cd in self.doc.componentDefinitions]:
                        # Create parent copy
                        uniqueId = self.getUniqueDisplayId(
                            None,
                            None,
                            parent.displayId + "_" + varDisplayId,
                            parent.version,
                            "CD",
                            self.doc
                        )
                        newParent = self.createTemplateCopy(
                            parent,
                            uniqueId,
                            "1"
                        )
                        self.doc.add(newParent)
                    else:
                        # Set newParent to existing CD
                        newParent = self.doc.getComponentDefinition(
                            parent.persistentIdentity + "_" + varDisplayId + "/1"
                        )
                    # Add children
                    self.addChildren(
                        template,
                        template.components[vc.variable],
                        newParent,
                        children
                    )
                    # Add to newParents
                    newParents.append(newParent)
            parents = newParents
        return parents

    def addChildren(
        self,
        originalTemplate: ComponentDefinition,
        originalComponent: Component,
        newParent: ComponentDefinition,
        children: List[ComponentDefinition]
    ):
        """Adds children to new parent component definition based on the
        original template.
        Args:
            originalTemplate (ComponentDefinition): Original template
                describing the design of the new parent
            originalComponent (Component): Variable component in the
                original template to be replaced in new parent
            newParent (ComponentDefinition): New component definition
                describing an enumerated design
            children (List[ComponentDefinition]): Children to be added
                to the new parent based on the variants
        """
        newComponent = newParent.components[originalComponent.displayId]
        newComponent.wasDerivedFrom = originalComponent.identity
        if children is None:
            self.removeConstraintReferences(newParent, newComponent)
            for sa in newParent.sequenceAnnotations:
                if sa.component \
                        is not None and sa.component == newComponent.identity:
                    newParent.sequenceAnnotations.remove(sa.identity)
            newParent.components.remove(newComponent.identity)
            return
        first = True
        for child in children:
            if first:
                # Take over definition of
                # newParent's version of original component
                newComponent.definition = child.identity
                first = False
            else:
                # Create new component
                uniqueId = self.getUniqueDisplayId(
                    newParent,
                    None,
                    child.displayId + "_Component", "1",
                    "Component",
                    None)
                link = newParent.components.create(uniqueId)
                link.definition = child.persistentIdentity
                link.access = SBOL_ACCESS_PUBLIC
                link.version = child.version
                link.wasDerivedFrom = originalComponent.identity
                # Create a new 'prev precedes link' constraint
                if originalTemplate.hasUpstreamComponent(originalComponent):
                    oldPrev = \
                        originalTemplate.getUpstreamComponent(originalComponent)
                    if oldPrev.identity in newParent.components:
                        newPrev = newParent.components[oldPrev.identity]
                        uniqueId = self.getUniqueDisplayId(
                            newParent,
                            None,
                            newParent.displayId + "_SequenceConstraint",
                            None,
                            "SequenceConstraint",
                            None
                        )
                        newSequenceConstraint = \
                            newParent.sequenceConstraints.create(uniqueId)
                        newSequenceConstraint.subject = newPrev.identity
                        newSequenceConstraint.object = link.identity
                        newSequenceConstraint.restriction = \
                            SBOL_RESTRICTION_PRECEDES
                # Create new 'link precedes next' constraint
                if originalTemplate.hasDownstreamComponent(originalComponent):
                    oldNext = \
                        originalTemplate.getDownstreamComponent(originalComponent)
                    if oldNext.identity in newParent.components:
                        newNext = newParent.components[oldNext.identity]
                        uniqueId = self.getUniqueDisplayId(
                            newParent,
                            None,
                            newParent.displayId + "_SeqeunceConstraint",
                            None,
                            "SequenceConstraint",
                            None
                        )
                        newSequenceConstraint = \
                            newParent.sequenceConstraints.create(uniqueId)
                        newSequenceConstraint.subject = link.identity
                        newSequenceConstraint.object = newNext.identity
                        newSequenceConstraint.restriction = \
                            SBOL_RESTRICTION_PRECEDES

    def removeConstraintReferences(
        self,
        newParent: ComponentDefinition,
        newComponent: Component
    ):
        """Remove sequence constraints of the component in the component definition
        Args:
            newParent (ComponentDefinition): Component definition containing
                the new component.
            newComponent (Component): Component to remove sequence
                constraints from.
        """
        subj = None
        obj = None
        for sc in newParent.sequenceConstraints:
            if sc.subject == newComponent.identity:
                obj = newParent.components[sc.object]
                if subj is not None:
                    sc.subject = subj
                    obj = None
                    subj = None
                else:
                    newParent.sequenceConstraints.remove(sc.identity)
            if sc.object == newComponent.identity:
                subj = newParent.components[sc.subject]
                if obj is not None:
                    sc.object = obj
                    obj = None
                    subj = None
                else:
                    newParent.sequenceConstraints.remove(sc.identity)

    def createTemplateCopy(
        self,
        template: ComponentDefinition,
        displayId: str,
        version: str
    ) -> ComponentDefinition:
        """Create a copy of the template of the combinatorial derivation.
        Args:
            template (ComponentDefinition): Template of the
                combinatorial derivation.
            displayId (str): Display ID to be assigned to the copy.
            version (str): Version of the copy.
        Returns:
            ComponentDefinition: Copy of template.
        """
        newDisplayId = URIRef(displayId)
        templateCopy = ComponentDefinition(
            newDisplayId,
            template.types,
            version
        )
        templateCopy.roles = template.roles
        primaryStructure = template.getPrimaryStructureComponents()
        curr = None
        prev = None
        for c in primaryStructure:
            curr = templateCopy.components.create(c.displayId)
            curr.access = c.access
            curr.definition = c.definition
            if prev is not None:
                uniqueId = self.getUniqueDisplayId(
                    templateCopy,
                    None,
                    templateCopy.displayId + "_SequenceConstraint",
                    None,
                    "SequenceConstraint",
                    None
                )
                sc = templateCopy.sequenceConstraints.create(uniqueId)
                sc.subject = prev.identity
                sc.object = curr.identity
                sc.restriction = SBOL_RESTRICTION_PRECEDES
            prev = curr
        templateCopy.wasDerivedFrom = [template.identity]
        for c in templateCopy.components:
            component = template.components[c.displayId]
            c.wasDerivedFrom = component.identity
        return templateCopy

    def getUniqueDisplayId(
        self,
        comp: ComponentDefinition = None,
        derivation: CombinatorialDerivation = None,
        displayId: str = None,
        version: str = None,
        dataType: str = None,
        doc: Document = None
    ) -> str:
        """Creates a unique display ID for an SBOL object.
        Args:
            comp (ComponentDefinition): Component definition containing
                the SBOL object
            derivation (CombinatorialDerivation): Combinatorial derivation
                containing the SBOL object
            displayId (str): Base display ID for SBOL object.
            version (str): Version of SBOL object.
            dataType (str): Type of SBOL object.
            doc (str): SBOL Document containing the SBOL object.
        Returns:
            str: Unique display ID of SBOL object.
        """
        i = 1
        if dataType == "CD":
            uniqueUri = getHomespace() + displayId + "/" + version
            # while doc.find(uniqueUri):
            while uniqueUri \
                    in [cd.displayId for cd in doc.componentDefinitions]:
                i += 1
                uniqueUri = \
                    getHomespace() + "%s_%d/%s" % (displayId, i, version)
            if i == 1:
                return displayId
            else:
                return displayId + "_" + str(i)
        elif dataType == "SequenceAnnotation":
            while displayId \
                    in [sa.displayId for sa in comp.sequenceAnnotations]:
                i += 1
                displayId = displayId + str(i)
            if i == 1:
                return displayId
            else:
                return displayId
        elif dataType == "SequenceConstraint":
            while displayId \
                    in [sc.displayId for sc in comp.sequenceConstraints]:
                i += 1
                displayId = displayId + str(i)
            if i == 1:
                return displayId
            else:
                return displayId
        elif dataType == "Component":
            while displayId in [c.displayId for c in comp.components]:
                i += 1
                displayId = displayId + str(i)
            if i == 1:
                return displayId
            else:
                return displayId
        elif dataType == "Sequence":
            uniqueUri = getHomespace() + displayId + "/" + version
            while doc.find(uniqueUri):
                i += 1
                uniqueUri = \
                    getHomespace() + "%s_%d/%s" % (displayId, i, version)
            if i == 1:
                return displayId
            else:
                return displayId + str(i)
        # TODO: Range
        elif dataType == "CombinatorialDerivation":
            uniqueUri = getHomespace() + displayId + "/" + version
            while doc.find(uniqueUri):
                i += 1
                uniqueUri = \
                    getHomespace() + "%s_%d/%s" % (displayId, i, version)
            if i == 1:
                return displayId
            else:
                return displayId + str(i)
        elif dataType == "VariableComponent":
            while displayId + str(i) \
                    in [vc.displayId for vc in derivation.variableComponents]:
                i += 1
                displayId = displayId + str(i)
            if i == 1:
                return displayId
            else:
                return displayId
        else:
            raise ValueError("")

    def concatenateChildrenDisplayId(
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
        concDisplayId = ""
        for child in children:
            concDisplayId = concDisplayId + child.displayId
        return concDisplayId

    def collectVariants(
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
        self.generateCombinations(groups, variants, 0, [])
        if repeat == "http://sbols.org/v2#oneOrMore":
            return groups
        if repeat == "http://sbols.org/v2#zeroOrMore":
            groups.append([])
            return groups

    def generateCombinations(
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
        self.generateCombinations(groups, variants, i + 1, no)
        yes = sets.copy()
        yes.add(variants[i])
        self.generateCombinations(groups, variants, i + 1, yes)

    def filterConstructs(
        self,
        allConstructs: List[ComponentDefinition]
    ) -> List[ComponentDefinition]:
        """Removes constructs with repeated components.
        Args:
            allConstructs (List[ComponentDefinition]): List of constructs
                to filter.
        Returns:
            List[ComponentDefinition]: List of filtered constructs.
        """
        # TODO: Filter constructs based on more user specifications
        filtered = []
        print("Removing designs with repeated parts...")
        for construct in allConstructs:
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
        allComponents = []
        while(d):
            comp = d.popleft()
            if(comp.components):
                d.extendleft(reversed(comp.getPrimaryStructure()))
            else:
                allComponents.append(comp)
        return allComponents

    def displayListOfParts(
        self,
    ) -> List[str]:
        # TODO: Test if robust to multiple nested variant derivations
        """Displays list of parts used in the assembly of the constructs
        in the SBOL document used to initialize the parser.
        Returns:
            List[str]: List of display IDs of parts.
        """

        def getExtendedDisplayId(
            combDeriv: CombinatorialDerivation
        ) -> List[str]:
            """Get the display ID extensions of an enumerated combinatorial derivation.
            Args:
                combDeriv: Combinatorial derivation to be enumerated.
            Returns:
                List[str]: List of display ID extensions.
            """
            extDisplayIds = []
            for vc in combDeriv.variableComponents:
                for v in vc.variants:
                    cd = self.doc.getComponentDefinition(v)
                    extDisplayIds.append("_Var_" + cd.displayId)
                for c in vc.variantCollections:
                    for m in c.members:
                        tl = self.doc.get(m)
                        if type(tl) == ComponentDefinition:
                            extDisplayIds.append("_Var_" + tl.displayId)
                for vd in vc.variantDerivations:
                    cDeriv = self.doc.get(vd)
                    template = cDeriv.masterTemplate
                    extDisplayIds.extend(
                        [template.displayId + edi
                            for edi in getExtendedDisplayId(cDeriv)]
                    )
            return extDisplayIds

        listOfParts = []
        rootCds = []
        # Get all root component definitions from document
        rootCds.extend(self.getRootComponentDefinitions())
        # Add all parts in each root cds
        for cd in rootCds:
            for c in cd.components:
                compdef = self.doc.getComponentDefinition(c.definition)
                listOfParts.append(compdef.displayId)
        # Get all root combinatorial derivations
        rootCombDerivs = self.getRootCombinatorialDerivations()
        for rootCombDeriv in rootCombDerivs:
            # Get master template
            template = \
                self.doc.getComponentDefinition(rootCombDeriv.masterTemplate)
            variables = \
                [vc.variable for vc in rootCombDeriv.variableComponents]
            # Add components of template that are not variables
            for c in template.components:
                if c.identity not in variables:
                    cd = self.doc.getComponentDefinition(c.definition)
                    listOfParts.append(cd.displayId)
            # Append variants
            for vc in rootCombDeriv.variableComponents:
                for v in vc.variants:
                    cd = self.doc.getComponentDefinition(v)
                    listOfParts.append(cd.displayId)
                for c in vc.variantCollections:
                    for m in c.members:
                        tl = self.doc.get(m)
                        if type(tl) == ComponentDefinition:
                            listOfParts.append(tl.displayId)
                for vd in vc.variantDerivations:
                    deriv = self.doc.get(vd)
                    template = \
                        self.doc.getComponentDefinition(deriv.masterTemplate)
                    listOfParts.extend(
                        [template.displayId + edi
                            for edi in getExtendedDisplayId(deriv)]
                    )
        listOfParts = list(dict.fromkeys(listOfParts))
        # Get list of linkers from linkerfile
        linkers = self.getRootComponentDefinitions(self.linkerFile)
        # Convert linkers into linker suffix and prefix and add to new list
        newListOfParts = []
        for part in listOfParts:
            if part in [linker.displayId for linker in linkers]:
                newListOfParts.append(part + "_Suffix")
                newListOfParts.append(part + "_Prefix")
            else:
                newListOfParts.append(part)
        return sorted(newListOfParts)

    def getListOfParts(
        self,
        allConstructs: List[ComponentDefinition] = []
    ) -> List[ComponentDefinition]:
        """Get list of parts (component defintions) from the list of
        all constructs.
        Args:
            allConstructs (list): List of all constructs to be assembled.
        Returns:
            list: List of component definitions specifying parts used across
                all constructs to be assembled.
        """
        listOfParts = []
        # Add components from all component definitions in allConstructs
        for construct in allConstructs:
            for component in construct.components:
                listOfParts.append(
                    self.doc.getComponentDefinition(component.definition)
                )
        # Remove duplicate components
        listOfParts = list(dict.fromkeys(listOfParts))
        return listOfParts

    def getSortedListOfParts(
        self,
        listOfParts: List[ComponentDefinition]
    ) -> List[ComponentDefinition]:
        """Get a sorted list of parts (str) from the list of parts.
        Sort by sbol2 displayId
        Args:
            listOfParts (list): List of parts to be sorted. (generated
                by getListOfConstructs)
        Returns:
            list: List of sorted parts (str)
        """
        listOfParts.sort(key=lambda x: x.displayId)
        return listOfParts

    def getDictOfComponents(
        self,
        listOfConstructs: List[ComponentDefinition]
    ) -> Dict[str, ComponentDefinition]:
        """Get a dictionary of components (as component definitions)
        from the list of constructs as
        {construct.displayId: construct.components (as component definitions)}
        Args:
            listOfConstructs (list): List of constructs
        Returns:
            dict: Dictionary of components
        """
        return {x.displayId: x.getPrimaryStructure() for x in listOfConstructs}

    def fillPlateoPlates(
        self,
        allContent: List[ComponentDefinition],
        contentName: str,
        numPlate: int = None,
        plate_class: plateo.Plate = None,
        maxWellsFilled: int = None,
        dictOfParts: Dict[str, Dict[str, Union[str, int, float]]] = None
    ) -> List[plateo.Plate]:
        """Generate a list of plateo plate objects from list of constructs
        Args:
            allContent (list): List of constructs.
            contentName (str): Name of content (Construct or Part).
            numPlate (int): Number of plates to be generated (default = 1).
            plate_class (plateo.Plate):
                Class of plateo plate (default = Plate96).
            maxWellsFilled (int): Maximum number of filled wells on a plate.
            dictOfParts (Dict[str, Dict[str, Union[str, int, float]]]):
                Dictionary of parts and associated information
        Returns:
            list: List of plates
        """

        def firstEmptyWell(
            plates: List[plateo.Plate],
            plateNum: int = None
        ) -> plateo.Well:
            """Finds the first empty well in a list of plates or
            specified plate.
            Args:
                plates (List[plateo.Plate]): List of plates.
            Returns:
                plate.Well: First empty well.
            """
            selectedWell = None
            if plateNum is None:
                # Find first empty well in ordered list of plates
                for plate in plates:
                    for well in plate.iter_wells(direction='row'):
                        if well.data == {}:
                            selectedWell = well
                            break
                    if selectedWell:
                        break
            else:
                # Find first empty well in plate specified
                plate = plates[plateNum - 1]
                for well in plate.iter_wells(direction='row'):
                    if well.data == {}:
                        selectedWell = well
                        break
            if selectedWell is None:
                raise ValueError("No empty wells in plates or plate specified")
            return selectedWell

        # TODO: Infer numPlate or plate_class?
        # TODO: Input well content vol and qty
        copyAllContent = allContent.copy()
        numPlate = 1 if numPlate is None else numPlate
        plate_class = (
            plateo.containers.Plate96 if plate_class is None else plate_class)
        num_wells = plate_class.num_rows * plate_class.num_columns
        maxWellsFilled = (
            num_wells if maxWellsFilled is None
            else maxWellsFilled)
        # Check if maxwells more than num_wells of plates
        if maxWellsFilled > num_wells:
            raise ValueError(
                "ValueError: maxWellsFilled must be less than"
                " plate_class.num_wells")
        # Check if numPlate*maxWellsFilled less than len(allContent)
        if numPlate * maxWellsFilled < len(allContent):
            raise ValueError(
                "ValueError: Length of allContent must be"
                " less than numPlate*maxWellsFilled")
        # Check if there will be empty plates
        if len(allContent) < (numPlate - 1) * maxWellsFilled:
            warnings.warn("Number of " + contentName + "s \
                            cannot fill all plates.")
        plates = [
            plate_class(name="Plate %d" % index)
            for index in range(1, numPlate + 1)]
        if dictOfParts is None:
            for plate in plates:
                for i in range(1, maxWellsFilled + 1):
                    if copyAllContent:
                        well = plate.wells[
                            plateo.tools.index_to_wellname(i, plate.num_wells)]
                        well.data = {contentName: copyAllContent.pop(0)}
        else:
            for content in copyAllContent:
                # TODO: Test all cases
                name = content.displayId
                listed = \
                    True if name in dictOfParts.keys() else False
                plated = \
                    True if listed and dictOfParts[name]['plate'] else False
                welled = \
                    True if listed and dictOfParts[name]['well'] else False
                if listed and plated and welled:
                    plateNum = dictOfParts[name]['plate']
                    plate = plates[plateNum - 1]
                    wellname = dictOfParts[name]['well']
                    well = plate.wells[wellname]
                    conc = dictOfParts[name]['concentration']
                    well.data = {contentName: content, "concentration": conc}
                elif listed and welled and not plated:
                    selectedPlate = None
                    wellname = dictOfParts[name]['well']
                    # Find suitable plate
                    for plate in plates:
                        well = plate.wells[wellname]
                        if well.data == {}:
                            selectedPlate = plate
                            break
                    if selectedPlate is None:
                        return ValueError(
                            "Specified well is "
                            "not empty in all plates"
                        )
                    else:
                        well = selectedPlate.wells[wellname]
                        conc = dictOfParts[name]['concentration']
                        well.data = \
                            {contentName: content, "concentration": conc}
                elif listed and plated and not welled:
                    plateNum = dictOfParts[name]['plate']
                    plate = plates[plateNum - 1]
                    # Find first empty well in plate
                    selectedWell = firstEmptyWell(plates, plateNum)
                    conc = dictOfParts[name]['concentration']
                    selectedWell.data = \
                        {contentName: content, "concentration": conc}
                else:
                    # Find first empty well in ordered list of plates
                    selectedWell = firstEmptyWell(plates)
                    selectedWell.data = \
                        {contentName: content, "concentration": ''}
        return plates

    def getAllContentFromPlateoPlate(
        self,
        contentPlate: plateo.Plate,
        contentName: str
    ) -> List[ComponentDefinition]:
        """Get a list of all content (as component definitions) from a
        Plateo plate.
        Args:
            contentPlate (plateo.Plate): Plateo plate containing content.
            contentName (str): Name of content (Construct or Part).
        Returns:
            list: List of all content (as component definitions).
        """
        allContent = []
        for well in contentPlate.iter_wells():
            if well.data:
                allContent.append(well.data[contentName])
        return allContent

    def getMinNumberOfBasicParts(
        self,
        allConstructs: List[ComponentDefinition]
    ) -> int:
        """Get the minimum number of Part/Linker pairs required to perform
        BASIC assembly for all constructs.
        Args:
            allConstructs (list): List of all constructs as component
                definitions.
        Returns:
            int: Number of Part/Linker paris for BASIC assembly.
        """
        minValue = 0
        numParts = 0
        for cd in allConstructs:
            components = cd.components
            numParts = len(components) // 2
            if minValue < numParts:
                minValue = numParts
        return minValue

    def getConstructCsvHeader(
        self,
        minNumberOfBasicParts: int
    ) -> List[str]:
        """Create header for Construct CSV for DNABot
        Args:
            minNumberOfBasicParts (int): Minimum number of of Part/Linker
                pairs required to perform BASIC assembly for all constructs.
        Returns:
            List[str]: List of strings describing header for Construct CSV.
        """
        header = ["Well"]
        for i in range(1, minNumberOfBasicParts + 1):
            header.extend(["Linker %d" % i, "Part %d" % i])
        return header

    def getWellComponentDictFromPlateoPlate(
        self,
        constructPlate: plateo.Plate,
        assembly: str
    ) -> Dict[str, List[ComponentDefinition]]:
        """Get a dictionary of wells containing components comprising
        constructs (as component definitions) in the form
        {Wellname:[Components]}
        Args:
            constructPlate (plateo.Plate): Plateo plate containing constructs.
            assembly (str): Type of assembly.
        Returns:
            dict: Dictionary of wells containing components.
        """
        # TODO: Perform checks on all constructs instead of sampled?
        dictWellComponent = {}
        for wellname, well in constructPlate.wells.items():
            for key, value in well.data.items():
                # Move linker at last position to front of the list
                primaryStructure = value.getPrimaryStructure()
                if assembly == "basic":
                    # Check part-linker order
                    if not self.is_linkers_order_correct(value):
                        # Shift linker to front
                        primaryStructure.insert(0, primaryStructure.pop())
                    dictWellComponent[wellname] = primaryStructure
                elif assembly == "moclo":
                    dictWellComponent[wellname] = primaryStructure
                elif assembly == "bio_bricks":
                    # TODO: Confirm whether construct name is needed
                    # Check if valid biobrick construct
                    if self.validateBioBricksConstruct(value):
                        # Check if first component is a plasmid vector:
                        plasmidVector = "http://identifiers.org/so/SO:0000755"
                        if plasmidVector in primaryStructure[0].roles:
                            # Shift backbone to last component
                            primaryStructure.insert(2, primaryStructure.pop(0))
                        dictWellComponent[wellname] = {
                            'Construct': value,
                            'Parts': primaryStructure
                        }
        return dictWellComponent

    def getListFromWellComponentDict(
        self,
        dictWellComponent: Dict[str, ComponentDefinition],
        assembly: str
    ) -> List[str]:
        """Get a concatenated list of wellname and components (as display ID)
        comprising the construct from the dictionary of wells containing
        constructs.
        Args:
            dictWellComponent: Dictionary of wells containing constructs.
            assembly (str): Type of assembly.
        Returns:
            List[str]: List of wellnames and components (as display ID).
        """
        listWellComponent = []
        for k, v in dictWellComponent.items():
            if assembly == "bio_bricks":
                listWellComponent.append([
                    v['Construct'].displayId,
                    k,
                    *(x.displayId for x in v['Parts'])
                ])
            else:
                listWellComponent.append([k, *(x.displayId for x in v)])
        return listWellComponent

    def getConstructDfFromPlateoPlate(
        self,
        constructPlate: plateo.Plate,
        assembly: str
    ) -> pd.DataFrame:
        """Get dataframe of constructs from Plateo plate containing constructs.
        Args:
            constructPlate (plateo.Plate): Plateo plate containing constructs.
            assembly (str): Type of assembly.
        Returns:
            pd.DataFrame: Dataframe of constructs.
        """
        allComponents = \
            self.getAllContentFromPlateoPlate(constructPlate, 'Construct')
        dictWellComponent = \
            self.getWellComponentDictFromPlateoPlate(constructPlate, assembly)
        listWellComponent = \
            self.getListFromWellComponentDict(dictWellComponent, assembly)
        # Create sparse array from list
        sparr = pd.arrays.SparseArray(listWellComponent)
        if assembly == "basic":
            minNumberOfBasicParts = \
                self.getMinNumberOfBasicParts(allComponents)
            header = self.getConstructCsvHeader(minNumberOfBasicParts)
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

    def getConstructCsvFromPlateoPlate(
        self,
        constructPlate: plateo.Plate,
        assembly: str
    ):
        """Convert construct dataframe into CSV and creates CSV file in the same
        directory.
        Args:
            constructPlate (plateo.Plate): Plateo plate containing constructs.
            uniqueId (str): Unique ID appended to filename.
            assembly (str): Type of assembly.
        """
        constructDf = \
            self.getConstructDfFromPlateoPlate(constructPlate, assembly)
        if assembly == "basic" or assembly == "bio_bricks":
            filepath = os.path.join(self.outdir, "construct.csv")
            constructDf.to_csv(
                filepath,
                index=False,
            )
            self.construct_csv_paths.append(filepath)
        elif assembly == "moclo":
            filepath = os.path.join(self.outdir, "construct.csv")
            constructDf.to_csv(
                filepath,
                index=False,
                header=False
            )
            self.construct_csv_paths.append(filepath)

    def isLinker(
        self,
        part: ComponentDefinition,
    ) -> bool:
        """Check whether a part is a linker.
        Args:
            part (ComponentDefinition): Part to check.
        Returns:
            bool: True if part is a linker. False otherwise.
        """
        linkers = self.getRootComponentDefinitions(self.linkerFile)
        if part.identity in [linker.identity for linker in linkers]:
            return True
        else:
            return False

    def getLinkerSP(
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

    def convertLinkerToSuffixPrefix(
        self,
        listOfParts: List[ComponentDefinition],
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
        newListOfParts = []
        for part in listOfParts:
            if self.isLinker(part):
                newListOfParts.extend(self.getLinkerSP(part))
            else:
                newListOfParts.append(part)
        return newListOfParts

    def getWellContentDictFromPlateoPlate(
        self,
        plateoPlate: plateo.Plate,
        contentName: str
    ) -> Dict[str, Tuple[ComponentDefinition, float]]:
        """Get the contents of a well based on well data.
        Args:
            plateoPlate (plate.Plate): Plate to get well
                content from.
            contentName (str): Type of content in well ("Construct"
                or "Part).
        Returns:
            Dict[str, Tuple[ComponentDefinition, float]]: Dictionary
                of well content with wellname as keys, and component
                definition of the part or construct and concentration
                as values.
        """
        # TODO: Add option to include content vol/qty?
        # FIXME: Function works, but only outside of module?
        dictWellContent = {}
        for wellname, well in plateoPlate.wells.items():
            if contentName in well.data.keys():
                cd = well.data[contentName]
                if "concentration" in well.data.keys():
                    conc = well.data['concentration']
                    if conc == 0:
                        conc = np.nan
                else:
                    conc = np.nan
                dictWellContent[wellname] = (cd, conc)
        return dictWellContent

    def getListFromWellPartDict(
        self,
        dictWellPart: Dict[str, Tuple[ComponentDefinition, float]]
    ) -> List[str]:
        """Convert a dictionary of well contents into a list.
        Args:
            dictWellPart (Dict[str, Tuple[ComponentDefinition, float]]):
                Dictionary of well contents in a plate.
        Returns:
            List[str]: Formatted list of well contents.
        """
        listWellPart = []
        for k, v in dictWellPart.items():
            cd = v[0]
            conc = v[1]
            listWellPart.append([cd.displayId, k, conc])
        return listWellPart

    def getPartLinkerDfFromPlateoPlate(
        self,
        partPlate: plateo.Plate
    ) -> pd.DataFrame:
        """Get part/linker dataframe from a plate.
        Args:
            partPlate (plateo.Plate): Plate containing parts used for the
                assembly of constructs.
        Returns:
            pd.DataFrame: Dataframe of part/linkers and their associated
                wellname and concentration.
        """
        header = ["Part/linker", "Well", "Part concentration (ng/uL)"]
        dictWellPart = self.getWellContentDictFromPlateoPlate(
            partPlate,
            "Part"
        )
        listWellPart = self.getListFromWellPartDict(dictWellPart)
        sparr = pd.arrays.SparseArray(listWellPart)
        df = pd.DataFrame(data=sparr, columns=header)
        return df

    def getPartLinkerCsvFromPlateoPlate(
        self,
        constructPlate: plateo.Plate,
        assembly: str,
        dictOfParts: Dict[str, Dict[str, Union[str, int, float]]] = None
    ):
        """Get part/linker CSV from plate.
        Args:
            constructPlate (plateo.Plate): Construct plates from which
                parts and linkers are derived.
            assembly (str): Type of assembly.
            dictOfParts (Dict[str, Dict[str, Union[str, int, float]]]):
                Dictionary of parts and associated information.
        """
        def getPartName(well: plateo.Well) -> str:
            if "Part" in well.data.keys():
                cd = well.data["Part"]
                name = cd.displayId
            else:
                name = ""
            return name

        # TODO: Determine plate class?
        # Obtain all constructs from plate
        allConstructs = \
            self.getAllContentFromPlateoPlate(constructPlate, 'Construct')
        # Obtain parts and linkers from all constructs
        listOfParts = self.getListOfParts(allConstructs)
        # Change linker to linker-s and linker-p
        listOfParts = self.convertLinkerToSuffixPrefix(listOfParts)
        # Sort list of parts and linkers
        self.getSortedListOfParts(listOfParts)
        # Determine number of plates if dict is None
        if dictOfParts is None:
            numPlates = len(listOfParts) // 96 + (len(listOfParts) % 96 > 0)
        else:
            # Determine number of plates from dict of parts
            plates = [info["plate"] for part, info in dictOfParts.items()]
            plates = list(dict.fromkeys(plates))
            numPlates = len(plates)
        # Add parts and linkers to plate
        partPlates = self.fillPlateoPlates(
            listOfParts,
            "Part",
            numPlates,
            plateo.containers.Plate96,
            96,
            dictOfParts
        )
        for plate in partPlates:
            if assembly == "basic":
                # Create df
                partLinkerDf = self.getPartLinkerDfFromPlateoPlate(plate)
                filepath = \
                    os.path.join(
                        self.outdir,
                        "part_linker_" + str(partPlates.index(plate) + 1) + ".csv"
                    )
                partLinkerDf.to_csv(
                    filepath,
                    index=False
                )
                self.part_csv_paths.append(filepath)
            elif assembly == "moclo":
                filepath = \
                    os.path.join(
                        self.outdir,
                        "parts_" + str(partPlates.index(plate) + 1) + ".csv"
                    )
                # Generate platemap
                plate_to_platemap_spreadsheet(
                    plate,
                    getPartName,
                    filepath,
                    headers=False
                )
                self.part_csv_paths.append(filepath)
            elif assembly == "bio_bricks":
                # Create df
                partLinkerDf = self.getPartLinkerDfFromPlateoPlate(plate)
                filepath = \
                    os.path.join(
                        self.outdir,
                        "parts_" + str(partPlates.index(plate) + 1) + ".csv"
                    )
                partLinkerDf.to_csv(
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
        """

        def _get_linker_names():
            """Open standard linker document and extract all displayIds
            of linkers.
            """
            # Get list of linkers from linkerfile
            linkers = self.getRootComponentDefinitions(self.linkerFile)
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

        primary_structure = construct.getPrimaryStructure()

        is_first_comp_linker = False
        is_prev_comp_linker = False
        prev_comp = 0
        for i, comp in enumerate(primary_structure):
            is_curr_comp_linker = _is_linker(comp, linkers)
            # initialise
            if i == 0:
                is_first_comp_linker = is_curr_comp_linker
                is_prev_comp_linker = is_curr_comp_linker
                continue
            if is_prev_comp_linker == is_curr_comp_linker:
                print('prev_comp', prev_comp)
                print('comp', comp)
                print('REMOVE PRINTS')
                # raise ValueError("Order of components is not alternating")
            is_prev_comp_linker = is_curr_comp_linker
            prev_comp = comp
        if is_first_comp_linker:
            return True
        else:
            return False

    def validateBioBricksConstruct(
        self,
        construct: ComponentDefinition
    ) -> bool:
        """Check that biobricks construct has the structure
        plasmid-prefix-suffix.
        Args:
            construct (ComponentDefinition): Construct to check.
        Returns:
            bool: True if construct structure is correct.
        """
        primary_structure = construct.getPrimaryStructure()
        # Check that there are only 3 parts in the construct
        if len(primary_structure) != 3:
            raise ValueError(
                "There can only be 3 components in each construct"
            )
        # Check that construct contains a backbone
        containsPlasmid = False
        plasmidVector = "http://identifiers.org/so/SO:0000755"
        for cd in primary_structure:
            if plasmidVector in cd.roles:
                containsPlasmid = True
        if not containsPlasmid:
            raise ValueError(
                "Construct must contain plasmid vector"
            )
        # Check that backbone is not between parts
        midComponent = primary_structure[1]
        if plasmidVector in midComponent.roles:
            raise ValueError(
                "Backbone should not be between parts"
            )
        return True
