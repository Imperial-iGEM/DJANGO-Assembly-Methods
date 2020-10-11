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

    def generate_dummy_components(self, num_comps=5):
        names = np.random.rand(num_comps)
        list_of_constructs = [sbol2.componentdefinition.ComponentDefinition(str(name)[0:5]) for name in names]
        for construct in list_of_constructs:
            self.doc.addComponentDefinition(construct)
        return list_of_constructs

    def test_generateCsv_for_DNABot(self):
        return

    def test_generateCsv_for_MoClo(self):
        return

    def test_getRootComponentDefinitions(self):
        for cd in self.parser.getRootComponentDefinitions():
            self.assertEquals(cd.displayId, 'Dummy')

    def test_getListOfParts(self):
        allConstructs = self.generate_dummy_components()
        construct = allConstructs[0]
        print('construct', construct)
        component = construct.components
        print('component', component)
        print('type(component)', type(component))
        defin = component.definition
        # print('\n\nallConstructs[0].components.definition', allConstructs[0].components.definition)

        list_of_parts = self.parser.getListOfParts(allConstructs)
        print('\n\nlist_of_parts', list_of_parts)
        assert type(list_of_parts[0]) == sbol2.componentdefinition.ComponentDefinition

    def test_getSortedListOfParts(self):
        listOfConstructs = self.generate_dummy_components()
        sorted_parts = self.parser.getSortedListOfParts(listOfConstructs)
        assert sorted_parts[0].displayId < sorted_parts[1].displayId, f'Sorting of component definitions not working, {sorted_parts[0].displayId} is not smaller than {sorted_parts[1]}'

    def test_getDictOfComponents(self):
        listOfConstructs = self.generate_dummy_components()
        return

        constructs_dict = self.parser.getDictOfComponents(listOfConstructs)  
        for key in constructs_dict.keys():
            assert type(key) == str, "Keys in dictionary of components not 'str' type displayId"
            assert constructs_dict[key] == list, "Values in dictionary of components not list"

    
