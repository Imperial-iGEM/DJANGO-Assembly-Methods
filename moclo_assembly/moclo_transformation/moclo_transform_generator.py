# Modified version 27/07/20

import os
import tkinter
from tkinter import filedialog, messagebox
import csv
import json
import yaml

###############################################################################
# Constants
###############################################################################

# CONFIG_PATH = "data/settings.yaml"

###############################################################################
# Main function of script
###############################################################################

# all variables for the function
# config = {'output_folder_path': 'output'}
# combinations_limit = 'single'
# dna_plate_map_filename = '/Users/Benedict/Documents/MoClo/OT2-MoClo-Transformation-Ecoli/examples/input_DNA_plate_csv/input-dna-map.csv'
# combinations_filename = '/Users/Benedict/Documents/MoClo/OT2-MoClo-Transformation-Ecoli/examples/combination_to_make_csv/combination-to-make-72.csv'
# moclo_function('output','single','/Users/Benedict/Documents/MoClo/OT2-MoClo-Transformation-Ecoli/examples/input_DNA_plate_csv/input-dna-map.csv','/Users/Benedict/Documents/MoClo/OT2-MoClo-Transformation-Ecoli/examples/combination_to_make_csv/combination-to-make-72.csv')


def moclo_function(output_folder, single_or_triplicate, dna_plate_map, combinations_file):

    # GETTING USER INPUT

    # config = get_config(CONFIG_PATH)
    # ^ returns config just a read of setting.yaml hopefull try to set to
    # string and still work
    config = {'output_folder_path': output_folder,
              'assembly_template_path':
              'moclo_assembly/moclo_transformation/data/moclo_assembly_template.py',
              'transform_template_path':
              'moclo_assembly/moclo_transformation/data/transform_moclo_template.py'}

    # combinations_limit = ask_single_or_triplicate()
    # ^ return the string either 'single' or triplet
    combinations_limit = single_or_triplicate
    
    # whether user wants to use p300 multi or single channel
    # multi = get_multi() in offline vers
    multi = False
    
    # whether user wants to use thermocycler module
    # thermocycle = get_thermocycle() in offline vers
    thermocycle = True

    # dna_plate_map_filename = ask_dna_plate_map_filename()
    # ^ return string of full disk file path of dna plate map
    dna_plate_map_filename = dna_plate_map

    # combinations_filename = ask_combinations_filename()
    # ^ returns string of full disk path of combinations file
    combinations_filename = combinations_file

    # Load in CSV files as a dict containing lists of lists.
    dna_plate_map_dict = generate_plate_maps(dna_plate_map_filename)
    combinations_to_make = generate_combinations(combinations_filename)
    check_number_of_combinations(combinations_limit, combinations_to_make)

    # Generate and save output plate maps.
    triplicate = generate_and_save_output_plate_maps(combinations_to_make,
                                                     combinations_limit,
                                                     config['output_folder_path'])

    # Create a protocol file and hard code the plate maps into it.
    create_protocol(dna_plate_map_dict, combinations_to_make,
                    config['assembly_template_path'],
                    config['transform_template_path'],
                    config['output_folder_path'], thermocycle,
                    triplicate, multi)

###############################################################################
# Functions for getting user input
###############################################################################


def get_config(config_path):

    # Load settings from file.
    config = yaml.safe_load(open(config_path))

    # Create a tkiner window and hide it (this will allow us to create dialog
    # boxes)
    window = tkinter.Tk()
    window.withdraw()

    # Ask user to set output folder if not set.
    if not config['output_folder_path']:
        messagebox.showinfo("Choose output folder",
                            "You will now select the folder to save the "
                            "protocol and plate maps to. This can be changed "
                            "later by editing settings.yaml in the "
                            "OT2_MoClo_JoVE/moclo_transform/data folder.")
        config['output_folder_path'] = filedialog.askdirectory(
            title="Choose output folder")
        with open(config_path, "w+") as yaml_file:
            yaml_file.write(yaml.dump(config))

    return config


# Ask user in command line whether they want single combinations or triplicates
# Max number of combinations if single is 88 (11 unique columns), and if
# triplicate is 24 (3 unique columns, each repeated 3 times)


def ask_single_or_triplicate():
    return str(input("Enter 'single' if you want to run at most 88 single"
                     "combinations or 'triplicate' if you want to run at most"
                     "24 triplicate combinations: "))


