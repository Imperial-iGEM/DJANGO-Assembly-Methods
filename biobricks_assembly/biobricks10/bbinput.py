import os
import csv
import json
import math
import pandas as pd

# labware dictionary - filled in by front end
labware_dict = {'p10_mount': 'right', 'p300_mount': 'left',
                'p10_type': 'p10_single', 'p300_type': 'p300_single',
                'well_plate': 'biorad_96_wellplate_200ul_pcr',
                'tube_rack': 'opentrons_24_tuberack_nest_1.5ml_snapcap',
                'soc_plate': 'usascientific_96_wellplate_2.4ml_deep',
                'transformation_plate': 'corning_96_wellplate_360ul_flat'}

TEMPLATE_DIR_NAME = 'template'
OUTPUT_DIR_NAME = 'output'

# Integer constants
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
DNA_TRANS_VOL = 1
CELL_TRANS_VOL = 50
COMPETENT_WELL_MAX_VOL = 200


def biobricks(output_folder, construct_path, part_path, thermocycle=True,
              p10_mount='right', p300_mount='left', p10_type='p10_single',
              p300_type='p300_single',
              well_plate='biorad_96_wellplate_200ul_pcr',
              tube_rack='opentrons_24_tuberack_nest_1.5ml_snapcap',
              soc_plate='usascientific_96_wellplate_2.4ml_deep',
              transformation_plate='corning_96_wellplate_360ul_flat'):
    '''
        Main function, creates scripts and metainformation
        Can take specific args or just **labware_dict for all labware
        Args:
            output_folder: the full file path of the intended output folder
            for files generated
            construct_path: a one element list with the full path of the
            construct csv
            part_path: a list of full paths to part csv(s) (one or more)
            thermocyle: True or False, indicating whether the user has
            and would like to use the Opentrons Thermocycler
            see labware_dict for rest of arguments
    '''

    full_output_path = output_folder

    # In case construct path is list: can only have one path
    if type(construct_path) == list:
        construct_path = construct_path[0]

    generator_dir = os.getcwd()
    '''
        Ensure that template directories are correct.
        Important for running this script through the front end.
    '''
    if os.path.split(generator_dir)[1] == 'biobricks10':
        template_dir_path = os.path.join(generator_dir, TEMPLATE_DIR_NAME)
    elif os.path.split(generator_dir)[1] == 'biobricks_assembly':
        template_dir_path = os.path.join(
            generator_dir, 'biobricks10', TEMPLATE_DIR_NAME)
    else:
        template_dir_path = os.path.join(
            generator_dir, 'biobricks_assembly/biobricks10', TEMPLATE_DIR_NAME)
    assembly_template_path = os.path.join(template_dir_path,
                                          'bbassembly10template.py')
    transformation_template_path = os.path.join(template_dir_path,
                                                'bbtransformationtemplate.py')
    try:
        # Creates constructs, parts, reagents, and digest dataframes
        constructs, dest_well_list = get_constructs(construct_path)
        parts = get_parts(part_path, constructs)
        reagents, reagents_well_list, mm_df = get_reagents_wells(
            constructs, parts)
        digest_loc, parts_df = get_digests(
            constructs, parts, reagents_well_list,
            dest_well_list, reagents)

        # Creates assembly dictionaries to be used in assembly protocol
        source_to_digest, reagent_to_digest, digest_to_storage, \
            digest_to_construct, reagent_to_construct = create_assembly_dicts(
                                        constructs, parts, digest_loc, reagents)

        # Creates and saves assembly protocol
        assembly_path = create_assembly_protocol(
            assembly_template_path, full_output_path, source_to_digest,
            reagent_to_digest, digest_to_storage, digest_to_construct,
            reagent_to_construct, p10_mount=p10_mount, p10_type=p10_type,
            well_plate_type=well_plate, tube_rack_type=tube_rack,
            thermocycle=thermocycle)
        output_paths = []
        output_paths.append(assembly_path)

        # Creates transformation dictionaries to be used in transformation
        # protocol
        competent_source_to_dest, control_source_to_dest, \
            assembly_source_to_dest, water_source_to_dest, transform_df \
            = create_tranformation_dicts(constructs, water_well='A1',
                                         controls_per_cons=False)

        # Creates and saves transformation protocol
        transform_path = create_transformation_protocol(
            transformation_template_path, full_output_path,
            competent_source_to_dest,
            control_source_to_dest, assembly_source_to_dest,
            water_source_to_dest,
            p10_mount=p10_mount, p300_mount=p300_mount, p10_type=p10_type,
            p300_type=p300_type, well_plate_type=well_plate,
            transformation_plate_type=transformation_plate,
            tube_rack_type=tube_rack, soc_plate_type=soc_plate)
        output_paths.append(transform_path)
        labwareDf = pd.DataFrame(
            data={'name': list(labware_dict.keys()),
                  'definition': list(labware_dict.values())})

        # Saves dataframes in metainformation csv
        dfs_to_csv(
            os.path.join(full_output_path, 'bb_metainformation.csv'),
            index=False, PARTS_INFO=parts_df, REAGENTS=reagents,
            MASTER_MIX=mm_df, DIGESTS=digest_loc, CONSTRUCTS=constructs,
            LABWARE=labwareDf)
        output_paths.append(
            os.path.join(full_output_path, 'bb_metainformation.csv'))

    except Exception as e:
        # Handles error and writes to file
        output_paths = []
        error_path = os.path.join(full_output_path, 'BioBricks_error.txt')
        print("Exception: error_path", error_path)
        with open(error_path) as f:
            f.write("Failed to generate BioBricks scripts: {}\n".format(str(e)))
        output_paths.append(error_path)
    finally:
        return output_paths


