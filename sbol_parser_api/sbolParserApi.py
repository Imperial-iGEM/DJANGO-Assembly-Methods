import sbol2
import plateo
import plateo.containers
import plateo.tools
import warnings
import pandas as pd
import uuid
from typing import List, Dict


class ParserSBOL:

    def __init__(self, sbolDocument: sbol2.document.Document):
        self.doc = sbolDocument

    def generateCsv_for_DNABot(
            self,
            listOfNonCombUris: List[str],
            listOfCombUris: List[str]
    ):
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

        # Create plateo construct plates
        constructPlates = self.getPlateoConstructPlates(
            allConstructs,
            1,
            plateo.containers.Plate96,
            88
        )

        # Create construct CSVs from plateo plates
        for plate in constructPlates:
            uniqueId = uuid.uuid4().hex
            self.getConstructCsvFromPlateoPlate(plate, uniqueId)

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

    def getRootComponenentDefinitions(
            self) -> List[sbol2.componentdefinition.ComponentDefinition]:
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
            listOfNonCombUris: List[str] = [],
            listOfCombUris: List[str] = []
    ) -> List[sbol2.componentdefinition.ComponentDefinition]:
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
    def filterConstructs(self):
        raise NotImplementedError("Not yet implemented")

    def getListOfParts(
            self,
            allConstructs: List[sbol2.componentdefinition.ComponentDefinition] = []) -> List[sbol2.componentdefinition.ComponentDefinition]:
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

    def getSortedListOfParts(
            self,
            listOfParts: List[sbol2.componentdefinition.ComponentDefinition] = []
    ) -> List[sbol2.componentdefinition.ComponentDefinition]:
        """Get a sorted list of parts (str) from the list of parts.

        Args:
            listOfParts (list): List of parts to be sorted.

        Returns:
            list: List of sorted parts (str)
        """
        return listOfParts.sort(key=lambda x: x.displayId)

    def getDictOfComponents(
            self,
            listOfConstructs: List[sbol2.componentdefinition.ComponentDefinition]) -> Dict[str, sbol2.componentdefinition.ComponentDefinition]:
        """Get a dictionary of components (as component definitions)
        from the list of constructs as
        {construct.displayId: construct.components (as component definitions)}

        Args:
            listOfConstructs (list): List of constructs

        Returns:
            dict: Dictionary of components
        """
        return {x.displayId: x.getPrimaryStructure() for x in listOfConstructs}

    def getPlateoConstructPlates(
            self,
            allConstructs: List[sbol2.componentdefinition.ComponentDefinition],
            numPlate: int = None,
            plate_class: plateo.Plate = None,
            maxWellsFilled: int = None
    ) -> List[plateo.Plate]:
        """Generate a list of plateo plate objects from list of constructs

        Args:
            allConstructs (list): List of constructs
            numPlate (int): Number of plates to be generated (default = 1)
            plate_class (plateo.Plate):
                Class of plateo plate (default = Plate96)
            maxWellsFilled (int): Maximum number of filled wells on a plate

        Returns:
            list: List of plates
        """
        # TODO: Infer numPlate or plate_class?
        copyAllConstructs = allConstructs.copy()
        numPlate = 1 if numPlate is None else numPlate
        plate_class = (
            plateo.containers.Plate96 if plate_class is None else plate_class)
        num_wells = plate_class.num_rows*plate_class.num_columns
        maxWellsFilled = (
            num_wells if maxWellsFilled is None
            else maxWellsFilled)
        # Check if maxwells more than num_wells of plates
        if maxWellsFilled > num_wells:
            raise ValueError(
                "ValueError: maxWellsFilled must be less than"
                " plate_class.num_wells")
        # Check if numPlate*maxWellsFilled less than len(allconstructs)
        if numPlate*maxWellsFilled < len(allConstructs):
            raise ValueError(
                "ValueError: Length of allConstructs must be"
                " less than numPlate*maxWellsFilled")
        # Check if there will be empty plates
        if len(allConstructs) < (numPlate-1)*maxWellsFilled:
            warnings.warn("Number of constructs cannot fill all plates.")
        plates = [
            plate_class(name="Plate %d" % index)
            for index in range(1, numPlate + 1)]
        for plate in plates:
            for i in range(1, maxWellsFilled+1):
                while copyAllConstructs:
                    well = plate.wells[
                        plateo.tools.index_to_wellname(i, plate.num_wells)]
                    well.data = {"Construct": copyAllConstructs.pop(0)}
        return plates

    def getAllConstructsFromPlateoPlate(
        self,
        constructPlate: plateo.Plate
    ) -> List[sbol2.componentdefinition.ComponentDefinition]:
        '''Get a list of all constructs (as component definitions) from a
        Plateo plate.

        Args:
            constructPlate (plateo.Plate): Plateo plate containing constructs

        Returns:
            list: List of all constructs (as component definitions)
        '''
        allConstructs = []
        for well in constructPlate.iter_wells():
            for key, value in well.data.items():
                allConstructs.append(value)
        return allConstructs

    def getMinNumberOfBasicParts(
        self,
        allConstructs: List[sbol2.componentdefinition.ComponentDefinition]
    ) -> int:
        '''Get the minimum number of Part/Linker pairs required to perform
        BASIC assembly for all constructs.

        Args:
            allConstructs (list): List of all constructs as component
                definitions

        Returns:
            int: Number of Part/Linker paris for BASIC assembly
        '''
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
        '''Create header for Construct CSV for DNABot

        Args:
            minNumberOfBasicParts (int): Minimum number of of Part/Linker
                pairs required to perform BASIC assembly for all constructs

        Returns:
            List[str]: List of strings describing header for Construct CSV
        '''
        header = ["Well"]
        for i in range(1, minNumberOfBasicParts + 1):
            header.extend(["Linker %d" % i, "Part %d" % i])
        return header

    def getWellComponentDictFromPlateoPlate(
        self,
        constructPlate: plateo.Plate
    ) -> Dict[str, List[sbol2.componentdefinition.ComponentDefinition]]:
        '''Get a dictionary of wells containing constructs (as
        component definitions) in the form {Wellname:Construct}

        Args:
            constructPlate (plateo.Plate): Plateo plate containing constructs

        Returns:
            dict: Dictionary of wells containing constructs
        '''
        dictWellComponent = {}
        for wellname, well in constructPlate.wells.items():
            for key, value in well.data.items():
                dictWellComponent[wellname] = value.getPrimaryStructure()
        return dictWellComponent

    def getListFromWellComponentDict(
        self,
        dictWellComponent: Dict[str, sbol2.componentdefinition.ComponentDefinition]
    ) -> List[str]:
        '''Get a concatenated list of wellname and components (as display ID)
        comprising the construct from the dictionary of wells containing
        constructs.

        Args:
            dictWellComponent: Dictionary of wells containing constructs

        Returns:
            List[str]: List of wellnames and components (as display ID)
        '''
        listWellComponent = []
        for k, v in dictWellComponent.items():
            listWellComponent.append([k, *(x.displayId for x in v)])
        return listWellComponent

    def getConstructDfFromPlateoPlate(
        self,
        constructPlate: plateo.Plate
    ) -> pd.DataFrame:
        '''Get dataframe of constructs from Plateo plate containing constructs

        Args:
            constructPlate (plateo.Plate): Plateo plate containing constructs

        Returns:
            pd.DataFrame: Dataframe of constructs
        '''
        allComponents = self.getAllConstructsFromPlateoPlate(constructPlate)
        minNumberOfBasicParts = self.getMinNumberOfBasicParts(allComponents)
        header = self.getConstructCsvHeader(minNumberOfBasicParts)
        dictWellComponent = self.getWellComponentDictFromPlateoPlate(constructPlate)
        listWellComponent = self.getListFromWellComponentDict(dictWellComponent)
        # Create sparse array from list
        sparr = pd.arrays.SparseArray(listWellComponent)
        # Create df from sparr
        df = pd.DataFrame(data=sparr, columns=header)
        return df

    def getConstructCsvFromPlateoPlate(
        self,
        constructPlate: List[plateo.Plate],
        uniqueId: str = None
    ):
        '''Convert construct dataframe into CSV and creates CSV file in the same
        directory.

        Args:
            constructPlate (plateo.Plate): Plateo plate containing constructs
            uniqueId (str): Unique ID appended to filename
        '''
        constructDf = self.getConstructDfFromPlateoPlate(constructPlate)
        constructDf.to_csv(
            "construct_"+uniqueId+".csv",
            index=False)