def ask_dna_plate_map_filename():

    # Create tkinter window in background to allow us to make dialog boxes.
    window = tkinter.Tk()
    window.withdraw()

    # Open dialog boxes asking user for dna plate map.
    dna_plate_map_filename = filedialog.askopenfilename(
        title="Select DNA plate map",
        filetypes=(("CSV files", "*.CSV"), ("all files", "*.*")))

    return dna_plate_map_filename


def ask_combinations_filename():
    # Create tkinter window in background to allow us to make dialog boxes.
    window = tkinter.Tk()
    window.withdraw()

    # Open dialog boxes asking user for combinations file.
    combinations_filename = filedialog.askopenfilename(
        title="Select file containing combinations to make.",
        filetypes=(("CSV files", "*.CSV"), ("all files", "*.*")))

    return combinations_filename


def generate_plate_maps(filename):
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


def generate_combinations(combinations_filename):
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
    # print("combinations_to_make", combinations_to_make))
    return combinations_to_make


def check_number_of_combinations(combinations_limit, combinations_to_make):
    number_of_combinations = len(combinations_to_make)
    if combinations_limit == 'single':
        if number_of_combinations > 88:
            raise ValueError('Too many combinations ({0}) requested.'
                             'Max for single combinations is'
                             '88.'.format(number_of_combinations))
    elif combinations_limit == 'triplicate':
        if number_of_combinations > 24:
            raise ValueError('Too many combinations ({0}) requested.'
                             'Max for triplicate combinations is'
                             '24.'.format(number_of_combinations))

###############################################################################
# Functions for creating output files
###############################################################################


def generate_and_save_output_plate_maps(combinations_to_make,
                                        combinations_limit,
                                        output_folder_path):
    # Split combinations_to_make into 8x6 plate maps.
    output_plate_map_flipped = []
    for i, combo in enumerate(combinations_to_make):
        name = combo["name"]
        # if i % 32 == 0:
        #   # new plate
        #   output_plate_maps_flipped.append([[name]])

        if i % 8 == 0:
            # new column
            output_plate_map_flipped.append([name])

        else:
            output_plate_map_flipped[-1].append(name)

    print("output_plate_map_flipped", output_plate_map_flipped)

    # Correct row/column flip.
    output_plate_map = []
    for i, row in enumerate(output_plate_map_flipped):
        for j, element in enumerate(row):
            if j >= len(output_plate_map):
                output_plate_map.append([element])
            else:
                output_plate_map[j].append(element)

    print("output_plate_map", output_plate_map)
    
    triplicate = False # false unless otherwise

    # creating an output plate three copies of each column
    if combinations_limit == 'triplicate':
        triplicate = True
        combinedRow = []
        splitRows = []

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
    return triplicate


def create_protocol(dna_plate_map_dict, combinations_to_make,
                    assembly_template_path, transform_template_path,
                    output_folder_path, thermocycle, triplicate, multi):

    # Get the contents of colony_pick_template.py, which contains the body of
    # the protocol.
    with open(assembly_template_path) as assembly_template_file:
        assembly_template_string = assembly_template_file.read()
    with open(output_folder_path + '/' + 'moclo_assembly_protocol.py',
              "w+") as assembly_file:
        # Paste in plate maps at top of file.
        assembly_file.write('dna_plate_map_dict = ' +
                            json.dumps(dna_plate_map_dict) + '\n\n')
        assembly_file.write('combinations_to_make = '
                            + json.dumps(combinations_to_make) + '\n\n')
        assembly_file.write('thermocycle = ' + str(thermocycle) + '\n\n')

        # Paste the rest of the protocol.
        assembly_file.write(assembly_template_string)

    with open(transform_template_path) as transform_template_file:
        transform_template_string = transform_template_file.read()
    with open(output_folder_path + '/' + 'transform_moclo_protocol.py',
              "w+") as transform_file:
        # Paste in plate maps at top of file.
        transform_file.write('combinations_to_make = '
                             + json.dumps(combinations_to_make) + '\n\n')
        transform_file.write('multi = ' + str(multi) + '\n\n')
        transform_file.write('triplicate = ' + str(triplicate) + '\n\n')

        # Paste the rest of the protocol.
        transform_file.write(transform_template_string)

###############################################################################
# Call main function
###############################################################################


# if __name__ == '__main__':
#    main()
