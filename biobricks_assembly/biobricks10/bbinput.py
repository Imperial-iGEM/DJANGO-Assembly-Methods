import os
import csv
import json
import math
import pandas as pd
from typing import List, Dict, Tuple

# labware dictionary - filled in by front end
labware_dict = {'p10_mount': 'left', 'p300_mount': 'right',
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


def biobricks(
    output_folder: str, construct_path: List[str],
    part_path: List[str], thermocycle: bool = True,
    p10_mount: str = 'right', p300_mount: str = 'left',
    p10_type: str = 'p10_single', p300_type: str = 'p300_single',
    well_plate: str = 'biorad_96_wellplate_200ul_pcr',
    tube_rack: str = 'opentrons_24_tuberack_nest_1.5ml_snapcap',
    soc_plate: str = 'usascientific_96_wellplate_2.4ml_deep',
    transformation_plate: str = 'corning_96_wellplate_360ul_flat'
) -> List[str]:
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
        Returns:
            List of output paths
            If there is an exception, the list of output paths will contain
            only one element = the error path
            Otherwise the list of output paths will contain:
            OT-2 script paths (assembly, transformation),
            metainformation
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
            constructs, parts, reagents)

        # Creates assembly dictionaries to be used in assembly protocol
        source_to_digest, reagent_to_digest, \
            digest_to_construct, reagent_to_construct, \
            reagents_dict = create_assembly_dicts(constructs, parts,
                                                  digest_loc, reagents)

        # Creates and saves assembly protocol
        assembly_path = create_assembly_protocol(
            assembly_template_path, full_output_path, source_to_digest,
            reagent_to_digest, digest_to_construct,
            reagent_to_construct, reagents_dict, p10_mount=p10_mount,
            p10_type=p10_type, well_plate_type=well_plate,
            tube_rack_type=tube_rack, thermocycle=thermocycle)
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
        with open(error_path) as f:
            f.write(
                "Failed to generate BioBricks scripts: {}\n".format(str(e)))
        output_paths.append(error_path)
    finally:
        return output_paths


def get_constructs(
    path: str
) -> Tuple[pd.DataFrame, List[str]]:
    '''
        Returns construct dataframe from constructs csv
        Args: path = path of construct csv
        Returns:
            merged_constructs_list: dataframe of constructs
            dest_well_list: list of wells in construct plate that are used
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


def process_construct(
    construct_entry: List
) -> Dict[str, List[str]]:
    '''
        Returns construct dictionary from row in csv file
        Used in get_constructs()
        Args: construct_entry = construct row from csv in list
        Returns: Dictionary of construct info
    '''
    construct_dict = {'name': [construct_entry[0]],
                      'well': [construct_entry[1]], 'upstream':
                      [construct_entry[2]], 'downstream':
                      [construct_entry[3]], 'plasmid': [
                                      construct_entry[4]]}
    return construct_dict


def get_parts(
    paths: List[str],
    constructs_list: pd.DataFrame
) -> pd.DataFrame:
    '''
        Returns a dataframe of parts from part csv file.
        Uses constructs_list to record the number of times the part is used
        in the constructs and the roles it plays.
        Args:
            paths: list of paths to part csvs
            constructs_list: dataframe of constructs
        Returns:
            merged_parts_list: dataframe of parts
    '''

    parts_list = []
    source_plate_pos = ['2', '5']
    if len(paths) > 2:
        paths = paths[0:2]
    for index, path in enumerate(paths):
        plate = source_plate_pos[index]
        with open(path, 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            for index, part in enumerate(csv_reader):
                if index != 0:
                    part = list(filter(None, part))
                    parts_list.append(
                        process_part(part, constructs_list, plate))
    merged_parts_list = pd.concat(parts_list, ignore_index=True)
    return merged_parts_list


def process_part(
    part: List,
    constructs_list: pd.DataFrame,
    plate: str
) -> Dict[str, List]:
    '''
        Returns a part dataframe with detailed information.
        Used in get_parts()
        Args:
            part: row of part csv file
            constructs_list: constructs dataframe
            plate: source plate of part
        Returns:
            Dataframe of individual part
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
        concentration = float(part[2])
        concentration = int(concentration)
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


