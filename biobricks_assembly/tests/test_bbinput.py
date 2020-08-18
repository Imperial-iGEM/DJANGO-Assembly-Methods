import sys
import pytest
import pandas as pd
import os
import numpy as np
from pandas.util import testing as tm
newpath = os.path.join(os.pardir, 'biobricks10')
sys.path.append(newpath)
import bbinput


constructs_file = [
    ['Construct', 'Well', 'upstream', 'downstream', 'plasmid'],
    ['construct1', 'A1', 'BBa_B0034', 'BBa_C0040', 'BBa_pSB1AK3'],
    ['construct2', 'A2', 'BBa_B0034', 'BBa_C0012', 'BBa_pSB1AK3'],
    ['construct3', 'A3', 'BBa_C0012', 'BBa_B0015', 'BBa_pSB1AK3']]

parts_file = [
    ['Part', 'Well', 'Part concentration'],
    ['BBa_B0034', 'A1', '500'],
    ['BBa_C0040', 'A2', '500'],
    ['BBa_pSB1AK3', 'A3', '500'],
    ['BBa_C0012', 'A4', '500'],
    ['BBa_B0015', 'A5', ]]

part_dfs = [pd.DataFrame(data={'name': ['BBa_B0034'], 'well': ['A1'],
                               'occurences': [[2, 0, 0]], 'roles':
                               [['upstream']], 'digests': [1], 'concentration':
                               [500], 'part_vol': [1], 'water_vol': [42],
                               'part_vol_tot': [1], 'water_vol_tot': [42],
                               'constructs_in': [[[0, 1], [], []]]}),
            pd.DataFrame(data={'name': ['BBa_C0040'], 'well': ['A2'],
                               'occurences': [[0, 1, 0]], 'roles':
                               [['downstream']], 'digests': [1],
                               'concentration': [500], 'part_vol': [1],
                               'water_vol': [42], 'part_vol_tot': [1],
                               'water_vol_tot': [42], 'constructs_in':
                               [[[], [0], []]]}),
            pd.DataFrame(data={'name': ['BBa_pSB1AK3'], 'well': ['A3'],
                               'occurences': [[0, 0, 3]], 'roles':
                               [['plasmid']], 'digests': [1], 'concentration':
                               [500], 'part_vol': [1], 'water_vol': [42],
                               'part_vol_tot': [1], 'water_vol_tot': [42],
                               'constructs_in': [[[], [], [0, 1, 2]]]}),
            pd.DataFrame(data={'name': ['BBa_C0012'], 'well': ['A4'],
                               'occurences': [[1, 1, 0]], 'roles':
                               [['upstream', 'downstream']], 'digests': [2],
                               'concentration': [500], 'part_vol': [1],
                               'water_vol': [42], 'part_vol_tot': [2],
                               'water_vol_tot': [84], 'constructs_in':
                               [[[2], [1], []]]}),
            pd.DataFrame(data={'name': ['BBa_B0015'], 'well': ['A5'],
                               'occurences': [[0, 1, 0]], 'roles':
                               [['downstream']], 'digests': [1],
                               'concentration': [500], 'part_vol': [1],
                               'water_vol': [42], 'part_vol_tot': [1],
                               'water_vol_tot': [42], 'constructs_in':
                               [[[], [2], []]]})]

parts_df = pd.concat(part_dfs, ignore_index=True)
constructs_df = pd.DataFrame(
                np.array([constructs_file[1], constructs_file[2],
                          constructs_file[3]]),
                columns=['name', 'well', 'upstream', 'downstream', 'plasmid'])

reagent_dfs = [pd.DataFrame(data={'name': ['water'], 'well': ['A1'],
                                  'total_vol': [285]}),
               pd.DataFrame(data={'name': ['NEBBuffer10X'], 'well': ['A2'],
                                  'total_vol': [30]}),
               pd.DataFrame(data={'name': ['T4Ligase10X'], 'well': ['A3'],
                                  'total_vol': [6]}),
               pd.DataFrame(data={'name': ['T4Ligase'], 'well': ['A4'],
                                  'total_vol': [3]}),
               pd.DataFrame(data={'name': ['EcoRI-HF'], 'well': ['A5'],
                                  'total_vol': [3]}),
               pd.DataFrame(data={'name': ['SpeI'], 'well': ['A6'],
                                  'total_vol': [2]}),
               pd.DataFrame(data={'name': ['XbaI'], 'well': ['B1'],
                                  'total_vol': [3]}),
               pd.DataFrame(data={'name': ['PstI'], 'well': ['B2'],
                                  'total_vol': [4]})]

