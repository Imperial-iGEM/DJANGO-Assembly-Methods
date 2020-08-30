import sbol2
import plateo
import plateo.containers
import plateo.tools
import warnings
import pandas as pd
import uuid
import numpy as np
from typing import List, Dict


class ParserSBOL:

    def __init__(self, sbolDocument: sbol2.document.Document):
        self.doc = sbolDocument

    def generateCsv_for_DNABot(
            self,
            listOfNonCombUris: List[str],
            listOfCombUris: List[str],
            linkerFile: sbol2.document.Document
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

        # Create plateo construct plates
        constructPlates = self.fillPlateoPlates(
            allConstructs,
            "Construct",
            1,
            plateo.containers.Plate96,
            88
        )

        # Create construct and parts/linkers CSVs from plateo plates
        for plate in constructPlates:
            # Create UUID
            uniqueId = uuid.uuid4().hex
            # Create construct CSV
            self.getConstructCsvFromPlateoPlate(plate, uniqueId)
            # Write parts/linkers csv
            self.getPartLinkerCsvFromPlateoPlate(plate, linkerFile, uniqueId)

    def generateCsv_for_MoClo(self):
        raise NotImplementedError("Not yet implemented")

    def getRootComponenentDefinitions(
            self,
            sbolDocument: sbol2.document.Document = None
    ) -> List[sbol2.componentdefinition.ComponentDefinition]:
        """Get the root component definitions of an SBOL document.

        Args:
            sbolDocument (sbol2.document.Document): SBOL document from
                which to get root component definitions (default: self.doc)

        Returns:
            list: List of root component definitions.
        """
        document = self.doc if sbolDocument is None else sbolDocument
        componentDefs = list(document.componentDefinitions)
        # Remove child components of component definitions
        for obj in document.componentDefinitions:
            for component in obj.components:
                childDefinition = document.getComponentDefinition(component.definition)
                if(childDefinition is not None
                        and childDefinition in componentDefs):
                    componentDefs.remove(childDefinition)
        # Remove child components of combinatorial derivations
        for obj in document.combinatorialderivations:
            for variableComponent in obj.variableComponents:
                # TODO: Verify that variants are component definitions
                for childDefinition in variableComponent.variants:
                    if(childDefinition is not None
                            and childDefinition in componentDefs):
                        componentDefs.remove(childDefinition)
        return list(componentDefs)

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
            listOfParts: List[sbol2.componentdefinition.ComponentDefinition]
    ) -> List[sbol2.componentdefinition.ComponentDefinition]:
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

    def fillPlateoPlates(
            self,
            allContent: List[sbol2.componentdefinition.ComponentDefinition],
            contentName: str,
            numPlate: int = None,
            plate_class: plateo.Plate = None,
            maxWellsFilled: int = None
    ) -> List[plateo.Plate]:
        """Generate a list of plateo plate objects from list of constructs

        Args:
            allContent (list): List of constructs
            contentName (str): Name of content (Construct or Part)
            numPlate (int): Number of plates to be generated (default = 1)
            plate_class (plateo.Plate):
                Class of plateo plate (default = Plate96)
            maxWellsFilled (int): Maximum number of filled wells on a plate

        Returns:
            list: List of plates
        """
        # TODO: Infer numPlate or plate_class?
        # TODO: Input well content vol and qty
        copyAllContent = allContent.copy()
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
        # Check if numPlate*maxWellsFilled less than len(allContent)
        if numPlate*maxWellsFilled < len(allContent):
            raise ValueError(
                "ValueError: Length of allContent must be"
                " less than numPlate*maxWellsFilled")
        # Check if there will be empty plates
        if len(allContent) < (numPlate-1)*maxWellsFilled:
            warnings.warn("Number of "+contentName+"s cannot fill all plates.")
        plates = [
            plate_class(name="Plate %d" % index)
            for index in range(1, numPlate + 1)]
        for plate in plates:
            for i in range(1, maxWellsFilled+1):
                if copyAllContent:
                    well = plate.wells[
                        plateo.tools.index_to_wellname(i, plate.num_wells)]
                    well.data = {contentName: copyAllContent.pop(0)}
        return plates

    def getAllContentFromPlateoPlate(
        self,
        contentPlate: plateo.Plate
    ) -> List[sbol2.componentdefinition.ComponentDefinition]:
        '''Get a list of all content (as component definitions) from a
        Plateo plate.

        Args:
            contentPlate (plateo.Plate): Plateo plate containing content

        Returns:
            list: List of all content (as component definitions)
        '''
        allContent = []
        for well in contentPlate.iter_wells():
            for key, value in well.data.items():
                allContent.append(value)
        return allContent

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
        '''Get a dictionary of wells containing components comprising
        constructs (as component definitions) in the form
        {Wellname:[Components]}

        Args:
            constructPlate (plateo.Plate): Plateo plate containing constructs

        Returns:
            dict: Dictionary of wells containing constructs
        '''
        dictWellComponent = {}
        for wellname, well in constructPlate.wells.items():
            for key, value in well.data.items():
                # TODO: Move linker at last position to front of the list
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
        allComponents = self.getAllContentFromPlateoPlate(constructPlate)
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
        constructPlate: plateo.Plate,
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

    def isLinker(
        self,
        part: sbol2.componentdefinition.ComponentDefinition,
        linkerFile: sbol2.document.Document
    ) -> bool:
        linkers = self.getRootComponenentDefinitions(linkerFile)
        if part.identity in [linker.identity for linker in linkers]:
            return True
        else:
            return False

    def getLinkerSP(
        self,
        linker: sbol2.componentdefinition.ComponentDefinition,
    ) -> List[sbol2.componentdefinition.ComponentDefinition]:
        linkersp = []
        for component in linker.components:
            linkersp.append(
                self.doc.getComponentDefinition(component.definition))
        return linkersp

    def convertLinkerToSuffixPrefix(
        self,
        listOfParts: List[sbol2.componentdefinition.ComponentDefinition],
        linkerFile: sbol2.document.Document
    ) -> List[sbol2.componentdefinition.ComponentDefinition]:
        newListOfParts = []
        for part in listOfParts:
            if self.isLinker(part, linkerFile):
                newListOfParts.extend(self.getLinkerSP(part))
            else:
                newListOfParts.append(part)
        return newListOfParts

    def getWellContentDictFromPlateoPlate(
        self,
        plateoPlate: plateo.Plate,
        contentName: str
    ) -> Dict[str, List[sbol2.componentdefinition.ComponentDefinition]]:
        # TODO: Add option to include content vol/qty?
        # FIXME: Function works, but only outside of module?
        dictWellContent = {}
        for wellname, well in plateoPlate.wells.items():
            if contentName in well.data.keys():
                dictWellContent[wellname] = well.data[contentName]
        return dictWellContent

    def getListFromWellPartDict(
        self,
        dictWellPart: Dict[str, List[sbol2.componentdefinition.ComponentDefinition]]
    ) -> List[str]:
        listWellPart = []
        for k, v in dictWellPart.items():
            listWellPart.append([v.displayId, k, np.nan])
        return listWellPart

    def getPartLinkerDfFromPlateoPlate(
        self,
        partPlate: plateo.Plate
    ) -> pd.DataFrame:
        header = ["Part/linker", "Well", "Part concentration (ng/uL)"]
        dictWellPart = self.getWellContentDictFromPlateoPlate(partPlate, "Part")
        listWellPart = self.getListFromWellPartDict(dictWellPart)
        sparr = pd.arrays.SparseArray(listWellPart)
        df = pd.DataFrame(data=sparr, columns=header)
        return df

    def getPartLinkerCsvFromPlateoPlate(
        self,
        constructPlate: plateo.Plate,
        linkerFile: sbol2.document.Document,
        uniqueId: str = None
    ):
        # Obtain all constructs from plate
        allConstructs = self.getAllContentFromPlateoPlate(constructPlate)
        # Obtain parts and linkers from all constructs
        listOfParts = self.getListOfParts(allConstructs)
        # Change linker to linker-s and linker-p
        listOfParts = self.convertLinkerToSuffixPrefix(listOfParts, linkerFile)
        # Sort list of parts and linkers
        self.getSortedListOfParts(listOfParts)
        # Add parts and linkers to plate
        # TODO: Calculate part/linker concentration
        # TODO: Add part/linker concentration to plate
        partPlates = self.fillPlateoPlates(
            listOfParts,
            "Part",
            1,
            plateo.containers.Plate96,
            96
        )
        for plate in partPlates:
            # Create df
            partLinkerDf = self.getPartLinkerDfFromPlateoPlate(plate)
            # TODO: Create csv
            partLinkerDf.to_csv(
                "part_linker_"+str(partPlates.index(plate)+1)+uniqueId,
                index=False
            )