def get_reagents_wells(
    constructs_list: pd.DataFrame,
    parts: pd.DataFrame
) -> Tuple[pd.DataFrame, List[str], pd.DataFrame]:
    '''
        Args:
            constructs_list: dataframe of constructs
            parts: dataframe of parts
        Returns:
            Dataframe with rows as reagent names and cols
            as the reagent well and the volume of the reagent required.
            List of wells used for reagents in reagents tube rack
            Master mix dataframe giving volumes of each reagent

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
    total_water_vol = total_water_vol + no_cons*WATER_VOL_LIG + 10
    total_volumes = [total_water_vol, mm_vol_per_digest*(no_upstream + 2),
                     mm_vol_per_digest*(no_downstream + 2),
                     mm_vol_per_digest*(no_plasmids + 2),
                     T4_LIGASE_VOL_10X + 10,
                     T4_LIGASE_VOL + 10,
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


def get_digests(
    constructs_list: pd.DataFrame, parts: pd.DataFrame,
    reagents: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    '''
        Creates a dataframe of digests, the intermediate step in assembly
        BioBricks constructs.
        Args:
            constructs_list: dataframe of constructs
            parts: dataframe of parts
            reagents: dataframe of reagents
        Returns:
            dataframe of digests
            updated parts dataframe with digest well column
    '''
    digests = []
    dest_wells_used = []
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
            dest_wells.append(dest_well)
            digest_df = pd.DataFrame.from_dict(digest)
            digests.append(digest_df)
        dest_wells_list.append(dest_wells)
    parts_df['digest_wells'] = dest_wells_list
    return pd.concat(digests, ignore_index=True), parts_df


def next_well(
    wells_used: List[str]
) -> str:
    '''
        Finds the next available well from a list of used wells
        for a 96 well plate
        Args:
            List of wells used in 96 well plate
        Returns:
            Next unused well in 96 well plate
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


def next_well_reagent(
    wells_used: List[str]
) -> str:
    '''
        Finds the next available well from a list of used wells
        for a 24 well plate/tube rack
        Args:
            List of wells used in 24 well plate/tube rack
        Returns:
            Next unused well in 24 well plate/tube rack
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


def count_part_occurences(
    constructs_list: pd.DataFrame,
    part: List
) -> Tuple[List[int], List[List[int]]]:
    '''
        Counts the number of times a part is used in the constructs.
        Differentiates between upstream uses, downstream uses,
        and plasmid uses: all require different digests.
        Args:
            constructs_list: dataframe of constructs
            part: row in part csv file as list
        Returns:
            counts: list where 0th element = upstream counts,
            1st element = downstream counts, 2nd element =
            plasmid counts
            constructs_in_upstream: index of constructs a part appears
            in as the upstream part
            constructs_in_downstream: index of constructs a part appears
            in as the downstream part
            constructs_in_plasmid: index of constructs a part appears
            in as the plasmid part
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