reagents_df = pd.concat(reagent_dfs, ignore_index=True)
reagents_wells = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'B1', 'B2']
constructs_wells = ['A1', 'A2', 'A3']

parts_digest_wells = [['A4'], ['A5'], ['A6'], ['A7', 'A8'], ['A9']]
parts_df_full = parts_df.copy()
parts_df_full['digest_wells'] = [['A4'], ['A5'], ['A6'], ['A7', 'A8'], ['A9']]

digest_dfs = [pd.DataFrame(data={'name': ['BBa_B0034-upstream'], 'role':
                                 ['upstream'], 'part': ['BBa_B0034'],
                                 'source_well': ['A1'], 'dest_well': ['A4'],
                                 'reagent_well': ['B3'], 'construct_wells':
                                 [['A1', 'A2']]}),
              pd.DataFrame(data={'name': ['BBa_C0040-downstream'], 'role':
                                 ['downstream'], 'part': ['BBa_C0040'],
                                 'source_well': ['A2'], 'dest_well': ['A5'],
                                 'reagent_well': ['B4'], 'construct_wells':
                                 [['A1']]}),
              pd.DataFrame(data={'name': ['BBa_pSB1AK3-plasmid'], 'role':
                                 ['plasmid'], 'part': ['BBa_pSB1AK3'],
                                 'source_well': ['A3'], 'dest_well': ['A6'],
                                 'reagent_well': ['B5'], 'construct_wells':
                                 [['A1', 'A2', 'A3']]}),
              pd.DataFrame(data={'name': ['BBa_C0012-upstream'], 'role':
                                 ['upstream'], 'part': ['BBa_C0012'],
                                 'source_well': ['A4'], 'dest_well': ['A7'],
                                 'reagent_well': ['B6'], 'construct_wells':
                                 [['A3']]}),
              pd.DataFrame(data={'name': ['BBa_C0012-downstream'], 'role':
                                 ['downstream'], 'part': ['BBa_C0012'],
                                 'source_well': ['A4'], 'dest_well': ['A8'],
                                 'reagent_well': ['C1'], 'construct_wells':
                                 [['A2']]}),
              pd.DataFrame(data={'name': ['BBa_B0015-downstream'], 'role':
                                 ['downstream'], 'part': ['BBa_B0015'],
                                 'source_well': ['A5'], 'dest_well': ['A9'],
                                 'reagent_well': ['C2'], 'construct_wells':
                                 [['A3']]})]
digests_df = pd.concat(digest_dfs, ignore_index=True)

source_to_digest = {'A1': [('A4', 1)], 'A2': [('A5', 1)], 'A3': [('A6', 1)],
                    'A4': [('A7', 1), ('A8', 1)], 'A5': [('A9', 1)]}

reagent_to_digest = {'A1': [('A4', 42), ('A5', 42), ('A6', 42), ('A7', 42),
                            ('A8', 42), ('A9', 42)],
                     'A2': [('A4', 5), ('A5', 5), ('A6', 5), ('A7', 5),
                            ('A8', 5), ('A9', 5)],
                     'A5': [('A4', 1), ('A6', 1), ('A7', 1)],
                     'A6': [('A4', 1), ('A7', 1)],
                     'B1': [('A5', 1), ('A8', 1), ('A9', 1)],
                     'B2': [('A5', 1), ('A6', 1), ('A8', 1), ('A9', 1)]}

digest_to_storage = {'A4': [('B3', 48)], 'A5': [('B4', 48)],
                     'A6': [('B5', 48)], 'A7': [('B6', 48)],
                     'A8': [('C1', 48)], 'A9': [('C2', 48)]}

digest_to_construct = {'A4': [('A1', 2), ('A2', 2)], 'A5': [('A1', 2)],
                       'A6': [('A1', 2), ('A2', 2), ('A3', 2)],
                       'A7': [('A3', 2)], 'A8': [('A2', 2)], 'A9': [('A3', 2)]}

