import pandas as pd
import numpy as np
import unittest
from unittest.mock import patch
import csv
import sys
import os
#parentdir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, '/biobricks10'))
TEST_DIR = "/home/runner/work/DJANGO-Assembly-Methods/DJANGO-Assembly-Methods/biobricks_assembly/tests/"
sys.path.append("/home/runner/work/DJANGO-Assembly-Methods/DJANGO-Assembly-Methods/biobricks_assembly/biobricks10/")
import bbinput
from . import side_effect_functions

class BioBricksInputTestCase(unittest.TestCase):

    def setUp(self):
        self.constructs_list = [['Construct', 'Well', 'upstream', 'downstream',
                                 'plasmid'],
                                ['construct1', 'A1', 'BBa_B0034', 'BBa_C0040',
                                 'BBa_pSB1AK3'],
                                ['construct2', 'A2', 'BBa_B0034', 'BBa_C0012',
                                 'BBa_pSB1AK3'],
                                ['construct3', 'A3', 'BBa_C0012', 'BBa_B0015',
                                 'BBa_pSB1AK3']]

        self.construct_dicts = [{'name': ['construct1'], 'well': ['A1'],
                                 'upstream': ['BBa_B0034'], 'downstream':
                                 ['BBa_C0040'], 'plasmid': ['BBa_pSB1AK3']},
                                {'name': ['construct2'], 'well': ['A2'],
                                 'upstream': ['BBa_B0034'], 'downstream':
                                 ['BBa_C0012'], 'plasmid': ['BBa_pSB1AK3']},
                                {'name': ['construct3'], 'well': ['A3'],
                                 'upstream': ['BBa_C0012'], 'downstream':
                                 ['BBa_B0015'], 'plasmid': ['BBa_pSB1AK3']}]

        self.parts_list = [['Part', 'Well', 'Part concentration'],
                           ['BBa_B0034', 'A1', '500'],
                           ['BBa_C0040', 'A2', '500'],
                           ['BBa_pSB1AK3', 'A3', '500'],
                           ['BBa_C0012', 'A4', '500'],
                           ['BBa_B0015', 'A5', ]]

        self.part_dfs = [pd.DataFrame(data={'name': ['BBa_B0034'], 'well':
                                            ['A1'], 'occurences': [[2, 0, 0]],
                                            'roles': [['upstream']], 'digests':
                                            [1], 'concentration': [500],
                                            'part_vol': [1], 'water_vol': [42],
                                            'part_vol_tot': [1],
                                            'water_vol_tot': [42],
                                            'constructs_in': [[[0, 1], [],
                                                              []]]}),
                         pd.DataFrame(data={'name': ['BBa_C0040'], 'well':
                                            ['A2'], 'occurences': [[0, 1, 0]],
                                            'roles': [['downstream']],
                                            'digests': [1], 'concentration':
                                            [500], 'part_vol': [1],
                                            'water_vol': [42], 'part_vol_tot':
                                            [1], 'water_vol_tot': [42],
                                            'constructs_in': [[[], [0], []]]}),
                         pd.DataFrame(data={'name': ['BBa_pSB1AK3'], 'well':
                                            ['A3'], 'occurences': [[0, 0, 3]],
                                            'roles': [['plasmid']], 'digests':
                                            [1], 'concentration': [500],
                                            'part_vol': [1], 'water_vol': [42],
                                            'part_vol_tot': [1],
                                            'water_vol_tot': [42],
                                            'constructs_in': [[[], [], [0, 1,
                                                                        2]]]}),
                         pd.DataFrame(data={'name': ['BBa_C0012'], 'well':
                                            ['A4'], 'occurences': [[1, 1, 0]],
                                            'roles': [['upstream', 'downstream'
                                                       ]], 'digests': [2],
                                            'concentration': [500], 'part_vol':
                                            [1], 'water_vol': [42],
                                            'part_vol_tot': [2],
                                            'water_vol_tot': [84],
                                            'constructs_in': [[[2], [1],
                                                              []]]}),
                         pd.DataFrame(data={'name': ['BBa_B0015'], 'well':
                                            ['A5'], 'occurences': [[0, 1, 0]],
                                            'roles': [['downstream']],
                                            'digests': [1], 'concentration':
                                            [500], 'part_vol': [1],
                                            'water_vol': [42], 'part_vol_tot':
                                            [1], 'water_vol_tot': [42],
                                            'constructs_in': [[[], [2], []]]})]

        self.parts_df = pd.concat(self.part_dfs, ignore_index=True)

        self.constructs_df = pd.DataFrame(
                np.array([self.constructs_list[1], self.constructs_list[2],
                          self.constructs_list[3]]),
                columns=['name', 'well', 'upstream', 'downstream', 'plasmid'])

        self.construct_wells = ['A1', 'A2', 'A3']

        self.occ = [[2, 0, 0], [0, 1, 0], [0, 0, 3], [1, 1, 0], [0, 1, 0]]
        self.cons_in = [[[0, 1], [], []], [[], [0], []], [[], [], [0, 1, 2]],
                        [[2], [1], []], [[], [2], []]]

        self.all_wells = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9',
                          'A10', 'A11', 'A12', 'B1', 'B2', 'B3', 'B4', 'B5',
                          'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12', 'C1',
                          'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9',
                          'C10', 'C11', 'C12', 'D1', 'D2', 'D3', 'D4', 'D5',
                          'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12', 'E1',
                          'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9',
                          'E10', 'E11', 'E12', 'F1', 'F2', 'F3', 'F4', 'F5',
                          'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'G1',
                          'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9',
                          'G10', 'G11', 'G12', 'H1', 'H2', 'H3', 'H4', 'H5',
                          'H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12']

        self.all_wells_reagent = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'B1',
                                  'B2', 'B3', 'B4', 'B5', 'B6', 'C1', 'C2',
                                  'C3', 'C4', 'C5', 'C6', 'D1', 'D2', 'D3',
                                  'D4', 'D5', 'D6']

        self.reagent_dfs = [pd.DataFrame(data={'name': ['water'], 'well':
                                               ['A1'], 'total_vol': [285]}),
                            pd.DataFrame(data={'name': ['mm_upstream'],
                                               'well': ['A2'], 'total_vol':
                                               [28]}),
                            pd.DataFrame(data={'name': ['mm_downstream'],
                                               'well': ['A3'], 'total_vol':
                                               [35]}),
                            pd.DataFrame(data={'name': ['mm_plasmid'],
                                               'well': ['A4'], 'total_vol':
                                               [21]}),
                            pd.DataFrame(data={'name': ['T4Ligase10X'], 'well':
                                               ['A5'], 'total_vol': [6]}),
                            pd.DataFrame(data={'name': ['T4Ligase'], 'well':
                                               ['A6'], 'total_vol': [3]})]
        self.reagents_df = pd.concat(self.reagent_dfs, ignore_index=True)
        self.reagents_wells = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6']
        self.mm_df = pd.DataFrame(
            data={'reagent': ['NEB Buffer 10X', 'EcoRI-HF', 'SpeI', 'XbaI',
                              'PstI'],
                  'volume in upstream mm': [20, 4, 4, 0, 0],
                  'volume in downstream mm': [25, 0, 0, 5, 5],
                  'volume in plasmid mm': [15, 3, 0, 0, 3]})
        self.constructs_wells = ['A1', 'A2', 'A3']

        self.parts_digest_wells = [['A4'], ['A5'], ['A6'], ['A7', 'A8'], ['A9']
                                   ]
        self.parts_df_full = self.parts_df.copy()
        self.parts_df_full['digest_wells'] = [['A4'], ['A5'], ['A6'],
                                              ['A7', 'A8'], ['A9']]

        self.digest_dfs = [pd.DataFrame(data={'name': ['BBa_B0034-upstream'],
                                              'role': ['upstream'], 'part':
                                              ['BBa_B0034'], 'source_well':
                                              ['A1'], 'dest_well': ['A4'],
                                              'reagent_well': ['B1'],
                                              'construct_wells':
                                              [['A1', 'A2']]}),
                           pd.DataFrame(data={'name': ['BBa_C0040-downstream'],
                                              'role': ['downstream'], 'part':
                                              ['BBa_C0040'], 'source_well':
                                              ['A2'], 'dest_well': ['A5'],
                                              'reagent_well': ['B2'],
                                              'construct_wells': [['A1']]}),
                           pd.DataFrame(data={'name': ['BBa_pSB1AK3-plasmid'],
                                              'role': ['plasmid'], 'part':
                                              ['BBa_pSB1AK3'], 'source_well':
                                              ['A3'], 'dest_well': ['A6'],
                                              'reagent_well': ['B3'],
                                              'construct_wells':
                                              [['A1', 'A2', 'A3']]}),
                           pd.DataFrame(data={'name': ['BBa_C0012-upstream'],
                                              'role': ['upstream'], 'part':
                                              ['BBa_C0012'], 'source_well':
                                              ['A4'], 'dest_well': ['A7'],
                                              'reagent_well': ['B4'],
                                              'construct_wells': [['A3']]}),
                           pd.DataFrame(data={'name': ['BBa_C0012-downstream'],
                                              'role': ['downstream'], 'part':
                                              ['BBa_C0012'], 'source_well':
                                              ['A4'], 'dest_well': ['A8'],
                                              'reagent_well': ['B5'],
                                              'construct_wells': [['A2']]}),
                           pd.DataFrame(data={'name': ['BBa_B0015-downstream'],
                                              'role': ['downstream'], 'part':
                                              ['BBa_B0015'], 'source_well':
                                              ['A5'], 'dest_well': ['A9'],
                                              'reagent_well': ['B6'],
                                              'construct_wells': [['A3']]})]

        self.digests_df = pd.concat(self.digest_dfs, ignore_index=True)

        self.source_to_digest = {'A1': [('A4', 1)], 'A2': [('A5', 1)], 'A3':
                                 [('A6', 1)], 'A4': [('A7', 1), ('A8', 1)],
                                 'A5': [('A9', 1)]}

        self.reagent_to_digest = {"A1": [("A4", 42), ("A5", 42), ("A6", 42),
                                         ("A7", 42), ("A8", 42), ("A9", 42)],
                                  "A2": [("A4", 7), ("A7", 7)],
                                  "A3": [("A5", 7), ("A8", 7), ("A9", 7)],
                                  "A4": [("A6", 7)]}

        self.digest_to_storage = {"A4": [("B1", 48)], "A5": [("B2", 48)],
                                  "A6": [("B3", 48)], "A7": [("B4", 48)],
                                  "A8": [("B5", 48)], "A9": [("B6", 48)]}


        self.digest_to_construct = {'A4': [('A1', 2), ('A2', 2)],
                                    'A5': [('A1', 2)],
                                    'A6': [('A1', 2), ('A2', 2), ('A3', 2)],
                                    'A7': [('A3', 2)], 'A8': [('A2', 2)],
                                    'A9': [('A3', 2)]}

        self.reagent_to_construct = {'A1': [('A1', 11), ('A2', 11),
                                            ('A3', 11)],
                                     'A5': [('A1', 2), ('A2', 2), ('A3', 2)],
                                     'A6': [('A1', 1), ('A2', 1), ('A3', 1)]}
        
        self.competent_source_to_dest = {"A4": [("A1", 50), ("A2", 50),
                                                ("A3", 50)],
                                         "A5": [("A4", 50), ("A5", 50),
                                                ("A6", 50)],
                                         "A6": [("A7", 50), ("A8", 50),
                                                ("A9", 50)],
                                         "A7": [("A10", 50), ("A11", 50),
                                                ("A12", 50)]}

        self.control_source_to_dest = {"A8": [("B1", 50), ("B2", 50),
                                              ("B3", 50)]}

        self.assembly_source_to_dest = {"A1": [("A1", 1), ("A2", 1), ("A3", 1),
                                               ("A4", 1)],
                                        "A2": [("A5", 1), ("A6", 1), ("A7", 1),
                                               ("A8", 1)],
                                        "A3": [("A9", 1), ("A10", 1),
                                               ("A11", 1), ("A12", 1)]}

        self.water_to_dest = {"A1": [("B1", 1), ("B2", 1), ("B3", 1)]}
        self.entry_dfs = [
            pd.DataFrame(data={'name': ['construct1-0'],
                               'number': [0], 'cell_type': ['competent'],
                               'construct': 'construct1', 'construct_well':
                               ['A1'], 'cell_well': ['A4'], 'dest_well':
                               ['A1'], 'reagent_well': [None]}),
            pd.DataFrame(data={'name': ['construct1-1'], 'number': [1],
                               'cell_type': ['competent'], 'construct':
                               'construct1', 'construct_well': ['A1'],
                               'cell_well': ['A4'], 'dest_well': ['A2'],
                               'reagent_well': [None]}),
            pd.DataFrame(data={'name': ['construct1-2'], 'number': [2],
                               'cell_type': ['competent'], 'construct':
                               'construct1', 'construct_well': ['A1'],
                               'cell_well': ['A4'], 'dest_well': ['A3'],
                               'reagent_well': [None]}),
            pd.DataFrame(data={'name': ['construct1-3'], 'number': [3],
                               'cell_type': ['competent'], 'construct':
                               'construct1', 'construct_well': ['A1'],
                               'cell_well': ['A5'], 'dest_well': ['A4'],
                               'reagent_well': [None]}),
            pd.DataFrame(data={'name': ['construct2-0'], 'number': [0],
                               'cell_type': ['competent'], 'construct':
                               'construct2', 'construct_well': ['A2'],
                               'cell_well': ['A5'], 'dest_well': ['A5'],
                               'reagent_well': [None]}),
            pd.DataFrame(data={'name': ['construct2-1'], 'number': [1],
                               'cell_type': ['competent'], 'construct':
                               'construct2', 'construct_well': ['A2'],
                               'cell_well': ['A5'], 'dest_well': ['A6'],
                               'reagent_well': [None]}),
            pd.DataFrame(data={'name': ['construct2-2'], 'number': [2],
                               'cell_type': ['competent'], 'construct':
                               'construct2', 'construct_well': ['A2'],
                               'cell_well': ['A6'], 'dest_well': ['A7'],
                               'reagent_well': [None]}),
            pd.DataFrame(data={'name': ['construct2-3'], 'number': [3],
                               'cell_type': ['competent'], 'construct':
                               'construct2', 'construct_well': ['A2'],
                               'cell_well': ['A6'], 'dest_well': ['A8'],
                               'reagent_well': [None]}),
            pd.DataFrame(data={'name': ['construct3-0'], 'number': [0],
                               'cell_type': ['competent'], 'construct':
                               'construct3', 'construct_well': ['A3'],
                               'cell_well': ['A6'], 'dest_well': ['A9'],
                               'reagent_well': [None]}),
            pd.DataFrame(data={'name': ['construct3-1'], 'number': [1],
                               'cell_type': ['competent'], 'construct':
                               'construct3', 'construct_well': ['A3'],
                               'cell_well': ['A7'], 'dest_well': ['A10'],
                               'reagent_well': [None]}),
            pd.DataFrame(data={'name': ['construct3-2'], 'number': [2],
                               'cell_type': ['competent'], 'construct':
                               'construct3', 'construct_well': ['A3'],
                               'cell_well': ['A7'], 'dest_well': ['A11'],
                               'reagent_well': [None]}),
            pd.DataFrame(data={'name': ['construct3-3'], 'number': [3],
                               'cell_type': ['competent'], 'construct':
                               'construct3', 'construct_well': ['A3'],
                               'cell_well': ['A7'], 'dest_well': ['A12'],
                               'reagent_well': [None]}),
            pd.DataFrame(data={'name': ['control-0'], 'number': [0],
                               'cell_type': ['control'], 'construct': [None],
                               'construct_well': [None], 'cell_well': ['A8'],
                               'dest_well': ['B1'], 'reagent_well': ['A1']}),
            pd.DataFrame(data={'name': ['control-1'], 'number': [1],
                               'cell_type': ['control'], 'construct': [None],
                               'construct_well': [None], 'cell_well': ['A8'],
                               'dest_well': ['B2'], 'reagent_well': ['A1']}),
            pd.DataFrame(data={'name': ['control-2'], 'number': [2],
                               'cell_type': ['control'], 'construct': [None],
                               'construct_well': [None], 'cell_well': ['A8'],
                               'dest_well': ['B3'], 'reagent_well': ['A1']})]
        self.transform_df = pd.concat(self.entry_dfs, ignore_index=True)

    def tearDown(self):
        pass

    def test_process_construct(self):
        for i in range(len(self.constructs_list)-1):
            construct = self.constructs_list[i+1]
            processed = bbinput.process_construct(construct)
            self.assertDictEqual(processed, self.construct_dicts[i])

    @patch('bbinput.process_construct',
           side_effect=side_effect_functions.process_cons)
    def test_get_constructs(self, mock_process_construct):
        with patch('csv.reader') as mocked_reader:
            mocked_reader.return_value = self.constructs_list
            cons_df, dest_wells = bbinput.get_constructs(
                            os.path.join(TEST_DIR, 'testfiles/constructs.csv'))
            self.assertListEqual(dest_wells, self.construct_wells)
            for col in ['name', 'well', 'upstream', 'downstream', 'plasmid']:
                self.assertListEqual(cons_df[col].to_list(),
                                     self.constructs_df[col].to_list())

    def test_count_part_occurrences(self):
        for index, part in enumerate(self.parts_list):
            if index != 0:
                self.assertListEqual(bbinput.count_part_occurences(
                            self.constructs_df, part)[0], self.occ[index-1])
                self.assertListEqual(bbinput.count_part_occurences(
                            self.constructs_df, part)[1], self.cons_in[index-1]
                                     )

    def test_process_part(self):
        for index, part in enumerate(self.parts_list):
            if index != 0:
                df = bbinput.process_part(part, self.constructs_df)
                part_df = self.part_dfs[index - 1]
                for col in df.columns:
                    self.assertListEqual(df[col].to_list(),
                                         part_df[col].to_list())

    @patch('bbinput.process_part',
           side_effect=side_effect_functions.process_part)
    def test_get_parts(self, mock_process_part):
        with patch('csv.reader') as mocked_reader:
            mocked_reader.return_value = self.parts_list
            df = bbinput.get_parts(os.path.join(TEST_DIR,
                                                'testfiles/parts.csv'),
                                   self.constructs_df)
            for col in df.columns:
                self.assertListEqual(df[col].to_list(),
                                     self.parts_df[col].to_list())

    def test_next_well(self):
        self.assertEqual(bbinput.next_well([]), 'A1')
        self.assertEqual(bbinput.next_well(['B2', 'A3']), 'A1')
        self.assertEqual(bbinput.next_well(['A1', 'A2', 'A3', 'A4', 'A5',
                                            'A6', 'A7', 'A8', 'A9', 'A10',
                                            'A11', 'A12']), 'B1')
        with self.assertRaises(ValueError):
            bbinput.next_well(self.all_wells)

    def test_next_well_reagent(self):
        self.assertEqual(bbinput.next_well_reagent([]), 'A1')
        self.assertEqual(bbinput.next_well_reagent(['A2', 'A3']), 'A1')
        self.assertEqual(bbinput.next_well_reagent(['A1', 'A2', 'A3', 'A4',
                                                    'A5', 'A6']), 'B1')
        with self.assertRaises(ValueError):
            bbinput.next_well_reagent(self.all_wells_reagent)

    def test_get_digests(self):
        digests, parts = bbinput.get_digests(self.constructs_df, self.parts_df,
                                             self.reagents_wells,
                                             self.constructs_wells,
                                             self.reagents_df)
        for col in digests.columns:
            self.assertListEqual(digests[col].to_list(),
                                 self.digests_df[col].to_list())

            self.assertListEqual(parts['digest_wells'].to_list(),
                                 self.parts_digest_wells)

    def test_create_assembly_dicts(self):
        dict1, dict2, dict3, dict4, dict5 = bbinput.create_assembly_dicts(
                    self.constructs_df, self.parts_df_full, self.digests_df,
                    self.reagents_df)
        self.assertDictEqual(dict1, self.source_to_digest)
        self.assertDictEqual(dict2, self.reagent_to_digest)
        self.assertDictEqual(dict3, self.digest_to_storage)
        self.assertDictEqual(dict4, self.digest_to_construct)
        self.assertDictEqual(dict5, self.reagent_to_construct)

    def test_create_tranformation_dicts(self):
        dict1, dict2, dict3, dict4, df = bbinput.create_tranformation_dicts(
            self.constructs_df)
        self.assertDictEqual(dict1, self.competent_source_to_dest)
        self.assertDictEqual(dict2, self.control_source_to_dest)
        self.assertDictEqual(dict3, self.assembly_source_to_dest)
        self.assertDictEqual(dict4, self.water_to_dest)

        for col in df.columns:
            self.assertListEqual(df[col].to_list(),
                                 self.transform_df[col].to_list())

if __name__ == "__main__":
    unittest.main()
