import os
import csv
import json
import math
import pandas as pd

TEMPLATE_DIR_NAME = 'template'
OUTPUT_DIR_NAME = 'output'
REAGENTS_TUBE_MAX_VOL = 1500
DEFAULT_CONCENTRATION = 500  # 500 ng/uL
PART_AMOUNT = 500
FILL_VOL = 50
NEB_BUFFER_10X_VOL = 5
ENZ_VOL = 1
T4_LIGASE_VOL = 1
T4_LIGASE_VOL_10X = 2
WATER_VOL_LIG = 11
DIGEST_TO_CONS_VOL = 2


def main():
    generator_dir = os.getcwd()
    template_dir_path = os.path.join(generator_dir, TEMPLATE_DIR_NAME)
    template_path = os.path.join(template_dir_path,
                                 'bbassembly10template.py')
    output_path = os.path.join(generator_dir, OUTPUT_DIR_NAME)
    constructs, dest_well_list = get_constructs(
        os.path.join(generator_dir, 'examples/constructs.csv'))
    parts = get_parts(os.path.join(generator_dir, 'examples/parts.csv'),
                      constructs)
    reagents, reagents_well_list = get_reagents_wells(constructs, parts)
    digest_loc, parts_df = get_digests(constructs, parts, reagents_well_list,
                                       dest_well_list, reagents)
    parts_df.to_csv(path_or_buf=os.path.join(generator_dir,
                                             'parts_df.csv'), index=False)
    reagents.to_csv(path_or_buf=os.path.join(generator_dir,
                                             'reagents_df.csv'), index=False)
    digest_loc.to_csv(path_or_buf=os.path.join(generator_dir,
                                               'digests_df.csv'), index=False)
    source_to_digest, reagent_to_digest, digest_to_storage, \
        digest_to_construct, reagent_to_construct = create_assembly_dicts(
                                    constructs, parts, digest_loc, reagents)
    create_protocol(template_path, output_path, source_to_digest,
                    reagent_to_digest, digest_to_storage, digest_to_construct,
                    reagent_to_construct)


