from sbol2 import *
from django.test import TestCase
from sbol_parser_api.sbol_parser_api import ParserSBOL
import pandas as pd
import os

EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests", "examples")


class TestSbolParserApi(TestCase):

    def setUp(self):
        basic_filepath = os.path.join(EXAMPLES_DIR, "basic_validation.xml")
        bb1_filepath = os.path.join(EXAMPLES_DIR, "bb_validation_actual_level1.xml")
        comb_1_filepath = os.path.join(EXAMPLES_DIR, "combinatorial_1var.xml")
        comb_nested_1_filepath = os.path.join(EXAMPLES_DIR, "combinatorial_nested1_one.xml")
        moclo_filepath = os.path.join(EXAMPLES_DIR, "moclo_validation.xml")
        dummy_filepath = os.path.join(EXAMPLES_DIR, "dummy.xml")
        basic_construct_csv = os.path.join(EXAMPLES_DIR, "basic_construct.csv")
        basic_part_1_csv = os.path.join(EXAMPLES_DIR, "basic_part_linker_1.csv")
        basic_part_2_csv = os.path.join(EXAMPLES_DIR, "basic_part_linker_2.csv")
        moclo_construct_csv = os.path.join(EXAMPLES_DIR, "moclo_construct.csv")
        moclo_part_csv = os.path.join(EXAMPLES_DIR, "moclo_parts_1.csv")
        bb_construct_csv = os.path.join(EXAMPLES_DIR, "bb_construct.csv")
        bb_part_csv = os.path.join(EXAMPLES_DIR, "bb_parts_1.csv")
        self.basic_doc = Document(basic_filepath)
        self.bb1_doc = Document(bb1_filepath)
        self.comb_1_doc = Document(comb_1_filepath)
        self.comb_nested_1_doc = Document(comb_nested_1_filepath)
        self.moclo_doc = Document(moclo_filepath)
        self.dummy_doc = Document(dummy_filepath)
        self.basic_construct_df = pd.read_csv(basic_construct_csv)
        self.basic_part_1_df = pd.read_csv(basic_part_1_csv)
        self.basic_part_2_df = pd.read_csv(basic_part_2_csv)
        self.moclo_construct_df = pd.read_csv(moclo_construct_csv)
        self.moclo_part_df = pd.read_csv(moclo_part_csv, header=None)
        self.bb_construct_df = pd.read_csv(bb_construct_csv)
        self.bb_part_df = pd.read_csv(bb_part_csv)
        self.maxDiff = None

    def test_generate_csv_basic(self):
        parser = ParserSBOL(self.basic_doc)
        part_info = {'BASIC_L3S2P21_J23101_RiboJ1': {'concentration': 211, 'plate': 1, 'well': 'D1'}, 'BASIC_L3S2P21_J23108_RiboJ1': {'concentration': 179, 'plate': 1, 'well': 'C1'}, 'BASIC_SEVA_36_CmR_p15A1': {'concentration': 70, 'plate': 1, 'well': 'E1'}, 'BASIC_mCherry_ORF1': {'concentration': 234, 'plate': 1, 'well': 'A1'}, 'BASIC_sfGFP_ORF1': {'concentration': 293, 'plate': 1, 'well': 'B1'}, 'L1RBS3_Prefix': {'concentration': '', 'plate': 2, 'well': 'C6'}, 'L1RBS3_Suffix': {'concentration': '', 'plate': 2, 'well': 'C3'}, 'LMP_Prefix': {'concentration': '', 'plate': 2, 'well': 'A7'}, 'LMP_Suffix': {'concentration': '', 'plate': 2, 'well': 'B7'}, 'LMS_Prefix': {'concentration': '', 'plate': 2, 'well': 'A8'}, 'LMS_Suffix': {'concentration': '', 'plate': 2, 'well': 'B8'}}
        files = parser.generate_csv("basic", part_info=part_info)
        construct_path = files["construct_path"]
        part_path = files["part_path"]
        # Compare construct csv
        construct_df = pd.read_csv(construct_path[0])
        construct_dict = construct_df.iloc[:, 1:-1].to_dict(orient='split')
        basic_construct_dict = self.basic_construct_df.iloc[:, 1:-1].to_dict(orient='split')
        # Assert data is equal
        self.assertCountEqual(construct_dict['data'], basic_construct_dict['data'])
        # Assert wells are equal
        self.assertCountEqual(list(construct_df.iloc[:, 0]), list(self.basic_construct_df.iloc[:, 0]))
        # Assert headings are equal
        self.assertListEqual(list(construct_df), list(self.basic_construct_df))
        # Compare part csv
        part_1_df = pd.read_csv(part_path[1])
        part_2_df = pd.read_csv(part_path[0])
        # Set NaN values to 0
        part_1_df.fillna(value=0, inplace=True)
        part_2_df.fillna(value=0, inplace=True)
        self.basic_part_1_df.fillna(value=0, inplace=True)
        self.basic_part_2_df.fillna(value=0, inplace=True)
        part_1_dict = part_1_df.to_dict()
        part_2_dict = part_2_df.to_dict()
        basic_part_1_dict = self.basic_part_1_df.to_dict()
        basic_part_2_dict = self.basic_part_2_df.to_dict()
        self.assertDictEqual(part_1_dict, basic_part_1_dict)
        self.assertDictEqual(part_2_dict, basic_part_2_dict)

    def test_generate_csv_moclo(self):
        parser = ParserSBOL(self.moclo_doc)
        files = parser.generate_csv("moclo")
        construct_path = files["construct_path"]
        part_path = files["part_path"]
        # Compare construct csv
        construct_df = pd.read_csv(construct_path[0])
        construct_dict = construct_df.to_dict(orient="split")
        moclo_construct_dict = self.moclo_construct_df.to_dict(orient="split")
        # Append "header" to data
        construct_dict['data'].append(construct_dict['columns'])
        moclo_construct_dict['data'].append(moclo_construct_dict['columns'])
        self.assertCountEqual(construct_dict['data'], moclo_construct_dict['data'])
        # Compare part csv
        part_df = pd.read_csv(part_path[0], header=None)
        # Set NaN values to 0
        part_df.fillna(value=0, inplace=True)
        self.moclo_part_df.fillna(value=0, inplace=True)
        part_dict = part_df.to_dict()
        moclo_part_dict = self.moclo_part_df.to_dict()
        self.assertDictEqual(part_dict, moclo_part_dict)

    def test_generate_csv_bio_bricks(self):
        parser = ParserSBOL(self.bb1_doc)
        files = parser.generate_csv("bio_bricks")
        construct_path = files["construct_path"]
        part_path = files["part_path"]
        # Compare construct csv
        construct_df = pd.read_csv(construct_path[0])
        # Assert header is equal
        self.assertListEqual(list(construct_df), list(self.bb_construct_df))
        # Assert wells are equal
        self.assertCountEqual(list(construct_df['Well']), list(self.bb_construct_df['Well']))
        # Remove Well column
        construct_df.drop(columns=['Well'], inplace=True)
        self.bb_construct_df.drop(columns=['Well'], inplace=True)
        # Assert data is equal
        construct_dict = construct_df.to_dict(orient="split")
        bb_construct_dict = self.bb_construct_df.to_dict(orient="split")
        self.assertCountEqual(construct_dict['data'], bb_construct_dict['data'])
        # Compare part csv
        part_df = pd.read_csv(part_path[0])
        # Set NaN values to 0
        part_df.fillna(value=0, inplace=True)
        self.bb_part_df.fillna(value=0, inplace=True)
        part_dict = part_df.to_dict()
        bb_part_dict = self.bb_part_df.to_dict()
        self.assertDictEqual(part_dict, bb_part_dict)
