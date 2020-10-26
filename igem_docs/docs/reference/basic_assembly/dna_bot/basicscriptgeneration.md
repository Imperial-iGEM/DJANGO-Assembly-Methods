# BASIC Script Generation

Script generation file: dnabot_app.py
Script generation run by `dnabot()` function in dnabot_app.py

The following sources were used in writing template scripts:
* [DNA-BOT: A low-cost, automated DNA assembly platform for synthetic biology](https://www.biorxiv.org/content/10.1101/832139v1)
* [BASIC: A New Biopart Assembly Standard for Idempotent Cloning Provides Accurate, Single-Tier DNA Assembly for Synthetic Biology](https://pubs.acs.org/doi/abs/10.1021/sb500356d)

## Inputs
### `output_folder`
The full path to the folder the user wants the output files to be in. The folder **must** already be made. Example: `'C:/Users/yourname/Documents/iGEM/SOAPLab/output'`

### `ethanol_well_for_stage_2`
The ethanol well used for purification, generally set as `'A11'`.

### `deep_well_plate_stage_4`
The SOC well used in tranformation, generally set as `'A1'`.

### `input_construct_path`
A list of the full path to the construct CSV file - this is simply a list of length one. If the list has more than one element, only the first element will be accessed. Example: `['C:/Users/yourname/Documents/iGEM/SOAPLab/myDesign/constructs.csv']` 

The format of a BASIC construct CSV is:
Well | Linker 1 | Part 1 | Linker 2 | Part 2 | Linker 3 | Part 3 | Linker 4 | Part 4 | Linker 5 | Part 5
------------ | ------------- | ------------- | ------------ | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | -------------
A1 | LMS | dummyBackbone | LMP | Pro | L1 | RBS | L2 | CDS | L3 | Ter


### `output_sources_paths`
A list of the full path(s) to the parts CSV file(s).
Example: `['C:/Users/yourname/Documents/iGEM/SOAPLab/myDesign/parts.csv']` 

The format of a BASIC parts/linkers CSV is:
Part/linker | Well | Part concentration (ng/uL)
------------ | ------------- | -------------
CDS | A1
L1-P | A2
L1-S | A3
L2-P | A4
L2-S | A5
L3-P | A6
L3-S | A7
LMP-P | A8
LMP-S | A9
LMS-P | A10
LMS-S | A11
Pro | A12
RBS | B1
Ter | B2
dummyBackbone | B3


### Labware parameters
#### Pipettes
`p10_mount`: `'left'` or `'right'`, indicating which mount the pipette of type `p10_type` will be mounted on.

`p300_mount`: `'left'` or `'right'`, indicating which mount the pipette of type `p300_type` will be mounted on. This only matters if the user is running the transformation protocol. Make sure the `p10_mount` and `p300_mount` are different.

`p10_type`: `'p10_single'` or `'p20_single_gen2'`, indicating the pipette used for transferring small amounts - needs a minimum transfer volume of 1 μL. Multi-channel pipettes are not permitted. 

`p300_type`: `'p300_single'`, `'p300_single_gen2'`, `'p300_multi'`, `'p300_multi_gen2'` indicating the pipette used for transferring large amounts. Multi-channel pipettes are permitted. This is only used in transformation.

See [Pipettes Python API Reference](https://docs.opentrons.com/v2/new_pipette.html) for more information on pipettes. 
#### Labware
`well_plate`: This must be an Opentrons compatible 96-well plate. The default value is `'biorad_96_wellplate_200ul_pcr'`. This plate type is used for the part plate or plates and the construct plate.
Opentrons compatible well plates can be found at: [Opentrons Labware Library: Well Plate](https://labware.opentrons.com/?category=wellPlate). Custom 96 well plates can also be created at: [Labware Creator](https://labware.opentrons.com/create).

`reagent_plate`: This must be an Opentrons compatible trough, ideally with a maximum well volume of 20 mL or above. Liquid waste, ethanol, and elution buffer is stored here. The default value is `'usascientific_12_reservoir_22ml'`.
Opentrons compatible troughs can be found at: [Opentrons Labware Libary: Reservoir](https://labware.opentrons.com/?category=reservoir). Custom troughs can also be created at: [Labware Creator](https://labware.opentrons.com/create).

`mag_plate`: This must be an Opentrons compatible 96-well plate. The default value is `'biorad_96_wellplate_200ul_pcr'`. This plate type is used as the output plate of the purification script, and thus the input plate for the assembly script. [Opentrons Labware Library: Well Plate](https://labware.opentrons.com/?category=wellPlate). Custom 96 well plates can also be created at: [Labware Creator](https://labware.opentrons.com/create).

`tube_rack`: This must be an Opentrons compatible tube rack, ideally with a maximum well volume of 1 mL or above. The master mixes for the clip protocol and assembly protocol are stored here. The default value is `'opentrons_24_tuberack_nest_1.5ml_snapcap'`.
Opentrons compatible tube racks can be found at: [Opentrons Labware Library: Tube Rack](https://labware.opentrons.com/?category=tubeRack). Custom tube racks can also be created at: [Labware Creator](https://labware.opentrons.com/create).

`aluminum_block`: This must be an Opentrons compatible 96 well aluminum block. The final assemblies are stored here. The default value is `'opentrons_96_aluminumblock_biorad_wellplate_200ul'`. Opentrons compatible aluminum blocks can be found at: [Opentrons Labware Library: Aluminum Block](https://labware.opentrons.com/?category=aluminumBlock). Custom labware can also be created at: [Labware Creator](https://labware.opentrons.com/create)

`bead_container`: This must be an Opentrons compatible trough. The magnetic beads are stored here. The default value is `'usascientific_96_wellplate_2.4ml_deep'`. Opentrons compatible troughs can be found at [Opentrons Labware Libary: Reservoir](https://labware.opentrons.com/?category=reservoir). Custom labware can also be created at: [Labware Creator](https://labware.opentrons.com/create).

`soc_plate`: A well plate or trough with a capacity of at least 2 mL per well, used to hold SOC. The default value is: `'usascientific_96_wellplate_2.4ml_deep'`. This is only used in transformation. Opentrons compatible well plates can be found at: [Opentrons Labware Library: Well Plate](https://labware.opentrons.com/?category=wellPlate), and troughs can be found at [Opentrons Labware Libary: Reservoir](https://labware.opentrons.com/?category=reservoir). Custom labware can also be created at: [Labware Creator](https://labware.opentrons.com/create).

`agar_plate`: A custom 96 well plate with the parameters of a flat rectangular agar plate. The default value is: `'thermofisher_96_wellplate_180ul'`. Custom 96 well plates can also be created at: [Labware Creator](https://labware.opentrons.com/create).

See [Labware Python API Reference](https://docs.opentrons.com/v2/new_labware.html) for more information on labware.

## The script generation process
### Overview of requirements
Name | Description
------------ | ------------- | -------------
Clip reactions | `dnabot()` must extrapolate the required clip reactions from the list of constructs, so that parts and linkers can be digested and ligated, forming linker-adapted parts. This is used by `1_clip.ot2.py`. The clip reaction wells must also be determined.
Master mix | Instructions for creating the master mix used in clip reactions need to be specified for the user.
Purification | The sample, mixing, and output wells for purification need to be specified. This is automatically done inside the purification script, but identical values are generated here so that they can be saved in metainformation.
Final assembly | The mapping between output purification wells and final assembly wells needs to be specified, as well as the volumes needed to be transferred. 
Transformation reactions | The positions used for plating are specified.
Protocols | Information must be inserted into templates, producing protocols. This includes dictionaries of transfers, labware information, and other parameters such as the ethanol well and SOC well.
Metainformation | Detailed information is saved in a CSV format. 
### Steps
#### 1. Read in and process constructs
`generate_constructs_list(input_construct_path)` reads in the constructs and returns a list of dataframes `constructs_list`. 
On each full, non-header row of the CSV, e.g. `['A1', 'LMS', 'dummyBackbone', 'LMP', 'Pro', 'L1', 'RBS', 'L2', 'CDS', 'L3', 'Ter']`, the function `process_construct()` is run on the 1st to last element (excluding the 0th element - in this case `'A1'`), returning a dataframe of clip reactions, outlining prefix linkers, parts, and suffix linkers. All odd indices (after the 0th element is removed) are assumed to be parts, and all even indices are assumed to be linkers. Each linker is converted into a prefix and suffix, with `interrogate_linker()`
appending a `'-P'` or a `'-S'`. If the last element is a part, it is assigned the first linker as its suffix. This is an example of the dataframe that will be produced:
prefixes | parts | suffixes
------------ | ------------- | -------------
LMS-P | dummyBackBone | LMP-S
LMP-P | Pro | L1-S
L1-P | RBS | L2-S
L2-P | CDS | L3-S
L3-P | Ter | LMS-S

#### 2. Generate clip reactions dataframe
`generate_clips_df(constructs_list)` returns a dataframe containing all of the unique clip reactions occurring between parts, prefixes, and suffixes. This is accomplished by merging the list of dataframes output by `generate_constructs_list()` into a single dataframe `merged_construct_dfs`, and then removing duplicates `unique_clips_df`.

`unique_clips_df` is iterated through, and for each unique clip `merged_construct_dfs` is iterated through, and all of the appearances of the unique clip in `merged_construct_dfs` are counted. This is important as each clip reaction can only supply a certain amount of constructs (e.g. 15), and therefore more than one clip may be needed. The number of clips needed is calculated by dividing the counts of the clip by the number of constructs possible per clip, and rounding up. This is then saved in the `'number'` column of the new clips dataframe, `clips_df`.

The well or wells in which the clip reactions take place, `'clip_well'` and the well or wells in which the output of the magnetic bead purification is held (output = purified linker-adapted parts) `'mag_well'` are also found and added as columns of `clips_df`. The number of clips needed also determines the number of clip wells and mag wells. Clip wells are assigned by starting from `'A1'` going forward to `'B1', 'C1'` etc., and extending at most to `'H6'` Mag wells are assigned starting from `'A7'` and extending at most to `'H12'`, the final well. 

#### 3. Read in and process parts
`generate_sources_dict(output_sources_paths)` reads in parts/linkers CSV files. The first output, `sources_dict` is a dictionary in which each key is the name of the part/linker and the value is a tuple of the CSV values read in e.g. well, possible concentration, and plate deck position (dependent on how many CSV files there are). The second output, `parts_df` is a datframe with the columns `'name', 'well', 'concentration', 'plate'`. If the concentration is left empty in the CSV file, a default concentration of 200 ng/µL is assumed.

#### 4. Fill parts dataframe
`fill_parts_df(clips_df, parts_df)` adds the columns `'clip_well', 'mag_well', 'total_vol', 'vol_per_clip', 'number'` to the parts dataframe. `'clip_well'`, `'mag_well'`, and `'number'` are found by iterating through the the clips dataframe and finding all of the clips with a given part in them. `'clip_well'` is then a list of all of the clip wells the part will be transferred into, `'mag_well'` is a list of all of the mag wells the part will end up in, and `'number'` is the sum of all of the numbers of the clips in the clips dataframe the part is in. `'vol_per_clip'` is determined with the value of concentration for parts (different for linkers), as 200 ng of the part is required per clip and therefore the volume per clip = concentration/amount per clip. For linkers, a volume of 1 µL per clip is assumed. The total volume needed of a part is found by multiplying the number value by the volume per clip and then adding a dead volume of 15 µL (if number > 0). 

#### 5. Create clips dictionary
`generate_clips_dict(clips_df, sources_dict, parts_df)` generates a dictionary of clips, designed to be used by the first clip protocol, and with the keys `'prefixes_wells', 'prefixes_plates', 'suffixes_wells', suffixes_plates', 'parts_wells',` `'parts_plates', 'parts_vols', 'water_vols'`.

The clips dataframe is iterated through row by row.

The well of the prefix of the clip is found in the sources_dict, e.g. `'A1'`. This is turned into a list of the same length as the clip's number: e.g. `['A1']*2 = ['A1', 'A1']` if number = 2. This list is added to the values of `clips_dict['prefixes_wells']` - forming part of a larger list. The same procedure is done for the parts wells and suffix wells, and the prefix, part, and suffix plates - the deck position of a part/linker found from the `sources_dict` and turned to a list of length = clip number.

The part volume per clip (parts only as linkers volume per clip = 1 µL) is calculated from the concentration, and saved in the same format of part of a larger list in the value for the key `'parts_vols'`.

The water volume is calculated by the equation `CLIP_VOL - (T4_BUFF_VOL + BSAI_VOL + T4_LIG_VOL + CLIP_MAST_WATER + 2) - part_vol = 30 - (3 + 1 + 0.5 + 15.5 + 2) - part_vol = 8 - part_vol`. It is also stored as a list in a list of lists.

Example dictionary:
```
clips_dict = {
  "prefixes_wells": ["A10", "A8", "A2", "A4", "A6"],
  "prefixes_plates": ["2", "2", "2", "2", "2"],
  "suffixes_wells": ["A9", "A3", "A5", "A7", "A11"],
  "suffixes_plates": ["2", "2", "2", "2", "2"],
  "parts_wells": ["B3", "A12", "B1", "A1", "B2"],
  "parts_plates": ["2", "2", "2", "2", "2"],
  "parts_vols": [1, 1, 1, 1, 1],
  "water_vols": [7.0, 7.0, 7.0, 7.0, 7.0]}
```

#### 6. Generate final assembly dictionary
`generate_final_assembly_dict(constructs_list, clips_df, parts_df)` finds the mapping of mag wells to construct wells, producing a dictionary `final_assembly_dict` with keys = construct wells, values = list of mag wells. The clips and parts dataframe are also updated with the column `construct_well`, containing a list of the construct wells the part/linker or clip is used in. 

`constructs_list` is iterated through, with each element being a dataframe of the clip reactions needed for the construct. This is then matched with the clip reaction in `clips_df`, getting the list of mag wells for the clip. The mag well to use is found by dividing the clip count, the number of times a clip has been encountered in the iteration so far, by the number of assemblies per clip (15). This mag well is then appended to the value corresponding to the construct well key. As rows in `clips_df` are already being matched with constructs, it made sense to fill in their construct wells during this process. It was easy to match parts and linkers with constructs as well, filling in the construct wells column of the parts dataframe.

An example of the final assembly dictionary:
`{"A1": ["A7", "B7", "C7", "D7", "E7"]}`

An example of the full parts dataframe:
concentration | name | well | plate | clip_well | mag_well | total_vol | vol_per_clip | number | construct_well
------------ | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------ | ------------
200 | CDS | A1 | 2 | ['D1'] | ['D7'] | 16 | 1 | 1 | ['A1']
200 | L1-P | A2 | 2 | ['C1'] | ['C7'] | 16 | 1 | 1 | ['A1']
200 | L1-S | A3 | 2 | ['B1'] | ['B7'] | 16 | 1 | 1 | ['A1']
200 | L2-P | A4 | 2 | ['D1'] | ['D7'] | 16 | 1 | 1 | ['A1']
200 | L2-S | A5 | 2 | ['C1'] | ['C7'] | 16 | 1 | 1 | ['A1']
200 | L3-P | A6 | 2 | ['E1'] | ['E7'] | 16 | 1 | 1 | ['A1']
200 | L3-S | A7 | 2 | ['D1'] | ['D7'] | 16 | 1 | 1 | ['A1']
200 | LMP-P | A8 | 2 | ['B1'] | ['B7'] | 16 | 1 | 1 | ['A1']
200 | LMP-S | A9 | 2 | ['A1'] | ['A7'] | 16 | 1 | 1 | ['A1']
200 | LMS-P | A10 | 2 | ['A1'] | ['A7'] | 16 | 1 | 1 | ['A1']
200 | LMS-S | A11 | 2 | ['E1'] | ['E7'] | 16 | 1 | 1 | ['A1']
200 | Pro | A12 | 2 | ['B1'] | ['B7'] | 16 | 1 | 1 | ['A1']
200 | RBS | B1 | 2 | ['C1'] | ['C7'] | 16 | 1 | 1 | ['A1']
200 | Ter | B2 | 2 | ['E1'] | ['E7'] | 16 | 1 | 1 | ['A1']
200 | dummyBackbone | B3 | 2 | ['A1'] | ['A7'] | 16 | 1 | 1 | ['A1']

An example of the full clips dataframe:
prefixes | parts | suffixes | number | clip_well | mag_well | construct_well
------------ | ------------- | ------------- | ------------- | ------------- | ------------- | -------------
LMS-P | dummyBackbone | LMP-S | 1 | ('A1') | ('A7') | ['A1']
LMP-P | Pro | L1-S | 1 | ('B1') | ('B7') | ['A1']
L1-P | RBS | L2-S | 1 | ('C1') | ('C7') | ['A1']
L2-P | CDS | L3-S | 1 | ('D1') | ('D7') | ['A1']
L3-P | Ter | LMS-S | 1 | ('E1') | ('E7') | ['A1']

#### 7. Generate spotting tuples
`spotting_tuples = generate_spotting_tuples(constructs_list, SPOTTING_VOLS_DICT)` uses the list of construct dataframes to generate a spotting tuple for every column of constructs. This function assumes that the 1st construct is located in well A1 and wells increase linearly. Target wells locations are equivalent to construct well locations and spotting volumes are defined by `SPOTTING_VOLS_DICT`. This is used by the transformation script. 

#### 8. Create protocols
`generate_ot2_script(full_output_path, FNAME, os.path.join(template_dir_path, TEMP_FNAME), **kwargs)` is used to generate each of the protocols, with `FNAME` being the output protocol file name, e.g. `1_clip.ot2.py`, and `TEMP_FNAME` being the template name, e.g. `clip_template.py`. The keyword arguments are used to insert whatever is needed for each template script, e.g. `clips_dict` for the clip protocol. The path to the output protocol is returned by this function.

#### 9. Define master mix
`generate_master_mix_df(clips_df['number'].sum())` generates the master mix for the user to make based on the number of clips needed in total. `T4_BUFF_VOL`, `CLIP_MAST_WATER`, `BSAI_VOL`, and `T4_LIG_VOL` are all multipled by the number of clips + 2, accounting for dead volume. 

An example master mix dataframe is:
Component | Volume (uL)
------------ | -------------
Promega T4 DNA Ligase buffer, 10X | 21.0
Water | 108.5
NEB BsaI-HFv2 | 7.0
Promega T4 DNA Ligase | 3.5

#### 10. Save metainformation
The metainformation is then saved by writing the dataframes and dictionaries to CSV files. 
