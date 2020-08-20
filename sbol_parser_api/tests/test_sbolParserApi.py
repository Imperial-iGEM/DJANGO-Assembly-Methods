import sbol2
from django.test import TestCase
from sbol_parser_api.sbolParserApi import ParserSBOL
import numpy as np


# class ComponentDefinition(sbol2.ComponentDefinition):
#     def __repr__(self):
#         self.displayId


class TestSbolParserApi(TestCase):

    # def __init__(self, x):
    #     self.setUp()

    def setUp(self):
        filepath = "./examples/sbol/dummy.xml"
        self.doc = sbol2.Document(filepath)
        self.parser = ParserSBOL(sbol2.Document(filepath))

    def test_generateCsv_for_DNABot(self):
        raise NotImplementedError("Not yet implemented")

    def test_generateCsv_for_MoClo(self):
        raise NotImplementedError("Not yet implemented")

    def test_getRootComponentDefinitions(self):
        for cd in self.parser.getRootComponenentDefinitions():
            self.assertEquals(cd.displayId, 'Dummy')

    def test_getSortedListOfParts(self):
        names = np.random.rand(5)
        listOfConstructs = [sbol2.componentdefinition.ComponentDefinition(str(name)[0:5]) for name in names]
        sorted_parts = self.parser.getSortedListOfParts(listOfConstructs)

        assert sorted_parts[0].displayId < sorted_parts[1].displayId, f'Sorting of component definitions not working, {sorted_parts[0].displayId} is not smaller than {sorted_parts[1]}'

    def test_getDictOfComponents(self):
        names = np.random.rand(5)
        listOfConstructs = [sbol2.componentdefinition.ComponentDefinition(str(name)[0:5]) for name in names]
        uris = []
        for construct in listOfConstructs:
            self.doc.addComponentDefinition(construct)
            uris.append(construct.uris)
        constructs_dict = self.parser.getDictOfComponents(listOfConstructs)  

        for key in constructs_dict.keys():
            assert type(key) == str, "Keys in dictionary of components not 'str' type displayId"
            assert constructs_dict[key] == list, "Values in dictionary of components not list"

    # def test_
