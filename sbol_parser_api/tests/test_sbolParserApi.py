import sbol2
from django.test import TestCase
from sbol_parser_api.sbolParserApi import ParserSBOL


class TestSbolParserApi(TestCase):

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