reagent_to_construct = {'A1': [('A1', 11), ('A2', 11), ('A3', 11)],
                        'A3': [('A1', 2), ('A2', 2), ('A3', 2)],
                        'A4': [('A1', 1), ('A2', 1), ('A3', 1)]}


@pytest.mark.parametrize('construct, result',
                         [
                            (constructs_file[1], {'name': ['construct1'],
                                                  'well': ['A1'], 'upstream':
                                                  ['BBa_B0034'], 'downstream':
                                                  ['BBa_C0040'], 'plasmid':
                                                  ['BBa_pSB1AK3']}),
                            (constructs_file[2], {'name': ['construct2'],
                                                  'well': ['A2'], 'upstream':
                                                  ['BBa_B0034'], 'downstream':
                                                  ['BBa_C0012'], 'plasmid':
                                                  ['BBa_pSB1AK3']}),
                            (constructs_file[3], {'name': ['construct3'],
                                                  'well': ['A3'], 'upstream':
                                                  ['BBa_C0012'], 'downstream':
                                                  ['BBa_B0015'], 'plasmid':
                                                  ['BBa_pSB1AK3']}),
                         ])
def test_process_construct(construct, result):
    assert bbinput.process_construct(construct) == result


def test_get_constructs():
    df, dest_wells = bbinput.get_constructs(os.path.join(newpath,
                                            'examples/constructs.csv'))
    tm.assert_frame_equal(df, constructs_df)

    assert dest_wells == constructs_wells


@pytest.mark.parametrize('part, result, cons_in',
                         [
                            (parts_file[1], [2, 0, 0], [[0, 1], [], []]),
                            (parts_file[2], [0, 1, 0], [[], [0], []]),
                            (parts_file[3], [0, 0, 3], [[], [], [0, 1, 2]]),
                            (parts_file[4], [1, 1, 0], [[2], [1], []]),
                            (parts_file[5], [0, 1, 0], [[], [2], []])
                         ]
                         )
def test_count_part_occurences(part, result, cons_in):
    assert bbinput.count_part_occurences(constructs_df, part)[0] == result
    assert bbinput.count_part_occurences(constructs_df, part)[1] == cons_in


@pytest.mark.parametrize('part, result',
                         [
                            (parts_file[1], part_dfs[0]),
                            (parts_file[2], part_dfs[1]),
                            (parts_file[3], part_dfs[2]),
                            (parts_file[4], part_dfs[3]),
                            (parts_file[5], part_dfs[4])
                         ]
                         )
def test_process_part(part, result):
    df = bbinput.process_part(part, constructs_df)
    tm.assert_frame_equal(df, result)


def test_get_parts():
    df = bbinput.get_parts(os.path.join(newpath,
                                        'examples/parts.csv'), constructs_df)
    tm.assert_frame_equal(df, parts_df)


@pytest.mark.parametrize('wells, result',
                         [
                             (['A1'], 'A2'),
                             ([], 'A1'),
                             (['F1', 'A1', 'A2', 'A3'], 'A4')
                         ]
                         )
def test_next_well(wells, result):
    assert bbinput.next_well(wells) == result


@pytest.mark.parametrize('wells, result',
                         [
                             (['A1'], 'A2'),
                             ([], 'A1'),
                             (['B1', 'A1', 'A2', 'A3'], 'A4')
                         ]
                         )
def test_next_well_reagent(wells, result):
    assert bbinput.next_well_reagent(wells) == result


def test_get_reagents_wells():
    df, wells = bbinput.get_reagents_wells(constructs_df, parts_df)
    assert wells == reagents_wells
    tm.assert_frame_equal(df, reagents_df)


def test_get_digests():
    digests, parts = bbinput.get_digests(constructs_df, parts_df,
                                         reagents_wells, constructs_wells,
                                         reagents_df)
    tm.assert_frame_equal(digests, digests_df)
    assert parts['digest_wells'].to_list() == parts_digest_wells


def test_create_assembly_dicts():
    dict1, dict2, dict3, dict4, dict5 = bbinput.create_assembly_dicts(
                 constructs_df, parts_df_full, digests_df, reagents_df)

    assert dict1 == source_to_digest
    assert dict2 == reagent_to_digest
    assert dict3 == digest_to_storage
    assert dict4 == digest_to_construct
    assert dict5 == reagent_to_construct
