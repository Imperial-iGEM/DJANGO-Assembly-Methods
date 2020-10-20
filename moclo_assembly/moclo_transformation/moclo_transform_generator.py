import os
import csv
import json
import pandas as pd
from typing import List, Dict, Tuple

# labware dictionary - filled in by front end
labware_dict = {'p10_mount': 'right', 'p300_mount': 'left',
                'p10_type': 'p10_single', 'p300_type': 'p300_multi',
                'well_plate': 'biorad_96_wellplate_200ul_pcr',
                'trough': 'usascientific_12_reservoir_22ml',
                'reagent_plate': 'biorad_96_wellplate_200ul_pcr',
                'agar_plate': 'thermofisher_96_wellplate_180ul'}


def moclo_function(
    output_folder: str, construct_path: List[str], part_path: List[str],
    thermocycle: bool = True, p10_mount: str = 'right',
    p300_mount: str = 'left', p10_type: str = 'p10_single',
    p300_type: str = 'p300_multi',
    well_plate: str = 'biorad_96_wellplate_200ul_pcr',
    trough: str = 'usascientific_12_reservoir_22ml',
    reagent_plate: str = 'biorad_96_wellplate_200ul_pcr',
    agar_plate: str = 'thermofisher_96_wellplate_180ul'
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
            metainformation (assembly, transformation, agar plate)
    '''

    output_paths = []
    full_output_path = output_folder

    # In case construct path is list: can only have one path
    if type(construct_path) == list:
        construct_path = construct_path[0]

    current_dir = os.getcwd()

    '''
        Ensure that template directories are correct.
        Important for running this script through the front end.
    '''
    if os.path.split(current_dir)[1] == 'moclo_transformation':
        assembly_path = os.path.join(
            current_dir, 'data', 'moclo_assembly_template.py')
        transform_path = os.path.join(
            current_dir, 'data', 'transform_moclo_template.py')
    elif os.path.split(current_dir)[1] == 'moclo_assembly':
        assembly_path = os.path.join(
            current_dir, 'moclo_assembly', 'moclo_transformation', 'data',
            'moclo_assembly_template.py')
        transform_path = os.path.join(
            current_dir, 'moclo_assembly', 'moclo_transformation', 'data',
            'transform_moclo_template.py')
    else:
        assembly_path = os.path.join(
            current_dir, 'moclo_assembly', 'moclo_transformation', 'data',
            'moclo_assembly_template.py')
        transform_path = os.path.join(
            current_dir, 'moclo_assembly', 'moclo_transformation', 'data',
            'transform_moclo_template.py')

    # sets paths to be used by script gen
    config = {
        'output_folder_path': full_output_path,
        'assembly_template_path': assembly_path,
        'transform_template_path': transform_path
    }

    # for now only do single (other option = triplicate)
    combinations_limit = 'single'

    if 'multi' in p300_type.lower():
        multi = True
    else:
        multi = False

    try:
        # Load in CSV files as a dict containing lists of lists.
        # Loop through all part_path's and merge dicts
        dna_plate_map_dict = {}
        if type(part_path) == list:
            for path in part_path:
                dna_plate_map_dict_local = generate_plate_maps(path)
                dna_plate_map_dict.update(dna_plate_map_dict_local)
        else:
            dna_plate_map_dict = generate_plate_maps(part_path)

        combinations_to_make = []
        combinations_to_make = generate_combinations(construct_path)

        check_number_of_combinations(combinations_limit, combinations_to_make)

        # Generate and save output plate maps.
        triplicate, agar_path = generate_and_save_output_plate_maps(
            combinations_to_make, combinations_limit,
            config['output_folder_path'])

        # Define assembly metainformation path
        assembly_metainformation_path = os.path.join(
            config['output_folder_path'], 'assembly_metainformation.csv')

        # Create and save assembly metainformation
        parts, comb, mm, reagents = create_metainformation(
            assembly_metainformation_path,
            dna_plate_map_dict, combinations_to_make, labware_dict,
            thermocycle, triplicate)

        # create master mix dictionary to use in assembly protocol
        reagent_to_mm_dict, mm_dict = get_mm_dicts(mm, reagents)

        transform_metainformation_path = os.path.join(
            config['output_folder_path'], 'transform_metainformation.csv')
        create_transform_metainformation(
            transform_metainformation_path,
            labware_dict, triplicate, multi)

        # Create a protocol file and hard code the plate maps into it.
        assembly_path, transform_path = create_protocol(
            dna_plate_map_dict, combinations_to_make, reagent_to_mm_dict,
            mm_dict, config['assembly_template_path'],
            config['transform_template_path'], config['output_folder_path'],
            thermocycle, triplicate, multi, p10Mount=p10_mount,
            p300Mount=p300_mount, p10_type=p10_type, p300_type=p300_type,
            reaction_plate_type=well_plate, reagent_plate_type=reagent_plate,
            trough_type=trough, agar_plate_type=agar_plate)
        print('Succesfully created opentrons scripts')

        output_paths.append(assembly_path)
        output_paths.append(transform_path)
        output_paths.append(assembly_metainformation_path)
        output_paths.append(transform_metainformation_path)
        output_paths.append(agar_path)

    except Exception as e:
        error_path = os.path.join(full_output_path, 'MoClo_error.txt')
        print("Exception: error_path", error_path)

        with open(error_path, 'w') as f:
            f.write("Failed to generate MoClo scripts: {}\n".format(str(e)))
        output_paths.append(error_path)
    finally:
        print("output_paths:", output_paths)
        return output_paths

###############################################################################
# Functions for getting user input
###############################################################################


def generate_plate_maps(
    filename: str
) -> Dict[str, List[List]]:
    '''
        Generates dictionaries for the part csvs
        Args: filename = absolute path to part csv
        Returns: dictionary of plate maps with key = name of part csv,
        value = list of rows (= list of lists)
    '''
    plate_maps = {}
    plate_map = []
    with open(filename, encoding='utf-8-sig') as file:
        for row in csv.reader(file, dialect='excel'):
            if len(row) == 0:
                continue
            if row[0]:
                plate_map.append(row)
    plate_name = os.path.splitext(os.path.basename(filename))[0]
    plate_maps[plate_name] = plate_map

    return plate_maps


def generate_combinations(
    combinations_filename: str
) -> List[Dict]:
    '''
        Generates a list of dictionaries of constructs to be made
        Args: combinations_filename = absolute path to construct csv file
        Returns: List of construct dictionaries with keys "name" and "parts"
    '''
    combinations_to_make = []
    with open(combinations_filename, encoding='utf-8-sig') as f:
        for row in csv.reader(f, dialect='excel'):
            if len(row) == 0:
                continue
            if row[0]:
                combinations_to_make.append({
                                            "name": row[0],
                                            "parts": [x for x in row[1:] if x]
                                            })
    return combinations_to_make


def check_number_of_combinations(
    combinations_limit: str,
    combinations_to_make: List[Dict]
):
    '''
        Ensures that the number of constructs does not exceed the maximum
        Args:
            combinations_limit: "single" or "triplicate" - if "single" can do
            max 88 constructs, if "triplicate" does every construct 3 times -
            max 24 constructs
        Raises: ValueError if there are too many constructs or
        combinations_limit is not "single" or "triplicate"
    '''
    number_of_combinations = len(combinations_to_make)
    if combinations_limit == 'single':
        if number_of_combinations > 88:
            raise ValueError('Too many combinations ({0}) requested.'
                             'Max for single combinations is '
                             ' 88.'.format(number_of_combinations))
    elif combinations_limit == 'triplicate':
        if number_of_combinations > 24:
            raise ValueError('Too many combinations ({0}) requested.'
                             'Max for triplicate combinations is '
                             '24.'.format(number_of_combinations))
    else:
        raise ValueError('Combinations limit must be single of triplicate')

###############################################################################
# Functions for creating output files
###############################################################################


def generate_and_save_output_plate_maps(
    combinations_to_make: List[Dict],
    combinations_limit: str,
    output_folder_path: str
) -> Tuple[str, str]:
    '''
        Saves the mapping of the agar plate for use in transformation.
        Args:
            combinations_to_make = list of construct dictionaries
            combinations_limit = "single" or "triplicate"
            output_folder_path = where to save mapping
        Returns:
            triplicate: whether 'single' (triplicate = False) or 'triplicate'
            (triplicate = True) is selected
            output_filename: the absolute path to the agar plate csv
    '''
    # Split combinations_to_make into 8x6 plate maps.
    output_plate_map_flipped = []
    for i, combo in enumerate(combinations_to_make):
        name = combo['name']
        # if i % 32 == 0:
        #   # new plate
        #   output_plate_maps_flipped.append([[name]])
        if i % 8 == 0:
            # new column
            output_plate_map_flipped.append([name])
        else:
            output_plate_map_flipped[-1].append(name)

    # Correct row/column flip.
    output_plate_map = []
    for i, row in enumerate(output_plate_map_flipped):
        for j, element in enumerate(row):
            if j >= len(output_plate_map):
                output_plate_map.append([element])
            else:
                output_plate_map[j].append(element)

    triplicate = False
    # creating an output plate three copies of each column
    if combinations_limit == 'triplicate':
        combinedRow = []
        splitRows = []
        triplicate = True

        for j in range(0, len(output_plate_map)):  # 8
            # Tripling each item in the plate
            for item in output_plate_map[j]:
                combinedRow.append(item)
                combinedRow.append(item)
                combinedRow.append(item)

        # Splitting up the rows into lists with number of elements (3, 6 or 9)
        # depending on how many columns in the combinations file
        how_to_split = 3*len(output_plate_map_flipped)
        for index, item in enumerate(combinedRow):
            if index % how_to_split == 0:
                splitRows.append([])
                splitRows[-1].append(item)
            else:
                splitRows[-1].append(item)

        output_plate_map = splitRows

    output_filename = os.path.join(output_folder_path, "Agar_plate.csv")
    with open(output_filename, 'w+', newline='') as f:
        writer = csv.writer(f)
        for row in output_plate_map:
            writer.writerow(row)
    return triplicate, output_filename


def create_metainformation(
    output_path: str, dna_plate_map_dict: Dict[str, List[List]],
    combinations_to_make: List[Dict],
    labware_dict: Dict[str, str], thermocycle: bool, triplicate: str
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    '''
        Returns detailed metainformation and saves in a csv.
        Includes a parts dataframe, a combinations (constructs)
        dataframe, a reagents dataframe, and a master mix dataframe.
        Args:
            output_path: the full path of the output folder
            dna_plate_map_dict: the dictionary of parts
            combinations_to_make: the list of dictionaries of
            constructs
            labware_dict: the dictionary of labware chosen
            thermocyle: whether the thermocycler module is used
            triplicate: whether 'single' (triplicate = False) or 'triplicate'
            (triplicate = True) is selected
        Returns:
            parts_df: dataframe of parts
            combinations_df: dataframe of constructs
            mm_df: master mix dataframe, contains information on all of the
            master mixes needed (different master mix needed for different
            number of parts per construct)
            reagents_df: reagents dataframe, contains information on all of the
            reagents, does not include master mix but DOES include reagents to
            go into master mixes
    '''

    # Create parts dataframe
    parts_df = create_parts_df(dna_plate_map_dict)

    # Creates combinations dataframe
    combination_df_list = []
    for comb_index, combination_dict in enumerate(combinations_to_make):
        combination_df_dict = {}
        name = combination_dict['name']
        combination_df_dict['name'] = [name]
        combination_df_dict['parts'] = [combination_dict['parts']]
        combination_df_dict['well'] = [index_to_well_name(comb_index)]
        combination_df_dict['no_parts'] = [len(combination_dict['parts'])]
        combination_df_dict['plate'] = ['reaction_plate']
        combination_df_list.append(pd.DataFrame.from_dict(combination_df_dict))
        for part in combination_dict['parts']:
            part_indices = parts_df[parts_df['name'] == part].index.values
            for part_index in part_indices:
                if parts_df.at[part_index, 'combinations'] == '0':
                    parts_df.at[part_index, 'combinations'] = [
                        combination_dict['name']]
                else:
                    parts_df.at[part_index, 'combinations'].append(
                        combination_dict['name'])
    if combination_df_list:
        combinations_df = pd.concat(combination_df_list, ignore_index=True)
    else:
        combination_df_dict['name'] = None
        combination_df_dict['parts'] = None
        combination_df_dict['well'] = None
        combination_df_dict['no_parts'] = None
        combination_df_dict['plate'] = None
        combinations_df = pd.DataFrame(
            combination_df_dict, index=len(combination_df_dict))

    # Creates master mix dataframe
    mm_df = create_mm_df(combinations_df)

    # Creates reagents dataframe
    reagents_df = create_reagents_df(mm_df)

    # saves as csv, adding extra info on run and labware
    with open(output_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        if triplicate:
            csvwriter.writerow(['Triplicate'])
        else:
            csvwriter.writerow(['Single'])
        csvwriter.writerow('')
        if thermocycle:
            csvwriter.writerow(['Using thermocycler module'])
        else:
            csvwriter.writerow(['Not using thermocycler module'])
        csvwriter.writerow('')
        csvwriter.writerow(['P10 Mount:', labware_dict['p10_mount']])
        csvwriter.writerow('')
        csvwriter.writerow('')
        csvwriter.writerow(['Labware', 'Labware definition', 'Position'])
        csvwriter.writerow(['DNA Source plate',
                            labware_dict['well_plate'], '1'])
        if thermocycle:
            csvwriter.writerow(['Reaction plate',
                                labware_dict['well_plate'], 'thermocycler'])
        else:
            csvwriter.writerow(['Reaction plate',
                                labware_dict['well_plate'], 'tempdeck (10)'])
        csvwriter.writerow(['Trough (contains water, washes)',
                            labware_dict['trough'], '5'])
        csvwriter.writerow(['Reagents plate',
                            labware_dict['reagent_plate'], '4'])
        csvwriter.writerow('')
        csvwriter.writerow('')

        kw_dfs = {'PARTS': parts_df, 'COMBINATIONS': combinations_df,
                  'MASTER_MIX': mm_df, 'REAGENTS': reagents_df}

        for key, value in kw_dfs.items():
            csvwriter.writerow([str(key)])
            value.to_csv(csvfile, index=False)
            csvwriter.writerow('')

    return parts_df, combinations_df, mm_df, reagents_df


def create_parts_df(
    dna_plate_map_dict: Dict[str, List[List]]
) -> pd.DataFrame:
    '''
        Returns a dataframe of parts and delegates wells.
        Takes in the dictionary of parts.
        Args:
            dna_plate_map_dict: dictionary with keys = plate names, values =
            list of rows = list of list of parts
        Returns:
            parts_df: dataframe of parts with dummy '0' for combinations col
    '''
    letter_dict = {'0': 'A', '1': 'B', '2': 'C', '3': 'D', '4': 'E', '5': 'F',
                   '6': 'G', '7': 'H'}
    for plate, plate_wells in dna_plate_map_dict.items():
        part_df_list = []
        for row_index, row in enumerate(plate_wells):
            row_letter = letter_dict[str(row_index)]
            for col_index, part in enumerate(row):
                if len(part) > 0:
                    part_dict = {}
                    well_name = row_letter + str(col_index + 1)
                    part_dict['name'] = [part]
                    part_dict['well'] = [well_name]
                    part_dict['plate'] = [plate]
                    part_df_list.append(pd.DataFrame.from_dict(part_dict))
    parts_df = pd.concat(part_df_list, ignore_index=True)

    # Empty column to be filled after combinations df is generated
    parts_df['combinations'] = pd.Series(['0'] * len(parts_df.index),
                                         index=parts_df.index)
    return parts_df


def create_mm_df(
    combinations_df: pd.DataFrame
) -> pd.DataFrame:
    '''
        Creates a master mix dataframe and delegates wells.
        Different master mixes must be created depending on
        the number of parts per construct.
        Args: combinations_df = dataframe of constructs
        Returns: dataframe of master mixes with wells and volumes
        of different reagents required
    '''
    TOT_VOL_PER_ASSEMBLY = 20
    BUFFER_VOL_PER_ASSEMBLY = 2
    LIGASE_VOL_PER_ASSEMBLY = 0.5
    ENZYME_VOL_PER_ASSEMBLY = 1
    PART_VOL = 2
    avail_mm_wells_no = list(range(95, len(combinations_df)-2, -1))
    avail_mm_wells = [index_to_well_name(no) for no in avail_mm_wells_no]
    mm_df_list = []

    # minimum of 2 parts per construct; max of 8
    for i in range(2, 9):
        # count number of combinations with i parts
        combinations_i = combinations_df[
            combinations_df['no_parts'] == i].index.values
        combinations = [combinations_df.loc[i] for i in combinations_i]
        if len(combinations) > 0:
            # create a new dictionary and fill
            mm_dict = {}
            well = avail_mm_wells.pop(0)
            mm_dict['well'] = [well]
            mm_dict['no_parts'] = [i]
            parts_per_assembly = i
            mm_vol_per_assembly = TOT_VOL_PER_ASSEMBLY - \
                parts_per_assembly*PART_VOL
            mm_dict['vol_per_assembly'] = [mm_vol_per_assembly]
            # number of assemblies is limited and dead vol is
            # accounted for
            max_assemblies = 180 // mm_vol_per_assembly
            mm_combinations = []
            if max_assemblies % 2 == 0:
                max_assemblies = max_assemblies - 2
            else:
                max_assemblies = max_assemblies - 3
            tot_assemblies = len(combinations)
            no_assemblies = 0
            for comb_index, comb_row in enumerate(combinations):
                if no_assemblies < max_assemblies:
                    mm_combinations.append(comb_row['name'])
                    no_assemblies += 1
                    if comb_index == tot_assemblies-1:
                        # no more assemblies for no of parts
                        # save the dictionary after filling
                        if no_assemblies % 2 == 0:
                            no = no_assemblies + 2
                        else:
                            no = no_assemblies + 3
                        mm_dict['combinations'] = [mm_combinations]
                        mm_dict['no_assemblies'] = [no_assemblies]
                        mm_dict['buffer_vol'] = [BUFFER_VOL_PER_ASSEMBLY*no]
                        mm_dict['ligase_vol'] = [LIGASE_VOL_PER_ASSEMBLY*no]
                        mm_dict['enzyme_vol'] = [ENZYME_VOL_PER_ASSEMBLY*no]
                        water_vol = mm_vol_per_assembly*no - \
                            mm_dict['buffer_vol'][0] - \
                            mm_dict['ligase_vol'][0] - mm_dict['enzyme_vol'][0]
                        mm_dict['water_vol'] = [water_vol]
                        mm_dict['plate'] = ['reaction_plate']
                        mm_df_list.append(pd.DataFrame.from_dict(mm_dict))
                else:
                    # run out of space for assemblies in mm well
                    # save mm_dict before creating new one
                    no = max_assemblies + 2
                    mm_dict['combinations'] = [mm_combinations]
                    mm_dict['no_assemblies'] = [no_assemblies]
                    mm_dict['buffer_vol'] = [BUFFER_VOL_PER_ASSEMBLY*no]
                    mm_dict['ligase_vol'] = [LIGASE_VOL_PER_ASSEMBLY*no]
                    mm_dict['enzyme_vol'] = [ENZYME_VOL_PER_ASSEMBLY*no]
                    water_vol = mm_vol_per_assembly*no - \
                        mm_dict['buffer_vol'][0] - \
                        mm_dict['ligase_vol'][0] - mm_dict['enzyme_vol'][0]
                    mm_dict['water_vol'] = [water_vol]
                    mm_dict['plate'] = ['reaction_plate']
                    mm_df_list.append(pd.DataFrame.from_dict(mm_dict))
                    mm_dict = {}
                    well = avail_mm_wells.pop(0)
                    mm_dict['well'] = [well]
                    mm_combinations = [comb_row['name']]
                    mm_dict['no_parts'] = [i]
                    mm_dict['vol_per_assembly'] = [mm_vol_per_assembly]
                    no_assemblies = 1
    # turn into dataframe
    if mm_df_list:
        mm_df = pd.concat(mm_df_list, ignore_index=True)
    else:  # If mm_df is empty, make default
        mm_dict = {}
        mm_dict['well'] = None
        mm_dict['no_parts'] = None
        mm_dict['vol_per_assembly'] = None
        mm_dict['combinations'] = None
        mm_dict['no_assemblies'] = None
        mm_dict['buffer_vol'] = None
        mm_dict['ligase_vol'] = None
        mm_dict['enzyme_vol'] = None
        mm_dict['water_vol'] = None
        mm_dict['plate'] = None
        mm_df = pd.DataFrame(mm_dict, index=range(len(mm_dict)))
    return mm_df


def create_reagents_df(
    mm_df: pd.DataFrame
) -> pd.DataFrame:
    '''
        Creates a dataframe of reagents used to make master mixes.
        More than one buffer well may be required, and water is
        held on a separate plate.
        Also indicates which master mix wells the reagent is
        transferred to.
        Args: master mix dataframe
        Returns: dataframe of reagents used in master mix + water
    '''
    water_vol = 15000
    reagents_df_list = []
    ligase_dict = {'name': ['ligase'], 'well': ['H12'], 'plate':
                   ['reagents_plate']}
    ligase_vol = mm_df.loc[0:len(mm_df)-1, 'ligase_vol'].sum()
    ligase_dead_vol = 2*(ligase_vol // len(mm_df))
    tot_ligase = ligase_vol + ligase_dead_vol

    # round up to the nearest 10
    if tot_ligase % 10 > 0:
        tot_ligase = 10*((tot_ligase // 10) + 1)
    ligase_dict['volume'] = [tot_ligase]
    ligase_dict['mm_wells'] = [list(mm_df['well'])]

    reagents_df_list.append(pd.DataFrame.from_dict(ligase_dict))

    enzyme_dict = {'name': ['restriction_enzyme'], 'well': ['G12'], 'plate':
                   ['reagents_plate']}

    enzyme_vol = mm_df.loc[0:len(mm_df)-1, 'enzyme_vol'].sum()
    enzyme_dead_vol = 2*(enzyme_vol // len(mm_df))
    tot_enzyme = enzyme_vol + enzyme_dead_vol

    # round up to the nearest 10
    if tot_enzyme % 10 > 0:
        tot_enzyme = 10*((tot_enzyme // 10) + 1)
    enzyme_dict['volume'] = [tot_enzyme]
    enzyme_dict['mm_wells'] = [list(mm_df['well'])]

    reagents_df_list.append(pd.DataFrame.from_dict(enzyme_dict))

    buffer_vol = mm_df.loc[0:len(mm_df)-1, 'buffer_vol'].sum()

    buffer_dead_vol = 2*(buffer_vol // len(mm_df))

    tot_buffer = buffer_vol + buffer_dead_vol

    # round to the nearest 10
    if tot_buffer % 10 > 0:
        tot_buffer = 10*((tot_buffer // 10) + 1)

    if tot_buffer > 180:
        # need to create more than one well
        for i in range(len(mm_df)-2, 0, -1):
            buffer_vol1 = mm_df.loc[0:i, 'buffer_vol'].sum()
            # buffer_dead_vol1 = 2*(buffer_vol1 // (i + 1))
            tot_buffer1 = buffer_vol1 + buffer_dead_vol

            if tot_buffer1 % 10 > 0:
                tot_buffer1 = 10*((tot_buffer1 // 10) + 1)

            if tot_buffer1 <= 180:
                # find configuration in which both buffer wells
                # have max 180 uL
                # there should never need to be more than 2 wells
                wells1 = list(mm_df.loc[0:i, 'well'])
                buffer_vol2 = mm_df.loc[i+1:len(mm_df)-1, 'buffer_vol'].sum()
                # buffer_dead_vol2 = 2*(buffer_vol2 // (len(mm_df)-i-1))
                tot_buffer2 = buffer_vol2 + buffer_dead_vol

                if tot_buffer2 % 10 > 0:
                    tot_buffer2 = 10*((tot_buffer2 // 10) + 1)

                wells2 = list(mm_df.loc[i+1:len(mm_df)-1, 'well'])
                break

        buffer_dict1 = {'name': ['buffer-1'], 'well': ['F12'], 'plate':
                        ['reagents_plate']}
        buffer_dict1['volume'] = [tot_buffer1]
        buffer_dict1['mm_wells'] = [wells1]
        reagents_df_list.append(pd.DataFrame.from_dict(buffer_dict1))

        buffer_dict2 = {'name': ['buffer-2'], 'well': ['E12'], 'plate':
                        ['reagents_plate']}
        buffer_dict2['volume'] = [tot_buffer2]
        buffer_dict2['mm_wells'] = [wells2]
        reagents_df_list.append(pd.DataFrame.from_dict(buffer_dict2))

    else:
        buffer_dict = {'name': ['buffer'], 'well': ['F12'], 'plate':
                       ['reagents_plate']}
        buffer_dict['volume'] = [tot_buffer]
        buffer_dict['mm_wells'] = [list(mm_df['well'])]
        reagents_df_list.append(pd.DataFrame.from_dict(buffer_dict))

    water_dict = {'name': ['water'], 'well': ['A1'], 'plate':
                  ['trough'], 'volume': [water_vol]}
    water_dict['mm_wells'] = [list(mm_df['well'])]

    reagents_df_list.append(pd.DataFrame.from_dict(water_dict))

    reagents_df = pd.concat(reagents_df_list, ignore_index=True, sort=False)

    return reagents_df


def get_mm_dicts(
    mm_df: pd.DataFrame, reagents_df: pd.DataFrame
) -> Tuple[Dict[str, List[Tuple[str, str, str]]], Dict]:
    '''
        Master mix dictionary purely for use in the assembly script.
        Provides instructions on tranfers.
        Args:
            mm_df = dataframe of master mix, gives wells and diff vol needed
            reagents_df = dataframe of reagents to be used in master mix and
            other parts of assembly
        Returns:
            reagent_to_mm_dict: dictionary directing where to transfer each
            reagent to to make master mixes, key = reagent well, value =
            list of tuples of reagent plate (different for water and other
            reagents), master mix well, and volume to be transferred
            mm_dict_list = mm_df rows stored as dictionaries in list
    '''
    reagent_to_mm_dict = {}
    for index, row in reagents_df.iterrows():
        source_well = row['well']
        reagent_to_mm_dict[source_well] = []
        if row['mm_wells']:
            for well in row['mm_wells']:
                if not (mm_df[mm_df['well'] == well].empty):
                    mm_well_index = mm_df[
                        mm_df['well'] == well].index.values[0]
                else:
                    continue
                if 'ligase' in row['name']:
                    transfer_vol = mm_df.at[mm_well_index, 'ligase_vol']
                elif 'restriction_enzyme' in row['name']:
                    transfer_vol = mm_df.at[mm_well_index, 'enzyme_vol']
                elif 'buffer' in row['name']:
                    transfer_vol = mm_df.at[mm_well_index, 'buffer_vol']
                elif 'water' in row['name']:
                    transfer_vol = mm_df.at[mm_well_index, 'water_vol']
                reagent_to_mm_dict[source_well].append(
                    tuple([row['plate'], well, str(transfer_vol)]))
        else:
            reagent_to_mm_dict[source_well].append(None, None, None)
    mm_dict_list = []
    for index, row in mm_df.iterrows():
        mm_dict = row.to_dict()
        mm_dict_list.append(mm_dict)
    return reagent_to_mm_dict, mm_dict_list


def index_to_well_name(
    no: int
) -> str:
    '''
        Converts well from number format to letter format
        Args: well in number format e.g. 0
        Returns: well in letter format e.g. 'A1'
    '''
    sample_number = no + 1
    letter = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    final_well_column = sample_number // 8 + \
        (1 if sample_number % 8 > 0 else 0)
    final_well_row = letter[sample_number - (final_well_column - 1) * 8 - 1]
    well = final_well_row + str(final_well_column)
    return well


def create_transform_metainformation(
    output_path: str, labware_dict: Dict[str, str],
    triplicate: str, multi: bool
):
    '''
        Saves transform metainformation and labware informaiton.
        SOC used in two steps: adding soc (150 uL) and dilution (45 uL)
        times by 96 as reaction plate has 96 wells
        Add 300 (150*2) and 90 (45*2) as dead vols
        Agar plate positions in agar plate csv

        Args:
            output_path: absolute path to transformation metainformation file
            labware_dict: dictionary of labware to be used
            triplicate: whether 'single' (triplicate = False) or 'triplicate'
            (triplicate = True) is selected
            multi: whether an 8 channel (multi = True) or single channel
            (mutli = False) p300 pipette is being used
    '''
    required_soc = (150 + 45)*96 + 300 + 90

    with open(output_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Required SOC volume (uL):', str(required_soc)])
        csvwriter.writerow('')
        csvwriter.writerow(['SOC well index (in trough):', '3'])
        csvwriter.writerow('')
        if triplicate:
            csvwriter.writerow(['Triplicate'])
        else:
            csvwriter.writerow(['Single'])
        csvwriter.writerow('')
        if multi:
            csvwriter.writerow(['P300 pipette type:', 'p300 multi'])
        else:
            csvwriter.writerow(['P300 pipette type:', 'p300 single'])
        csvwriter.writerow('')
        csvwriter.writerow(['P10 Mount:', labware_dict['p10_mount']])
        csvwriter.writerow('')
        csvwriter.writerow(['P300 Mount:', labware_dict['p300_mount']])
        csvwriter.writerow('')
        csvwriter.writerow('')
        csvwriter.writerow(['Labware', 'Labware definition', 'Position'])
        csvwriter.writerow(['New reaction plate (for competent cells)',
                            labware_dict['well_plate'], 'tempdeck (10)'])
        csvwriter.writerow(['Post-MoClo reaction plate (from assembly)',
                            labware_dict['well_plate'], '7'])
        csvwriter.writerow(['Trough (contains washes, SOC)',
                            labware_dict['trough'], '5'])
        csvwriter.writerow(['Agar plate',
                            labware_dict['agar_plate'], '2'])
        csvwriter.writerow('')


def create_protocol(
    dna_plate_map_dict: Dict[str, List],
    combinations_to_make: List[Dict],
    reagent_to_mm_dict: Dict, mm_dict: Dict,
    assembly_template_path: str, transform_template_path: str,
    output_folder_path: str, thermocycle: bool, triplicate: str, multi: bool,
    p10Mount: str, p300Mount: str, p10_type: str, p300_type: str,
    reaction_plate_type: str, reagent_plate_type: str, trough_type: str,
    agar_plate_type: str
) -> Tuple[str, str]:
    '''
        Generates the assembly and transformation protocols used by opentrons.
        Returns the paths of the assembly and transform scripts.
        Args:
            dna_plate_map_dict: the dictionary of parts
            combinations_to_make: the list of dictionaries of
            constructs
            reagent_to_mm_dict: dictionary directing where to transfer each
            reagent to to make master mixes, key = reagent well, value =
            list of tuples of reagent plate (different for water and other
            reagents), master mix well, and volume to be transferred
            mm_dict_list = mm_df rows stored as dictionaries in list
            assembly_template_path: the absolute path of the assembly template
            script
            transform_template_path: the absolute path of the transformation
            template script
            output_folder_path: the absolute path to the output folder that
            will contain the assembly and transformation protocols
            thermocycle: whether or not the Opentrons thermocycler module
            is being used
            triplicate: whether 'single' (triplicate = False) or 'triplicate'
            (triplicate = True) is selected
            multi: whether an 8 channel (multi = True) or single channel
            (mutli = False) p300 pipette is being used
            p10_mount: "left" or "right", the Opentrons pipette mount options
            p300_mount: "left" or "right", the Opentrons pipette mount options
            p10_type: the name of the p10 pipette, e.g. "p10_single"
            p300_type: the name of the p300 pipette, e.g. "p300_single"
            reaction_plate_type: the name of the well plate type used as the
            source and construct plate
            reagent_plate_type: the name of the well plate type used as the
            reagent plate (for master mix and non-water reagents)
            trough_type: the name of the trough type used for water and soc
            agar_plate_type: the name of the agar plate type used
    '''

    # Get the contents of colony_pick_template.py, which contains the body of
    # the protocol.
    with open(assembly_template_path) as assembly_template_file:
        assembly_template_string = assembly_template_file.read()
    assembly_path = output_folder_path + '/' + 'moclo_assembly_protocol.py'
    with open(assembly_path, "w+") as assembly_file:
        # Paste in plate maps at top of file.
        assembly_file.write('dna_plate_map_dict = ' +
                            json.dumps(dna_plate_map_dict) + '\n\n')
        assembly_file.write('combinations_to_make = '
                            + json.dumps(combinations_to_make) + '\n\n')
        assembly_file.write('reagent_to_mm = '
                            + json.dumps(reagent_to_mm_dict) + '\n\n')
        assembly_file.write('master_mix_dicts = '
                            + json.dumps(mm_dict) + '\n\n')
        assembly_file.write('thermocycle = ' + str(thermocycle) + '\n\n')
        assembly_file.write('pipetteMount10 = "' + p10Mount + '"\n\n')
        assembly_file.write('p10_type = "' + p10_type + '"\n\n')
        assembly_file.write(
            'reaction_plate_type = "' + reaction_plate_type + '"\n\n')
        assembly_file.write(
            'reagent_plate_type = "' + reagent_plate_type + '"\n\n')
        assembly_file.write(
            'trough_type = "' + trough_type + '"\n\n')

        # Paste the rest of the protocol.
        assembly_file.write(assembly_template_string)

    with open(transform_template_path) as transform_template_file:
        transform_template_string = transform_template_file.read()
    transform_path = output_folder_path + '/' + 'transform_moclo_protocol.py'
    with open(transform_path, "w+") as transform_file:
        # Paste in plate maps at top of file.
        transform_file.write('combinations_to_make = '
                             + json.dumps(combinations_to_make) + '\n\n')
        transform_file.write('multi = ' + str(multi) + '\n\n')
        transform_file.write('triplicate = ' + str(triplicate) + '\n\n')
        transform_file.write('pipetteMount10 = "' + p10Mount + '"\n\n')
        transform_file.write('pipetteMount300 = "' + p300Mount + '"\n\n')
        transform_file.write('p10_type = "' + p10_type + '"\n\n')
        transform_file.write('p300_type = "' + p300_type + '"\n\n')
        transform_file.write(
            'reaction_plate_type = "' + reaction_plate_type + '"\n\n')
        transform_file.write(
            'agar_plate_type = "' + agar_plate_type + '"\n\n')
        transform_file.write(
            'trough_type = "' + trough_type + '"\n\n')

        # Paste the rest of the protocol.
        transform_file.write(transform_template_string)

    return assembly_path, transform_path


'''
Below is an example of how this would be run through the command line:
To use this, replace the output_folder name, construct_path, and part_path.
'''
'''
output_folder = "C:/Users/gabri/Documents/Uni/iGEM/DJANGO-Assembly-Methods/output"
construct_path = ["C:/Users/gabri/Documents/Uni/iGEM/DJANGO-Assembly-Methods/examples/moclo_combinations.csv"]
part_path = ["C:/Users/gabri/Documents/Uni/iGEM/DJANGO-Assembly-Methods/examples/moclo_dna_map.csv"]

moclo_function('output', construct_path, part_path, thermocycle=True,
              **labware_dict)
'''