def get_constructs(path):
    '''
        Returns construct dataframe from constructs csv
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
        Used in get_constructs()
    '''
    construct_dict = {'name': [construct_entry[0]],
                      'well': [construct_entry[1]], 'upstream':
                      [construct_entry[2]], 'downstream':
                      [construct_entry[3]], 'plasmid': [
                                      construct_entry[4]]}
    return construct_dict


def get_parts(paths, constructs_list):
    '''
        Returns a dataframe of parts from part csv file.
        Uses constructs_list to record the number of times the part is used
        in the constructs and the roles it plays.
    '''

    parts_list = []
    source_plate_pos = ['2', '5', '6']
    if len(paths) > 3:
        paths = paths[0:2]
    for index, path in enumerate(paths):
        plate = source_plate_pos[index]
        with open(path, 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            for index, part in enumerate(csv_reader):
                if index != 0:
                    part = list(filter(None, part))
                    parts_list.append(process_part(part, constructs_list, plate))
    merged_parts_list = pd.concat(parts_list, ignore_index=True)
    return merged_parts_list


def process_part(part, constructs_list, plate):
    '''
        Returns a part dictionary with detailed information.
        Used in get_parts()
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
    part_dict['plate'] = [plate]
    part_df = pd.DataFrame.from_dict(part_dict)
    return part_df


def get_reagents_wells(constructs_list, parts):
    '''
        Returns dataframe with rows as reagent names and cols
        as the reagent well and the volume of the reagent required.
    '''
    reagents_well_list = []
    ''' mm_upstream = digest master mix for upstream dna digests
        * 1 uL EcoRI-HF
        * 1 uL SpeI
        * 5 uL NEB Buffer 10X
        mm_downstream = digest master mix for downstream dna digests
        * 1 uL XbaI
        * 1 uL PstI
        * 5 uL NEB Buffer 10X
        mm_plasmid = digest master mix for plasmid digests
        * 1 uL EcoRI-HF
        * 1 uL PstI
        * 5 uL NEB Buffer 10X
    '''
    reagents = ['water', 'mm_upstream', 'mm_downstream', 'mm_plasmid',
                'T4Ligase10X', 'T4Ligase']
    reagents_list = []
    no_cons = len(constructs_list)
    no_plasmids = 0
    no_upstream = 0
    no_downstream = 0
    total_water_vol = parts['water_vol_tot'].sum()
    mm_vol_per_digest = 2*ENZ_VOL + NEB_BUFFER_10X_VOL
    for _, roles in parts['roles'].iteritems():
        if 'plasmid' in roles:
            no_plasmids += 1
        if 'upstream' in roles:
            no_upstream += 1
        if 'downstream' in roles:
            no_downstream += 1
    total_water_vol = total_water_vol + no_cons*WATER_VOL_LIG
    total_volumes = [total_water_vol, mm_vol_per_digest*(no_upstream + 2),
                     mm_vol_per_digest*(no_downstream + 2),
                     mm_vol_per_digest*(no_plasmids + 2),
                     T4_LIGASE_VOL_10X*no_cons,
                     T4_LIGASE_VOL*no_cons,
                     ]
    for i in range(len(reagents)):
        reagents_dict = {}
        reagents_dict['name'] = [reagents[i]]
        new_well = next_well_reagent(reagents_well_list)
        reagents_well_list.append(new_well)
        reagents_dict['well'] = [new_well]
        reagents_dict['total_vol'] = [total_volumes[i]]
        reagents_list.append(pd.DataFrame.from_dict(reagents_dict))

    neb_upstream_vol = NEB_BUFFER_10X_VOL*(no_upstream + 2)
    neb_downstream_vol = NEB_BUFFER_10X_VOL*(no_downstream + 2)
    neb_plasmid_vol = NEB_BUFFER_10X_VOL*(no_plasmids + 2)

    EcoRI_upstream_vol = ENZ_VOL*(no_upstream + 2)
    SpeI_upstream_vol = EcoRI_upstream_vol

    XbaI_downstream_vol = ENZ_VOL*(no_downstream + 2)
    PstI_downstream_vol = XbaI_downstream_vol

    EcoRI_plasmid_vol = ENZ_VOL*(no_plasmids + 2)
    PstI_plasmid_vol = EcoRI_plasmid_vol

    mm_df = pd.DataFrame(
        data={'reagent': ['NEB Buffer 10X', 'EcoRI-HF', 'SpeI', 'XbaI',
                          'PstI'],
              'volume in upstream mm': [neb_upstream_vol, EcoRI_upstream_vol,
                                        SpeI_upstream_vol, 0, 0],
              'volume in downstream mm': [neb_downstream_vol, 0, 0,
                                          XbaI_downstream_vol,
                                          PstI_downstream_vol],
              'volume in plasmid mm': [neb_plasmid_vol, EcoRI_plasmid_vol,
                                       0, 0, PstI_plasmid_vol]})
    return pd.concat(reagents_list, ignore_index=True), reagents_well_list, \
        mm_df


def get_digests(constructs_list, parts, reagents_wells_used, dest_wells_used,
                reagents):
    '''
        Creates a dataframe of digests, the intermediate step in assembly
        BioBricks constructs.
    '''
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
    '''
        Finds the next available well from a list of used wells
        for a 96 well plate
    '''
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
    '''
        Finds the next available well from a list of used wells
        for a 24 well plate
    '''
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
    '''
        Counts the number of times a part is used in the constructs.
        Differentiates between upstream uses, downstream uses,
        and plasmid uses: all require different digests.
    '''
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
    '''
        Returns assembly dictionaries to be used in the assembly protocol,
        instructing which transfers need to be made.
    '''
    source_to_digest = {}
    reagent_to_digest = {}
    digest_to_construct = {}
    reagent_to_construct = {}
    digest_to_storage = {}

    # water well
    water_index = reagents[reagents['name'] == 'water'].index.values[0]
    water_well = reagents.at[water_index, 'well']
    reagent_to_digest[water_well] = []

    mm_upstream_index = reagents[reagents[
        'name'] == 'mm_upstream'].index.values[0]
    mm_upstream_well = reagents.at[mm_upstream_index, 'well']
    reagent_to_digest[mm_upstream_well] = []

    mm_downstream_index = reagents[
        reagents['name'] == 'mm_downstream'].index.values[0]
    mm_downstream_well = reagents.at[mm_downstream_index, 'well']
    reagent_to_digest[mm_downstream_well] = []

    mm_plasmid_index = reagents[
        reagents['name'] == 'mm_plasmid'].index.values[0]
    mm_plasmid_well = reagents.at[mm_plasmid_index, 'well']
    reagent_to_digest[mm_plasmid_well] = []

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

            reagent_to_digest[water_well].append(
                (digest['dest_well'], int(parts['water_vol'][idx])))

        if digest['role'] == 'upstream':
            reagent_to_digest[mm_upstream_well].append(
                (digest['dest_well'], int(2*ENZ_VOL + NEB_BUFFER_10X_VOL)))
        elif digest['role'] == 'downstream':
            reagent_to_digest[mm_downstream_well].append(
                (digest['dest_well'], int(2*ENZ_VOL + NEB_BUFFER_10X_VOL)))
        elif digest['role'] == 'plasmid':
            reagent_to_digest[mm_plasmid_well].append(
                (digest['dest_well'], int(2*ENZ_VOL + NEB_BUFFER_10X_VOL)))

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
    reagent_to_construct[water_well] = [*zip(construct_wells, tuple(
                                    [WATER_VOL_LIG]*len(constructs)))]
    T4_ligase_10X_index = reagents[
        reagents['name'] == 'T4Ligase10X'].index.values[0]
    T4_ligase_10X_well = reagents.at[T4_ligase_10X_index, 'well']
    T4_ligase_index = reagents[reagents['name'] == 'T4Ligase'].index.values[0]
    T4_ligase_well = reagents.at[T4_ligase_index, 'well']
    reagent_to_construct[T4_ligase_10X_well] = [*zip(construct_wells, tuple(
                                    [T4_LIGASE_VOL_10X]*len(constructs)))]
    reagent_to_construct[T4_ligase_well] = [*zip(construct_wells, tuple(
                                    [T4_LIGASE_VOL]*len(constructs)))]
    return source_to_digest, reagent_to_digest, digest_to_storage, \
        digest_to_construct, reagent_to_construct


def create_tranformation_dicts(constructs, water_well='A1',
                               controls_per_cons=False):
    '''
        Returns transformation dictionaries to be used in the transformation
        protocol, instructing which transfers need to be made.
    '''

    competent_source_to_dest = {}
    control_source_to_dest = {}
    assembly_source_to_dest = {}
    water_source_to_dest = {}
    construct_wells = [construct['well'] for index, construct in
                       constructs.iterrows()]
    full_source_wells = construct_wells
    full_dest_wells = []
    competent_source_wells = []
    competent_source_wells.append(next_well(full_source_wells))
    last_competent = competent_source_wells[0]
    competent_source_to_dest[last_competent] = []
    full_source_wells.append(last_competent)
    entry_dicts = []

    for index, row in constructs.iterrows():
        construct_well = row['well']
        assembly_source_to_dest[construct_well] = []
        for i in range(4):
            entry_dict = {}
            entry_dict['name'] = [row['name'] + '-' + str(i)]
            entry_dict['number'] = [i]
            entry_dict['cell_type'] = ['competent']
            entry_dict['construct'] = row['name']
            entry_dict['construct_well'] = [row['well']]
            dest_well = next_well(full_dest_wells)
            full_dest_wells.append(dest_well)
            assembly_source_to_dest[construct_well].append((dest_well,
                                                            DNA_TRANS_VOL))

            # max volume of source well = 200 uL, use 150 uL for safety
            # -> only 3 transfers of 50 uL, then get new source well
            if len(competent_source_to_dest[last_competent]) > 2:
                last_competent = next_well(full_source_wells)
                competent_source_wells.append(last_competent)
                full_source_wells.append(last_competent)
                competent_source_to_dest[last_competent] = []
            competent_source_to_dest[last_competent].append((dest_well,
                                                             CELL_TRANS_VOL))
            entry_dict['cell_well'] = [last_competent]
            entry_dict['dest_well'] = [dest_well]
            entry_dict['reagent_well'] = [None]
            entry_dicts.append(pd.DataFrame.from_dict(entry_dict))

    control_source_wells = []
    control_source_wells.append(next_well(full_source_wells))
    last_control = control_source_wells[0]
    full_source_wells.append(last_control)
    control_source_to_dest[last_control] = []

    if controls_per_cons:
        no_constructs = len(constructs['well'].to_list())
        no_controls = no_constructs*3
    else:
        no_controls = 3

    water_source_to_dest[water_well] = []
    for i in range(no_controls):
        entry_dict['name'] = ['control' + '-' + str(i)]
        entry_dict['number'] = [i]
        entry_dict['cell_type'] = ['control']
        entry_dict['construct'] = [None]
        entry_dict['construct_well'] = [None]
        dest_well = next_well(full_dest_wells)
        full_dest_wells.append(dest_well)
        water_source_to_dest[water_well].append((dest_well, DNA_TRANS_VOL))
        if len(control_source_to_dest[last_control]) > 2:
            last_control = next_well(full_source_wells)
            control_source_wells.append(last_control)
            full_source_wells.append(last_control)
            control_source_to_dest[last_control] = []
        control_source_to_dest[last_control].append((dest_well,
                                                     CELL_TRANS_VOL))
        entry_dict['cell_well'] = [last_control]
        entry_dict['dest_well'] = [dest_well]
        entry_dict['reagent_well'] = [water_well]
        entry_dicts.append(pd.DataFrame.from_dict(entry_dict))

    transform_df = pd.concat(entry_dicts, ignore_index=True)

    return competent_source_to_dest, control_source_to_dest, \
        assembly_source_to_dest, water_source_to_dest, transform_df


def create_assembly_protocol(template_path, output_path, source_to_digest,
                             reagent_to_digest, digest_to_storage,
                             digest_to_construct, reagent_to_construct,
                             p10_mount, p10_type, well_plate_type,
                             tube_rack_type, thermocycle):
    '''
        Generates the assembly protocol used by opentrons.
        Returns the path of the assembly script.
    '''
    with open(template_path) as template_file:
        template_string = template_file.read()
    assembly_path = os.path.join(output_path, 'bb_assembly_protocol.py')
    with open(assembly_path, "w+") as protocol_file:
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
        protocol_file.write('p10_mount = "' + p10_mount + '"\n\n')
        protocol_file.write('p10_type = "' + p10_type + '"\n\n')
        protocol_file.write('well_plate_type = "' + well_plate_type + '"\n\n')
        protocol_file.write('tube_rack_type = "' + tube_rack_type + '"\n\n')
        protocol_file.write('thermocycle = ' + str(thermocycle) + '\n\n')

        # Paste the rest of the protocol.
        protocol_file.write(template_string)

    return assembly_path


def create_transformation_protocol(template_path, output_path,
                                   competent_source_to_dest,
                                   control_source_to_dest,
                                   assembly_source_to_dest,
                                   water_source_to_dest, p10_mount,
                                   p300_mount, p10_type, p300_type,
                                   well_plate_type,
                                   transformation_plate_type,
                                   tube_rack_type,
                                   soc_plate_type):
    '''
        Generates the transformation protocol used by opentrons.
        Returns the path of the transform script.
    '''
    with open(template_path) as template_file:
        template_string = template_file.read()
    transform_path = os.path.join(output_path, 'bb_transformation_protocol.py')
    with open(transform_path, "w+") as protocol_file:
        # Paste in plate maps at top of file.
        protocol_file.write('competent_source_to_dest = ' +
                            json.dumps(competent_source_to_dest) + '\n\n')
        protocol_file.write('control_source_to_dest = '
                            + json.dumps(control_source_to_dest) + '\n\n')
        protocol_file.write('assembly_source_to_dest = '
                            + json.dumps(assembly_source_to_dest) + '\n\n')
        protocol_file.write('water_to_dest = '
                            + json.dumps(water_source_to_dest) + '\n\n')
        protocol_file.write('p10_mount = "' + p10_mount + '"\n\n')
        protocol_file.write('p300_mount = "' + p300_mount + '"\n\n')
        protocol_file.write('p10_type = "' + p10_type + '"\n\n')
        protocol_file.write('p300_type = "' + p300_type + '"\n\n')
        protocol_file.write('well_plate_type = "' + well_plate_type + '"\n\n')
        protocol_file.write('transformation_plate_type = "' +
                            transformation_plate_type + '"\n\n')
        protocol_file.write('tube_rack_type = "' + tube_rack_type + '"\n\n')
        protocol_file.write('soc_plate_type = "' + soc_plate_type + '"\n\n')

        # Paste the rest of the protocol.
        protocol_file.write(template_string)

    return transform_path


def dfs_to_csv(path, index=True, **kw_dfs):
    """Generates a csv file defined by path, where kw_dfs are
    written one after another with each key acting as a title. If index=True,
    df indexes are written to the csv file.

    """
    with open(path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        for key, value in kw_dfs.items():
            csvwriter.writerow([str(key)])
            value.to_csv(csvfile, index=index)
            csvwriter.writerow('')


'''
Below is an example of how this would be run through the command line:
To use this, replace the output_folder name, construct_path, and part_path.
'''
'''
output_folder = 'C:/Users/gabri/Documents/Uni/iGEM/DJANGO-Assembly-Methods/output'
construct_path = [
    'C:/Users/gabri/Documents/Uni/iGEM/DJANGO-Assembly-Methods/examples/biobricks-constructs.csv']
part_path = [
    'C:/Users/gabri/Documents/Uni/iGEM/DJANGO-Assembly-Methods/examples/biobricks-parts.csv']
biobricks(output_folder, construct_path, part_path, thermocycle=True, **labware_dict)
'''
