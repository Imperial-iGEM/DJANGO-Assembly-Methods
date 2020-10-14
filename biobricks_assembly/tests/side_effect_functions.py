import pandas as pd
import numpy as np
import sys
import os
sys.path.append("/home/runner/work/DJANGO-Assembly-Methods/DJANGO-Assembly-Methods/biobricks_assembly/biobricks10/")
import bbinput

constructs_list = [['Construct', 'Well', 'upstream', 'downstream', 'plasmid'],
                   ['construct1', 'A1', 'BBa_B0034', 'BBa_C0040', 'BBa_pSB1AK3'
                    ],
                   ['construct2', 'A2', 'BBa_B0034', 'BBa_C0012', 'BBa_pSB1AK3'
                    ],
                   ['construct3', 'A3', 'BBa_C0012', 'BBa_B0015', 'BBa_pSB1AK3'
                    ]]

construct_dicts = [{'name': ['construct1'], 'well': ['A1'], 'upstream':
                    ['BBa_B0034'], 'downstream': ['BBa_C0040'], 'plasmid':
                    ['BBa_pSB1AK3']},
                   {'name': ['construct2'], 'well': ['A2'], 'upstream':
                    ['BBa_B0034'], 'downstream': ['BBa_C0012'], 'plasmid':
                    ['BBa_pSB1AK3']},
                   {'name': ['construct3'], 'well': ['A3'], 'upstream':
                    ['BBa_C0012'], 'downstream': ['BBa_B0015'], 'plasmid':
                    ['BBa_pSB1AK3']}]

parts_list = [['Part', 'Well', 'Part concentration'],
              ['BBa_B0034', 'A1', '500'], ['BBa_C0040', 'A2', '500'],
              ['BBa_pSB1AK3', 'A3', '500'], ['BBa_C0012', 'A4', '500'],
              ['BBa_B0015', 'A5', ]]

part_dfs = [pd.DataFrame(data={'name': ['BBa_B0034'], 'well': ['A1'],
                               'occurences': [[2, 0, 0]], 'roles':
                               [['upstream']], 'digests': [1], 'concentration':
                               [500], 'part_vol': [1], 'water_vol': [42],
                               'part_vol_tot': [1], 'water_vol_tot': [42],
                               'constructs_in': [[[0, 1], [], []]], 'plate': ['2']}),
            pd.DataFrame(data={'name': ['BBa_C0040'], 'well': ['A2'],
                               'occurences': [[0, 1, 0]], 'roles':
                               [['downstream']], 'digests': [1],
                               'concentration': [500], 'part_vol': [1],
                               'water_vol': [42], 'part_vol_tot': [1],
                               'water_vol_tot': [42], 'constructs_in':
                               [[[], [0], []]], 'plate': ['2']}),
            pd.DataFrame(data={'name': ['BBa_pSB1AK3'], 'well': ['A3'],
                               'occurences': [[0, 0, 3]], 'roles':
                               [['plasmid']], 'digests': [1], 'concentration':
                               [500], 'part_vol': [1], 'water_vol': [42],
                               'part_vol_tot': [1], 'water_vol_tot': [42],
                               'constructs_in': [[[], [], [0, 1, 2]]], 'plate': ['2']}),
            pd.DataFrame(data={'name': ['BBa_C0012'], 'well': ['A4'],
                               'occurences': [[1, 1, 0]], 'roles':
                               [['upstream', 'downstream']], 'digests': [2],
                               'concentration': [500], 'part_vol': [1],
                               'water_vol': [42], 'part_vol_tot': [2],
                               'water_vol_tot': [84], 'constructs_in':
                               [[[2], [1], []]], 'plate': ['2']}),
            pd.DataFrame(data={'name': ['BBa_B0015'], 'well': ['A5'],
                               'occurences': [[0, 1, 0]], 'roles':
                               [['downstream']], 'digests': [1],
                               'concentration': [500], 'part_vol': [1],
                               'water_vol': [42], 'part_vol_tot': [1],
                               'water_vol_tot': [42], 'constructs_in':
                               [[[], [2], []]], 'plate': ['2']})]


def process_cons(construct):
    success_mock = 0
    for i in range(len(construct_dicts)):
        if construct == constructs_list[i + 1]:
            success_mock = 1
            return construct_dicts[i]
            break
    if success_mock == 0:
        print('Unable to mock. Using actual function')
        return bbinput.process_construct(construct)


def process_part(part, constructs_df, plate):
    success_mock = 0
    for i in range(len(part_dfs)):
        if part == parts_list[i + 1]:
            success_mock = 1
            return part_dfs[i]
            break
    if success_mock == 0:
        print('Unable to mock. Using actual function')
        return bbinput.process_part(part, constructs_df, plate)

        