def create_assembly_dicts(
    constructs: pd.DataFrame, parts: pd.DataFrame,
    digests: pd.DataFrame, reagents: pd.DataFrame
) -> Tuple[Dict, Dict, Dict, Dict, Dict]:
    '''
        Returns assembly dictionaries to be used in the assembly protocol,
        instructing which transfers need to be made.
        Args:
            constructs: dataframe of constructs
            parts: dataframe of parts
            digests: dataframe of digests
            reagents: dataframe of reagents
        Returns:
            source_to_digest: dictionary with key = source (part) well,
            key = list of tuples in format (digest well, volume to transfer)
            reagent_to_digest: dictionary with key = reagent well,
            key = list of tuples in format (digest well, volume to transfer)
            digest_to_construct: dictionary with key = digest well,
            key = list of tuples in format (construct well, volume to transfer)
            reagent_to_construct: dictionary with key = reagent well,
            key = list of tuples in format (construct well, volume to transfer)
            reagents_dict: dictionary with key = reagent name,
            key = reagent well
    '''
    source_to_digest = {}
    reagent_to_digest = {}
    digest_to_construct = {}
    reagent_to_construct = {}
    reagents_dict = {}

    # water well
    water_index = reagents[reagents['name'] == 'water'].index.values[0]
    water_well = reagents.at[water_index, 'well']
    reagent_to_digest[water_well] = []
    reagents_dict['water'] = water_well

    mm_upstream_index = reagents[reagents[
        'name'] == 'mm_upstream'].index.values[0]
    mm_upstream_well = reagents.at[mm_upstream_index, 'well']
    reagent_to_digest[mm_upstream_well] = []
    reagents_dict['mm_upstream'] = mm_upstream_well

    mm_downstream_index = reagents[
        reagents['name'] == 'mm_downstream'].index.values[0]
    mm_downstream_well = reagents.at[mm_downstream_index, 'well']
    reagent_to_digest[mm_downstream_well] = []
    reagents_dict['mm_downstream'] = mm_downstream_well

    mm_plasmid_index = reagents[
        reagents['name'] == 'mm_plasmid'].index.values[0]
    mm_plasmid_well = reagents.at[mm_plasmid_index, 'well']
    reagent_to_digest[mm_plasmid_well] = []
    reagents_dict['mm_plasmid'] = mm_plasmid_well

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
    reagents_dict['T4Ligase10X'] = T4_ligase_10X_well
    T4_ligase_index = reagents[reagents['name'] == 'T4Ligase'].index.values[0]
    T4_ligase_well = reagents.at[T4_ligase_index, 'well']
    reagents_dict['T4Ligase'] = T4_ligase_well
    reagent_to_construct[T4_ligase_10X_well] = [*zip(construct_wells, tuple(
                                    [T4_LIGASE_VOL_10X]*len(constructs)))]
    reagent_to_construct[T4_ligase_well] = [*zip(construct_wells, tuple(
                                    [T4_LIGASE_VOL]*len(constructs)))]
    return source_to_digest, reagent_to_digest, \
        digest_to_construct, reagent_to_construct, reagents_dict


def create_tranformation_dicts(
    constructs: pd.DataFrame, water_well: str = 'A1',
    controls_per_cons: bool = False
) -> Tuple[Dict[str, List[Tuple[str, int]]], Dict[str, List[Tuple[str, int]]],
           Dict[str, List[Tuple[str, int]]], Dict[str, List[Tuple[str, int]]],
           pd.DataFrame]:
    '''
        Creates transformation dictionaries to be used in the
        transformation protocol, instructing which transfers need to be made.
        Creates transform_df for metainformation
        Competent wells + construct wells -> same well for transformation.
        Control wells + water well -> same well for transformation.
        Args:
            Constructs: dataframe of constructs
            water_well: well that water is stored in
            controls_per_cons: create three controls per construct if True
            create three controls total if False
        Returns:
            competent_source_to_dest: dictionary with key = competent cell
            well, value = tuple of destination well + transfer vol
            control_source_to_dest: dictionary with key = control cell
            well, value = tuple of destination well + transfer vol
            assembly_source_to_dest: dictionary with key = construct
            well, value = tuple of destination well + transfer vol,
            water_source_to_dest: dictionary with key = water
            well, value = tuple of destination well + transfer vol
            transform_df: dataframe of transformation reactions
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


def create_assembly_protocol(
    template_path: str, output_path: str,
    source_to_digest: Dict[str, List[Tuple[str, int]]],
    reagent_to_digest: Dict[str, List[Tuple[str, int]]],
    digest_to_construct: Dict[str, List[Tuple[str, int]]],
    reagent_to_construct: Dict[str, List[Tuple[str, int]]],
    reagents_dict: Dict[str, str],
    p10_mount: str, p10_type: str, well_plate_type: str,
    tube_rack_type: str, thermocycle: bool
) -> str:
    '''
        Generates the assembly protocol used by opentrons.
        Returns the path of the assembly script.
        Args:
            template_path: absolute path of the Opentrons script template
            output_path: absolute path of the output folder to save protocol in
            source_to_digest: dictionary of form
            Dict[str, List[Tuple(str, int)]], dictionary key (string) gives
            source (part) well to transfer from, the 0th element of each tuple
            gives well to transfer to (digest well in this case), with the 1st
            element of the tuple giving the volume to transfer.
            reagent_to_digest: dictionary of same form as source_to_digest
            (Dict[str, List[Tuple(str, int)]]), instructing transfers from
            reagent wells to digest wells
            digest_to_storage: dictionary of same form as source_to_digest
            (Dict[str, List[Tuple(str, int)]]), instructing transfers from
            digest wells to storage wells (wells where digest not used in
            construct is stored after assembly)
            digest_to_construct: dictionary of same form as source_to_digest
            (Dict[str, List[Tuple(str, int)]]), instructing transfers from
            digest wells to construct wells
            reagent_to_construct: dictionary of same form as source_to_digest
            (Dict[str, List[Tuple(str, int)]]), instructing transfers from
            reagent wells to construct wells
            p10_mount: "left" or "right", the Opentrons pipette mount options
            p10_type: the name of the p10 pipette, e.g. "p10_single"
            well_plate_type: the name of the well plate type used as the source
            plate and construct plate
            tube_rack_type: the name of the tube rack type used for holding the
            reagents
            thermocycle: True or False, True = run thermocycle module in
            scripts, False = use benchtop thermocycler
        Returns:
            path of assembly protocol script
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
        protocol_file.write('reagents_dict = '
                            + json.dumps(reagents_dict) + '\n\n')
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


