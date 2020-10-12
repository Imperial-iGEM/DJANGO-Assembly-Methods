import pandas as pd
import unittest
from unittest.mock import patch
import sys
import os
TEST_DIR = "/home/runner/work/DJANGO-Assembly-Methods/DJANGO-Assembly-Methods/basic_assembly/tests/"
sys.path.append("/home/runner/work/DJANGO-Assembly-Methods/DJANGO-Assembly-Methods/basic_assembly/dna_bot/")
import dnabot_app


class DNABotAppTestCase(unittest.TestCase):
    def setUp(self):
        self.constructs_csv_lists = [['Well', 'Linker 1', 'Part 1', 'Linker 2', 'Part 2', 'Linker 3', 'Part 3', 'Linker 4', 'Part 4', 'Linker 5', 'Part 5'], ['A1', 'LMS', 'dummyBackbone', 'LMP', 'Pro', 'L1', 'RBS', 'L2', 'CDS', 'L3', 'Ter']]
        self.parts_csv_lists = [['Part/linker', 'Well', 'Part concentration (ng/uL)'], ['CDS', 'A1'], ['L1-P', 'A2'], ['L1-S', 'A3'], ['L2-P', 'A4'], ['L2-S', 'A5'], ['L3-P', 'A6'], ['L3-S', 'A7'], ['LMP-P', 'A8'], ['LMP-S', 'A9'], ['LMS-P', 'A10'], ['LMS-S', 'A11'], ['Pro', 'A12'], ['RBS', 'B1'], ['Ter', 'B2'], ['dummyBackbone', 'B3']]
        self.constructs_lists = [pd.DataFrame.from_dict({'prefixes': ['LMS-P', 'LMP-P', 'L1-P', 'L2-P', 'L3-P'], 'parts': ['dummyBackbone', 'Pro', 'RBS', 'CDS', 'Ter'], 'suffixes': ['LMP-S', 'L1-S', 'L2-S', 'L3-S', 'LMS-S']})]
        self.clips_df_1 = pd.DataFrame(data={'prefixes': ['LMS-P', 'LMP-P', 'L1-P', 'L2-P', 'L3-P'], 'parts': ['dummyBackbone', 'Pro', 'RBS', 'CDS', 'Ter'], 'suffixes': ['LMP-S', 'L1-S', 'L2-S', 'L3-S', 'LMS-S'], 'number': [1, 1, 1, 1, 1], 'clip_well': [('A1',), ('B1',), ('C1',), ('D1',), ('E1',)], 'mag_well': [('A7',), ('B7',), ('C7',), ('D7',), ('E7',)]})
        self.clips_df = pd.DataFrame(data={'prefixes': ['LMS-P', 'LMP-P', 'L1-P', 'L2-P', 'L3-P'], 'parts': ['dummyBackbone', 'Pro', 'RBS', 'CDS', 'Ter'], 'suffixes': ['LMP-S', 'L1-S', 'L2-S', 'L3-S', 'LMS-S'], 'number': [1, 1, 1, 1, 1], 'clip_well': [('A1',), ('B1',), ('C1',), ('D1',), ('E1',)], 'mag_well': [('A7',), ('B7',), ('C7',), ('D7',), ('E7',)], 'construct_well': [['A1'], ['A1'], ['A1'], ['A1'], ['A1']]})
        self.clips_dict = {"prefixes_wells": ["A10", "A8", "A2", "A4", "A6"], "prefixes_plates": ["2", "2", "2", "2", "2"], "suffixes_wells": ["A9", "A3", "A5", "A7", "A11"], "suffixes_plates": ["2", "2", "2", "2", "2"], "parts_wells": ["B3", "A12", "B1", "A1", "B2"], "parts_plates": ["2", "2", "2", "2", "2"], "parts_vols": [1, 1, 1, 1, 1], "water_vols": [7.0, 7.0, 7.0, 7.0, 7.0]}
        self.sources_dict = {'CDS': ('A1', '2'), 'L1-P': ('A2', '2'), 'L1-S': ('A3', '2'), 'L2-P': ('A4', '2'), 'L2-S': ('A5', '2'), 'L3-P': ('A6', '2'), 'L3-S': ('A7', '2'), 'LMP-P': ('A8', '2'), 'LMP-S': ('A9', '2'), 'LMS-P': ('A10', '2'), 'LMS-S': ('A11', '2'), 'Pro': ('A12', '2'), 'RBS': ('B1', '2'), 'Ter': ('B2', '2'), 'dummyBackbone': ('B3', '2')}
        self.parts_df_1 = pd.DataFrame(data={'concentration': [200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200], 'name': ['CDS', 'L1-P', 'L1-S', 'L2-P', 'L2-S', 'L3-P', 'L3-S', 'LMP-P', 'LMP-S', 'LMS-P', 'LMS-S', 'Pro', 'RBS', 'Ter', 'dummyBackbone'], 'well': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12', 'B1', 'B2', 'B3'], 'plate': ['2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2']})
        self.parts_df_2 = pd.DataFrame(data={'concentration': [200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200], 'name': ['CDS', 'L1-P', 'L1-S', 'L2-P', 'L2-S', 'L3-P', 'L3-S', 'LMP-P', 'LMP-S', 'LMS-P', 'LMS-S', 'Pro', 'RBS', 'Ter', 'dummyBackbone'], 'well': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12', 'B1', 'B2', 'B3'], 'plate': ['2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2'], 'clip_well': [['D1'], ['C1'], ['B1'], ['D1'], ['C1'], ['E1'], ['D1'], ['B1'], ['A1'], ['A1'], ['E1'], ['B1'], ['C1'], ['E1'], ['A1']], 'mag_well': [['D7'], ['C7'], ['B7'], ['D7'], ['C7'], ['E7'], ['D7'], ['B7'], ['A7'], ['A7'], ['E7'], ['B7'], ['C7'], ['E7'], ['A7']], 'total_vol': [16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16], 'vol_per_clip': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'number': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]})
        self.parts_df = pd.DataFrame(data={'concentration': [200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200], 'name': ['CDS', 'L1-P', 'L1-S', 'L2-P', 'L2-S', 'L3-P', 'L3-S', 'LMP-P', 'LMP-S', 'LMS-P', 'LMS-S', 'Pro', 'RBS', 'Ter', 'dummyBackbone'], 'well': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12', 'B1', 'B2', 'B3'], 'plate': ['2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2'], 'clip_well': [['D1'], ['C1'], ['B1'], ['D1'], ['C1'], ['E1'], ['D1'], ['B1'], ['A1'], ['A1'], ['E1'], ['B1'], ['C1'], ['E1'], ['A1']], 'mag_well': [['D7'], ['C7'], ['B7'], ['D7'], ['C7'], ['E7'], ['D7'], ['B7'], ['A7'], ['A7'], ['E7'], ['B7'], ['C7'], ['E7'], ['A7']], 'total_vol': [16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16], 'vol_per_clip': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'number': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'construct_well': [['A1'], ['A1'], ['A1'], ['A1'], ['A1'], ['A1'], ['A1'], ['A1'], ['A1'], ['A1'], ['A1'], ['A1'], ['A1'], ['A1'], ['A1']]})
        self.final_assembly_dict = {"A1": ["A7", "B7", "C7", "D7", "E7"]}
        self.final_assembly_tipracks = 1
        self.spotting_tuples = [(('A1',), ('A1',), (5,))]

    def tearDown(self):
        pass

    def test_generate_constructs_list(self):
        construct_dir = os.path.join(
            TEST_DIR, 'testfiles/basic_constructs.csv')
        with patch('csv.reader') as mocked_reader:
            mocked_reader.return_value = self.constructs_csv_lists
            constructs = dnabot_app.generate_constructs_list(construct_dir)
            self.assertEqual(len(constructs), len(self.constructs_lists))
            for i in range(len(constructs)):
                for col in constructs[i].columns:
                    self.assertListEqual(
                        constructs[i][col].to_list(),
                        self.constructs_lists[i][col].to_list())

    def test_generate_clips_df(self):
        clips = dnabot_app.generate_clips_df(self.constructs_lists)
        for col in clips.columns:
            self.assertListEqual(clips[col].to_list(),
                                 self.clips_df_1[col].to_list())

    def test_generate_sources_dict(self):
        source_dir = [os.path.join(
            TEST_DIR, 'testfiles/basic_parts_linkers.csv')]
        with patch('csv.reader') as mocked_reader:
            mocked_reader.return_value = self.parts_csv_lists
            source_dict, part = dnabot_app.generate_sources_dict(source_dir)
            self.assertDictEqual(source_dict, self.sources_dict)
            for col in part.columns:
                self.assertListEqual(part[col].to_list(),
                                     self.parts_df_1[col].to_list())

    def test_fill_parts_df(self):
        part = dnabot_app.fill_parts_df(self.clips_df_1, self.parts_df_1)
        for col in part.columns:
            self.assertListEqual(part[col].to_list(),
                                 self.parts_df_2[col].to_list())

    def test_generate_clips_dict(self):
        clips = dnabot_app.generate_clips_dict(
            self.clips_df_1, self.sources_dict, self.parts_df_2)
        self.assertDictEqual(clips, self.clips_dict)

    def test_generate_final_assembly_dict(self):
        final_assembly_dict, clips_df, parts_df = \
            dnabot_app.generate_final_assembly_dict(
                self.constructs_lists, self.clips_df_1, self.parts_df_2)
        self.assertDictEqual(final_assembly_dict, self.final_assembly_dict)
        for col in clips_df.columns:
            self.assertListEqual(
                clips_df[col].to_list(), self.clips_df[col].to_list())
        for col in parts_df.columns:
            self.assertListEqual(
                parts_df[col].to_list(), self.parts_df[col].to_list())

    def test_final_assembly_tipracks(self):
        final_assembly_tipracks = dnabot_app.calculate_final_assembly_tipracks(
            self.final_assembly_dict)
        self.assertEqual(final_assembly_tipracks, self.final_assembly_tipracks)

    def test_generate_spotting_tuples(self):
        SPOTTING_VOLS_DICT = {2: 5, 3: 5, 4: 5, 5: 5, 6: 5, 7: 5}
        spotting_tuples = dnabot_app.generate_spotting_tuples(
            self.constructs_lists, SPOTTING_VOLS_DICT)
        self.assertListEqual(spotting_tuples, self.spotting_tuples)


if __name__ == "__main__":
    unittest.main()
