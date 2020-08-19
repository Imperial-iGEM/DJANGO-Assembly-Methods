import pandas as pd
import numpy as np
import unittest
from unittest.mock import patch
import csv
import sys
#import os
#parentdir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, '/biobricks10'))
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
                            pd.DataFrame(data={'name': ['NEBBuffer10X'],
                                               'well': ['A2'], 'total_vol':
                                               [30]}),
                            pd.DataFrame(data={'name': ['T4Ligase10X'], 'well':
                                               ['A3'], 'total_vol': [6]}),
                            pd.DataFrame(data={'name': ['T4Ligase'], 'well':
                                               ['A4'], 'total_vol': [3]}),
                            pd.DataFrame(data={'name': ['EcoRI-HF'], 'well':
                                               ['A5'], 'total_vol': [3]}),
                            pd.DataFrame(data={'name': ['SpeI'], 'well':
                                               ['A6'], 'total_vol': [2]}),
                            pd.DataFrame(data={'name': ['XbaI'], 'well':
                                               ['B1'], 'total_vol': [3]}),
                            pd.DataFrame(data={'name': ['PstI'], 'well':
                                               ['B2'], 'total_vol': [4]})]

        self.reagents_df = pd.concat(self.reagent_dfs, ignore_index=True)
        self.reagents_wells = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'B1', 'B2']
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
                                              'reagent_well': ['B3'],
                                              'construct_wells':
                                              [['A1', 'A2']]}),
                           pd.DataFrame(data={'name': ['BBa_C0040-downstream'],
                                              'role': ['downstream'], 'part':
                                              ['BBa_C0040'], 'source_well':
                                              ['A2'], 'dest_well': ['A5'],
                                              'reagent_well': ['B4'],
                                              'construct_wells': [['A1']]}),
                           pd.DataFrame(data={'name': ['BBa_pSB1AK3-plasmid'],
                                              'role': ['plasmid'], 'part':
                                              ['BBa_pSB1AK3'], 'source_well':
                                              ['A3'], 'dest_well': ['A6'],
                                              'reagent_well': ['B5'],
                                              'construct_wells':
                                              [['A1', 'A2', 'A3']]}),
                           pd.DataFrame(data={'name': ['BBa_C0012-upstream'],
                                              'role': ['upstream'], 'part':
                                              ['BBa_C0012'], 'source_well':
                                              ['A4'], 'dest_well': ['A7'],
                                              'reagent_well': ['B6'],
                                              'construct_wells': [['A3']]}),
                           pd.DataFrame(data={'name': ['BBa_C0012-downstream'],
                                              'role': ['downstream'], 'part':
                                              ['BBa_C0012'], 'source_well':
                                              ['A4'], 'dest_well': ['A8'],
                                              'reagent_well': ['C1'],
                                              'construct_wells': [['A2']]}),
                           pd.DataFrame(data={'name': ['BBa_B0015-downstream'],
                                              'role': ['downstream'], 'part':
                                              ['BBa_B0015'], 'source_well':
                                              ['A5'], 'dest_well': ['A9'],
                                              'reagent_well': ['C2'],
                                              'construct_wells': [['A3']]})]

        self.digests_df = pd.concat(self.digest_dfs, ignore_index=True)

        self.source_to_digest = {'A1': [('A4', 1)], 'A2': [('A5', 1)], 'A3':
                                 [('A6', 1)], 'A4': [('A7', 1), ('A8', 1)],
                                 'A5': [('A9', 1)]}

        self.reagent_to_digest = {'A1': [('A4', 42), ('A5', 42), ('A6', 42),
                                         ('A7', 42), ('A8', 42), ('A9', 42)],
                                  'A2': [('A4', 5), ('A5', 5), ('A6', 5),
                                         ('A7', 5), ('A8', 5), ('A9', 5)],
                                  'A5': [('A4', 1), ('A6', 1), ('A7', 1)],
                                  'A6': [('A4', 1), ('A7', 1)],
                                  'B1': [('A5', 1), ('A8', 1), ('A9', 1)],
                                  'B2': [('A5', 1), ('A6', 1), ('A8', 1),
                                         ('A9', 1)]}

        self.digest_to_storage = {'A4': [('B3', 48)], 'A5': [('B4', 48)],
                                  'A6': [('B5', 48)], 'A7': [('B6', 48)],
                                  'A8': [('C1', 48)], 'A9': [('C2', 48)]}

        self.digest_to_construct = {'A4': [('A1', 2), ('A2', 2)],
                                    'A5': [('A1', 2)],
                                    'A6': [('A1', 2), ('A2', 2), ('A3', 2)],
                                    'A7': [('A3', 2)], 'A8': [('A2', 2)],
                                    'A9': [('A3', 2)]}

        self.reagent_to_construct = {'A1': [('A1', 11), ('A2', 11),
                                            ('A3', 11)],
                                     'A3': [('A1', 2), ('A2', 2), ('A3', 2)],
                                     'A4': [('A1', 1), ('A2', 1), ('A3', 1)]}

    def tearDown(self):
        pass

    def test_process_construct(self):
        for i in range(len(self.constructs_list)-1):
            construct = self.constructs_list[i+1]
            processed = biobricks10.bbinput.process_construct(construct)
            self.assertDictEqual(processed, self.construct_dicts[i])

    @patch('bbinput.process_construct',
           side_effect=side_effect_functions.process_cons)
    def test_get_constructs(self, mock_process_construct):
        with patch('csv.reader') as mocked_reader:
            mocked_reader.return_value = self.constructs_list
            cons_df, dest_wells = biobricks10.bbinput.get_constructs(
                                'testfiles/constructs.csv')
            self.assertListEqual(dest_wells, self.construct_wells)
            for col in ['name', 'well', 'upstream', 'downstream', 'plasmid']:
                self.assertListEqual(cons_df[col].to_list(),
                                     self.constructs_df[col].to_list())

    def test_count_part_occurrences(self):
        for index, part in enumerate(self.parts_list):
            if index != 0:
                self.assertListEqual(biobricks10.bbinput.count_part_occurences(
                            self.constructs_df, part)[0], self.occ[index-1])
                self.assertListEqual(biobricks10.bbinput.count_part_occurences(
                            self.constructs_df, part)[1], self.cons_in[index-1]
                                     )

    def test_process_part(self):
        for index, part in enumerate(self.parts_list):
            if index != 0:
                df = biobricks10.bbinput.process_part(part, self.constructs_df)
                part_df = self.part_dfs[index - 1]
                for col in df.columns:
                    self.assertListEqual(df[col].to_list(),
                                         part_df[col].to_list())

    @patch('bbinput.process_part',
           side_effect=side_effect_functions.process_part)
    def test_get_parts(self, mock_process_part):
        with patch('csv.reader') as mocked_reader:
            mocked_reader.return_value = self.parts_list
            df = biobricks10.bbinput.get_parts(
                'testfiles/parts.csv', self.constructs_df)
            for col in df.columns:
                self.assertListEqual(df[col].to_list(),
                                     self.parts_df[col].to_list())

    def test_next_well(self):
        self.assertEqual(biobricks10.bbinput.next_well([]), 'A1')
        self.assertEqual(biobricks10.bbinput.next_well(['B2', 'A3']), 'A1')
        self.assertEqual(biobricks10.bbinput.next_well(['A1', 'A2', 'A3', 'A4', 'A5',
                                            'A6', 'A7', 'A8', 'A9', 'A10',
                                            'A11', 'A12']), 'B1')
        with self.assertRaises(ValueError):
            biobricks10.bbinput.next_well(self.all_wells)

    def test_next_well_reagent(self):
        self.assertEqual(biobricks10.bbinput.next_well_reagent([]), 'A1')
        self.assertEqual(biobricks10.bbinput.next_well_reagent(['A2', 'A3']), 'A1')
        self.assertEqual(biobricks10.bbinput.next_well_reagent(['A1', 'A2', 'A3', 'A4',
                                                    'A5', 'A6']), 'B1')
        with self.assertRaises(ValueError):
            biobricks10.bbinput.next_well_reagent(self.all_wells_reagent)

    def test_get_digests(self):
        digests, parts = biobricks10.bbinput.get_digests(self.constructs_df, self.parts_df,
                                             self.reagents_wells,
                                             self.constructs_wells,
                                             self.reagents_df)
        for col in digests.columns:
            self.assertListEqual(digests[col].to_list(),
                                 self.digests_df[col].to_list())

            self.assertListEqual(parts['digest_wells'].to_list(),
                                 self.parts_digest_wells)

    def test_create_assembly_dicts(self):
        dict1, dict2, dict3, dict4, dict5 = biobricks10.bbinput.create_assembly_dicts(
                    self.constructs_df, self.parts_df_full, self.digests_df,
                    self.reagents_df)
        self.assertDictEqual(dict1, self.source_to_digest)
        self.assertDictEqual(dict2, self.reagent_to_digest)
        self.assertDictEqual(dict3, self.digest_to_storage)
        self.assertDictEqual(dict4, self.digest_to_construct)
        self.assertDictEqual(dict5, self.reagent_to_construct)


if __name__ == "__main__":
    unittest.main()
