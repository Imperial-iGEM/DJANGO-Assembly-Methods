import sbol2
import plateo
import warnings
import pandas


class ParserSBOL:

    def __init__(self, sbolDocument: sbol2.Document()):
        self.doc = sbolDocument

    def generateCsv_for_DNABot(
            self,
            listOfNonCombUris: list,
            listOfCombUris: list):
        """Create construct and parts/linkers CSVs for DNABot input

        Args:
            listOfNonCombUris (list): List of component definition
                URIs pointing to non-combinatorial designs.
            listOfCombUris (list): List of combinatorial derivation
                URIs pointing to combinatorial designs.
        """
        allConstructs = []

        # Get list of constructs
        allConstructs = self.getListOfConstructs(
            listOfNonCombUris,
            listOfCombUris)

        # TODO: Filter constructs - to improve

        # TODO: Select constructs - implement in filter?

        # Display number of Component Definitions to be constructed
        numberOfDesigns = len(allConstructs)
        print(numberOfDesigns, "construct(s) will be assembled.")

        # TODO: Check/Insert backbone - to handle on frontend?

        # TODO: Insert up to 7 linkers - to handle on frontend?

        # TODO: Create plate from all constructs

        # TODO: Write constructs csv from plate

        # Obtain parts and linkers
        listOfParts = self.getListOfParts(allConstructs)

        # TODO: Convert list of parts from component definition to str

        # TODO: If part is a linker, include prefix/suffix entries
        # Obtain linkers from frontend?

        # Sort parts/linkers alphabetically
        sortedListOfParts = self.getSortedListOfParts(listOfParts)

        # TODO: Write parts/linkers csv

    def generateCsv_for_MoClo(self):
        raise NotImplementedError("Not yet implemented")

    def getRootComponenentDefinitions(self) -> list:
        """Get the root component definitions of an SBOL document.

        Returns:
            list: List of root component definitions.
        """
        componentDefs = self.doc.componentDefinitions
        # Remove child components of component definitions
        for obj in self.doc.componentDefinitions:
            for component in obj.components:
                childDefinition = component.definition
                if(childDefinition is not None
                        and childDefinition in componentDefs):
                    componentDefs.remove(childDefinition)
        # Remove child components of combinatorial derivations
        for obj in self.doc.combinatorialderivations:
            for variableComponent in obj.variableComponents:
                for childDefinition in variableComponent.variants:
                    if(childDefinition is not None
                            and childDefinition in componentDefs):
                        componentDefs.remove(childDefinition)
        return componentDefs

    def getListOfConstructs(
            self,
            listOfNonCombUris: list = [],
            listOfCombUris: list = []) -> list:
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
        # Add non-combinatorial constructs to list
        for uri in listOfNonCombUris:
            listOfConstructs.append(self.doc.getComponentDefinition(uri))
        # Add combinatorial constructs to list
        for uri in listOfCombUris:
            # Enumerate Combinatorial Derivations and add to allConstructs
            # sbol2 doesnt have getCombinatorialDerivation() function
            listOfConstructs.extend(self.enumerator(
                self.doc.combinatorialderivations.get(uri)))
        return listOfConstructs

    # TODO: Implement an Enumerator class?
    def enumerator(self) -> list:
        raise NotImplementedError("Not yet implemented")

    # TODO: Implement a Filter class?
    def filter(self):
        raise NotImplementedError("Not yet implemented")

    def getListOfParts(
            self,
            allConstructs: list = []) -> list:
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
                    self.doc.getComponentDefinition(component.definition))
        # Remove duplicate components
        listOfParts = list(dict.fromkeys(listOfParts))
        return listOfParts

    def getSortedListOfParts(self, listOfParts: list = []) -> list:
        """Get a sorted list of parts (str) from the list of parts.

        Args:
            listOfParts (list): List of parts to be sorted.

        Returns:
            list: List of sorted parts (str)
        """
        return listOfParts.sort(key=lambda x: x.displayId)

    def getDictOfComponents(self, listOfConstructs: list) -> dict:
        return {x.displayId: x.getPrimaryStructure() for x in listOfConstructs}

    def plateo_plates_from_constructs(
            self,
            allConstructs: list,
            numPlate: int = None,
            plate_class=None,
            maxWellsFilled: int = None) -> list:
        numPlate = 1 if numPlate is None else numPlate
        plate_class = (
            plateo.containers.Plate96 if plate_class is None else plate_class)
        maxWellsFilled = (
            plate_class.num_wells if maxWellsFilled is None
            else maxWellsFilled)
        # Check if maxwells more than num_wells of plates
        if maxWellsFilled > plate_class.num_wells:
            raise ValueError(
                "ValueError: maxWellsFilled must be less than"
                " plate_class.num_wells")
        # Check if numPlate*maxWellsFilled less than len(allconstructs)
        if numPlate*maxWellsFilled < len(allConstructs):
            raise ValueError(
                "ValueError: Length of allConstructs must be"
                " less than numPlate*maxWellsFilled")
        # Check if there will be empty plates
        if len(allConstructs)/maxWellsFilled < numPlate:
            warnings.warn("Number of constructs cannot fill all plates.")
        plates = {
            index: plateo.containers.Plate96(name="Plate %d" % index)
            for index in range(1, numPlate + 1)}
        # TODO: Put wells into plates
        return NotImplementedError("Not yet implemented")