def create_transformation_protocol(
    template_path: str, output_path: str,
    competent_source_to_dest: Dict[str, List],
    control_source_to_dest: Dict[str, List],
    assembly_source_to_dest: Dict[str, List],
    water_source_to_dest: Dict[str, List], p10_mount: str,
    p300_mount: str, p10_type: str, p300_type: str,
    well_plate_type: str,
    transformation_plate_type: str,
    tube_rack_type: str, soc_plate_type: str
) -> str:
    '''
        Generates the transformation protocol used by opentrons.
        Args:
            template_path: absolute path of the Opentrons script template
            output_path: absolute path of the output folder to save protocol in
            competent_source_to_digest: dictionary of form
            Dict[str, List[Tuple(str, int)]], dictionary key (string) gives
            competent cell well to transfer from, the 0th element of each tuple
            gives well to transfer to (transformation well), with the 1st
            element of the tuple giving the volume to transfer.
            control_source_to_digest: dictionary of same form as
            competent_source_to_digest (Dict[str, List[Tuple(str, int)]]),
            instructing transfers from control wells to transformation wells
            assembly_source_to_digest: dictionary of same form as
            competent_source_to_digest (Dict[str, List[Tuple(str, int)]]),
            instructing transfers from construct wells to transformation wells
            water_source_to_digest: dictionary of same form as
            competent_source_to_digest (Dict[str, List[Tuple(str, int)]]),
            instructing transfers from water well to transformation wells
            p10_mount: "left" or "right", the Opentrons pipette mount options
            p300_mount: "left" or "right", the Opentrons pipette mount options
            p10_type: the name of the p10 pipette, e.g. "p10_single"
            p300_type: the name of the p300 pipette, e.g. "p300_single"
            well_plate_type: the name of the well plate type used as the
            construct plate
            transformation_plate_type: the name of the well plate type used as the
            transformation plate
            tube_rack_type: the name of the tube rack type used to store cells
            soc_plate_type: the name of the plate type used to store soc
        Returns:
            path of transform protocol script
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
output_folder = 'C:/Users/gabri/Documents/Uni/iGEM/DJANGO-Assembly-Methods/output/last'
construct_path = [
    'C:/Users/gabri/Downloads/construct_b.csv']
part_path = [
    'C:/Users/gabri/Downloads/parts_1_b.csv']
biobricks(output_folder, construct_path, part_path, thermocycle=True,
          **labware_dict)

'''