def get_constructs(path):
    '''
        Returns list of construct dictionaries from csv file
    '''
    constructs_list = []
    dest_well_list = []
    with open(path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for index, construct in enumerate(csv_reader):
            if index != 0:  # Checks if row is header.
                construct = list(filter(None, construct))
                if not construct[2:]:
                    break
                else:
                    construct_dict = process_construct(construct)
                    construct_df = pd.DataFrame.from_dict(construct_dict)
                    constructs_list.append(construct_df)
                    dest_well_list.append(construct_dict['well'][0])
    merged_constructs_list = pd.concat(constructs_list, ignore_index=True)
    return merged_constructs_list, dest_well_list


def process_construct(construct_entry):
    '''
        Returns construct dictionary from row in csv file
    '''
    construct_dict = {'name': [construct_entry[0]],
                      'well': [construct_entry[1]], 'upstream':
                      [construct_entry[2]], 'downstream':
                      [construct_entry[3]], 'plasmid': [
                                      construct_entry[4]]}
    return construct_dict


def get_parts(path, constructs_list):
    '''
        Returns list of part dictionaries from part csv file.
        Uses constructs_list to record the number of times the part is used
        in the constructs and the roles it plays.
    '''

    parts_list = []
    with open(path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for index, part in enumerate(csv_reader):
            if index != 0:
                part = list(filter(None, part))
                parts_list.append(process_part(part, constructs_list))
    merged_parts_list = pd.concat(parts_list, ignore_index=True)
    return merged_parts_list


def process_part(part, constructs_list):
    '''
        Returns a part dictionary with detailed information.
    '''
    part_dict = {'name': [part[0]], 'well': [part[1]]}
    occ, cons_in = count_part_occurences(constructs_list, part)
    part_dict['occurences'] = occ

    # part_dict['occurences'][2] = number of time part is actually plasmid
    # plasmids cannot be inserted as parts, and vice versa
    if part_dict['occurences'][2] > 0:
        digests = 1
        part_dict['roles'] = [['plasmid']]
    elif part_dict['occurences'][0] > 0:
        if part_dict['occurences'][1] > 0:
            digests = 2
            part_dict['roles'] = [['upstream', 'downstream']]
        else:
            digests = 1
            part_dict['roles'] = [['upstream']]
    elif part_dict['occurences'][1] > 0:
        digests = 1
        part_dict['roles'] = [['downstream']]
    else:
        digests = 0  # part/plasmid not in constructs
        part_dict['roles'] = [[]]

    if len(part) == 2:
        concentration = DEFAULT_CONCENTRATION
        part_vol = 1
    else:
        concentration = int(part[2])
        part_vol = math.ceil(PART_AMOUNT/concentration)
    part_dict['digests'] = [digests]
    part_dict['concentration'] = [concentration]
    part_dict['part_vol'] = [part_vol]
    water_vol = FILL_VOL - part_vol - 2*ENZ_VOL - NEB_BUFFER_10X_VOL
    part_dict['water_vol'] = [water_vol]
    part_vol_tot = part_vol*digests
    part_dict['part_vol_tot'] = [part_vol_tot]
    water_vol_tot = water_vol*digests
    part_dict['water_vol_tot'] = [water_vol_tot]
    part_dict['occurences'] = [part_dict['occurences']]
    part_dict['constructs_in'] = [cons_in]
    part_df = pd.DataFrame.from_dict(part_dict)
    return part_df


def get_reagents_wells(constructs_list, parts):
    '''
        Returns dataframe with rows as reagent names and cols
        as the reagent well and the volume of the reagent required.
    '''
    reagents_well_list = []
    reagents = ['water', 'NEBBuffer10X', 'T4Ligase10X', 'T4Ligase',
                'EcoRI-HF', 'SpeI', 'XbaI', 'PstI']
    reagents_list = []
    no_cons = len(constructs_list)
    no_plasmids = 0
    no_upstream = 0
    no_downstream = 0
    total_water_vol = parts['water_vol_tot'].sum()
    total_digests = parts['digests'].sum()
    for _, roles in parts['roles'].iteritems():
        if 'plasmid' in roles:
            no_plasmids += 1
        if 'upstream' in roles:
            no_upstream += 1
        if 'downstream' in roles:
            no_downstream += 1
    total_water_vol = total_water_vol + no_cons*WATER_VOL_LIG
    total_volumes = [total_water_vol, NEB_BUFFER_10X_VOL*total_digests,
                     T4_LIGASE_VOL_10X*no_cons,
                     T4_LIGASE_VOL*no_cons,
                     ENZ_VOL*(no_upstream + no_plasmids),
                     ENZ_VOL*no_upstream, ENZ_VOL*no_downstream,
                     ENZ_VOL*(no_downstream + no_plasmids),
                     ]
    for i in range(len(reagents)):
        reagents_dict = {}
        reagents_dict['name'] = [reagents[i]]
        new_well = next_well_reagent(reagents_well_list)
        reagents_well_list.append(new_well)
        reagents_dict['well'] = [new_well]
        reagents_dict['total_vol'] = [total_volumes[i]]
        reagents_list.append(pd.DataFrame.from_dict(reagents_dict))
    return pd.concat(reagents_list, ignore_index=True), reagents_well_list


def get_digests(constructs_list, parts, reagents_wells_used, dest_wells_used,
                reagents):
    digests = []
    parts_df = parts.copy()
    parts_df['digest_wells'] = pd.Series([] * len(parts_df.index))
    dest_wells_list = []
    for index, row in parts.iterrows():
        dest_wells = []
        for i in range(int(row['digests'])):
            digest = {}
            role = row['roles'][i]
            digest['name'] = [row['name'] + '-' + role]
            digest['role'] = [role]
            digest['part'] = [row['name']]
            digest['source_well'] = [row['well']]
            dest_well = next_well(dest_wells_used)
            digest['dest_well'] = [dest_well]
            dest_wells_used.append(dest_well)
            reagent_well = next_well_reagent(reagents_wells_used)
            digest['reagent_well'] = [reagent_well]
            if role == 'upstream':
                digest_to_construct = row['constructs_in'][0]
            elif role == 'downstream':
                digest_to_construct = row['constructs_in'][1]
            else:
                digest_to_construct = row['constructs_in'][2]
            cons_wells = []
            for cons_index in digest_to_construct:
                cons_well = constructs_list['well'][int(cons_index)]
                cons_wells.append(cons_well)
            digest['construct_wells'] = [cons_wells]
            reagents_wells_used.append(reagent_well)
            dest_wells.append(dest_well)
            digest_df = pd.DataFrame.from_dict(digest)
            digests.append(digest_df)
        dest_wells_list.append(dest_wells)
    parts_df['digest_wells'] = dest_wells_list
    return pd.concat(digests, ignore_index=True), parts_df


def next_well(wells_used):
    letter = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    well_avail = None
    for i in range(96):
        rowindex = i // 12
        row = letter[rowindex]
        col = (i % 12) + 1
        well = row + str(col)
        if well in wells_used:
            continue
        else:
            well_avail = well
            break
    if not well_avail:
        raise ValueError('No empty wells')
    return well_avail


def next_well_reagent(wells_used):
    letter = ['A', 'B', 'C', 'D']
    well_avail = None
    for i in range(24):
        rowindex = i // 6
        row = letter[rowindex]
        col = (i % 6) + 1
        well = row + str(col)
        if well in wells_used:
            continue
        else:
            well_avail = well
            break
    if not well_avail:
        raise ValueError('No empty wells')
    return well_avail


def count_part_occurences(constructs_list, part):
    # upstream_counts, downstream_counts, plasmid_counts = 0
    counts = [0, 0, 0]
    constructs_in_upstream = []
    constructs_in_downstream = []
    constructs_in_plasmid = []
    # roles = ['upstream', 'downstream', 'plasmid']
    for index, row in constructs_list.iterrows():
        if part[0] in row['upstream']:
            counts[0] += 1
            constructs_in_upstream.append(index)
        if part[0] in row['downstream']:
            counts[1] += 1
            constructs_in_downstream.append(index)
        elif part[0] in row['plasmid']:
            counts[2] += 1
            constructs_in_plasmid.append(index)
    return counts, [constructs_in_upstream, constructs_in_downstream,
                    constructs_in_plasmid]


def create_assembly_dicts(constructs, parts, digests, reagents):
    source_to_digest = {}
    reagent_to_digest = {}
    digest_to_construct = {}
    reagent_to_construct = {}
    digest_to_storage = {}

    # water well
    reagent_to_digest['A1'] = []  # water

    digest_wells = tuple(digests['dest_well'].to_list())
    NEBVols = tuple([int(NEB_BUFFER_10X_VOL)]*len(digests))
    reagent_to_digest['A2'] = [*zip(digest_wells, NEBVols)]

    reagent_to_digest['A5'] = []
    reagent_to_digest['A6'] = []
    reagent_to_digest['B1'] = []
    reagent_to_digest['B2'] = []

    for i, digest in digests.iterrows():
        part_idx = parts[parts['name'] == digest['part']].index.values
        if len(part_idx) > 0:
            idx = part_idx[0]
            if str(digest['source_well']) not in source_to_digest.keys():
                source_to_digest[str(digest['source_well'])] = [
                    (digest['dest_well'], int(parts['part_vol'][idx]))]
            else:
                source_to_digest[str(digest['source_well'])].append((
                        digest['dest_well'], int(parts['part_vol'][idx])))

            reagent_to_digest['A1'].append((digest['dest_well'],
                                            int(parts['water_vol'][idx])))

        if digest['role'] == 'upstream':
            reagent_to_digest['A5'].append((digest['dest_well'], int(ENZ_VOL)))
            reagent_to_digest['A6'].append((digest['dest_well'], int(ENZ_VOL)))
        elif digest['role'] == 'downstream':
            reagent_to_digest['B1'].append((digest['dest_well'], int(ENZ_VOL)))
            reagent_to_digest['B2'].append((digest['dest_well'], int(ENZ_VOL)))
        elif digest['role'] == 'plasmid':
            reagent_to_digest['A5'].append((digest['dest_well'], int(ENZ_VOL)))
            reagent_to_digest['B2'].append((digest['dest_well'], int(ENZ_VOL)))

        storage_vol = FILL_VOL - DIGEST_TO_CONS_VOL
        digest_to_storage[str(digest['dest_well'])] = [(
            str(digest['reagent_well']), storage_vol)]
        if len(digest['construct_wells']) > 1:
            cons_wells = tuple(digest['construct_wells'])
            construct_vols = tuple([DIGEST_TO_CONS_VOL]*len(
                                         digest['construct_wells']))
            digest_to_construct[str(digest['dest_well'])] = [
                             *zip(cons_wells, construct_vols)]
        else:
            digest_to_construct[str(digest['dest_well'])] = [(
                            digest['construct_wells'][0], DIGEST_TO_CONS_VOL)]

    construct_wells = tuple(constructs['well'].to_list())
    reagent_to_construct['A1'] = [*zip(construct_wells, tuple(
                                    [WATER_VOL_LIG]*len(constructs)))]
    reagent_to_construct['A3'] = [*zip(construct_wells, tuple(
                                    [T4_LIGASE_VOL_10X]*len(constructs)))]
    reagent_to_construct['A4'] = [*zip(construct_wells, tuple(
                                    [T4_LIGASE_VOL]*len(constructs)))]
    return source_to_digest, reagent_to_digest, digest_to_storage, \
        digest_to_construct, reagent_to_construct


def create_protocol(template_path, output_path, source_to_digest,
                    reagent_to_digest, digest_to_storage, digest_to_construct,
                    reagent_to_construct):
    with open(template_path) as template_file:
        template_string = template_file.read()
    with open(os.path.join(output_path, 'bb_assembly_protocol.py'),
              "w+") as protocol_file:
        # Paste in plate maps at top of file.
        protocol_file.write('source_to_digest = ' +
                            json.dumps(source_to_digest) + '\n\n')
        protocol_file.write('reagent_to_digest = '
                            + json.dumps(reagent_to_digest) + '\n\n')
        protocol_file.write('digest_to_storage = '
                            + json.dumps(digest_to_storage) + '\n\n')
        protocol_file.write('digest_to_construct = '
                            + json.dumps(digest_to_construct) + '\n\n')
        protocol_file.write('reagent_to_construct = '
                            + json.dumps(reagent_to_construct) + '\n\n')

        # Paste the rest of the protocol.
        protocol_file.write(template_string)


if __name__ == '__main__':
    main()
