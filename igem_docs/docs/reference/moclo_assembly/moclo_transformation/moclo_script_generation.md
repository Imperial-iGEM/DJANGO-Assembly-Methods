# MoClo Script Generation
Script generation file: moclo_transform_generator.py
Script generation run by `moclo_function()` function in moclo_transform_generator.py

The following sources were used in writing template scripts:
* [Automated Robotic Liquid Handling Assembly of Modular DNA Devices](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5755516/)
* [A Modular Cloning System for Standardized Assembly of Multigene Constructs](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3041749/)
* [Synthetic DNA Assembly Using Golden Gate Cloning and the Hierarchical Modular Cloning Pipeline](https://currentprotocols.onlinelibrary.wiley.com/doi/full/10.1002/cpmb.115)
* [OT2 Modular Cloning (MoClo) and Transformation in E. coli Workflow](https://github.com/DAMPLAB/OT2-MoClo-Transformation-Ecoli)

## Inputs
### `output_folder`
The full path to the folder the user wants the output files to be in. The folder **must** already be made. Example: `'C:/Users/yourname/Documents/iGEM/SOAPLab/output'`

### `construct_path`
A list of the full path to the construct CSV file - this is simply a list of length one. If the list has more than one element, only the first element will be accessed. Example: `['C:/Users/yourname/Documents/iGEM/SOAPLab/myDesign/constructs.csv']` 

The format of a MoClo constructs csv is:

construct name | part1 | part2 | part3 | part4
------------ | ------------- | ------------ | ------------- | -------------
construct1 | pICH47742 | Bba_J23119 | BBa_K1114211 | pC0_069
construct2 | pICH47732 | Bba_J23102 | pC0_009 | pC0_062
construct3 | pICH47732 | BBa_J23100 | pC0_009 | pC0_062
construct4 | pICH47732 | BBa_J23114 | pC0_009 | pC0_062
construct5 | pICH47732 | BBa_J23106 | pC0_009 | pC0_062
construct6 | pICH47742 | BBa_J23100 | BBa_K1114211 | pC0_069
construct7 | pICH47742 | BBa_J23106 | BBa_K1114211 | pC0_069
construct8 | pICH47742 | BBa_J23114 | BBa_K1114211 | pC0_069
construct9 | pICH47732 | Bba_J23119 | pC0_009 | pC0_062
construct10 | pICH47742 | Bba_J23102 | BBa_K1114211 | pC0_069

The names at the top are shown purely for reference - there is no header in the CSV file. There can be a minimum of 2 parts per construct and a maximum of 8: four parts constructs are only shown here for reference.

### `part_path`
A list of the full path(s) to the parts CSV file(s).
Example: `['C:/Users/yourname/Documents/iGEM/SOAPLab/myDesign/parts.csv']` 

The format of a MoClo parts CSV is:
 |  |  |  |  |  |  |  |  |  |  | 
------------ | ------------- | ------------ | ------------- | ------------- | ------------ | ------------- |------------ | ------------- | ------------- | ------------- | ------------- 
BBa_J23100 | BBa_J23106 | BBa_J23114 | BBa_K1114211 | Bba_J23102 | Bba_J23119 | pC0_009 | pC0_062 | pC0_069 | pICH47732 | pICH47742 | 
 |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  |  |  |  |  | 
 |  |  |  |  |  |  |  |  |  |  | 

There are 8 rows and 12 columns in this format, and each position corresponds to a well, with wells being filled if there is a part name in them.

### `thermocycle`
A Boolean value indicating whether the user has the thermocycler module and would like to use it in the protocols (`True`), or not (`False`). 

For information on the thermocycler module, see:
* [Opentrons store page](https://shop.opentrons.com/products/thermocycler-module)
* [Hardware modules Python API reference](https://docs.opentrons.com/v2/new_modules.html)

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

`trough`: This must be an Opentrons compatible trough, ideally with a maximum well volume of 20 mL or above. Water, the washes (washes may be removed in future), and SOC is stored here. The default value is `'usascientific_12_reservoir_22ml'`.
Opentrons compatible troughs can be found at: [Opentrons Labware Libary: Reservoir](https://labware.opentrons.com/?category=reservoir). Custom troughs can also be created at: [Labware Creator](https://labware.opentrons.com/create).

`reagent_plate`: This must be an Opentrons compatible 96-well plate. The default value is `'biorad_96_wellplate_200ul_pcr'`. This plate type is used for the reagents, not including water or the master mixes.
Opentrons compatible well plates can be found at: [Opentrons Labware Library: Well Plate](https://labware.opentrons.com/?category=wellPlate). Custom 96 well plates can also be created at: [Labware Creator](https://labware.opentrons.com/create).

`agar_plate`: A custom 96 well plate with the parameters of a flat rectangular agar plate. The default value is: `'thermofisher_96_wellplate_180ul'`. Custom 96 well plates can also be created at: [Labware Creator](https://labware.opentrons.com/create).

See [Labware Python API Reference](https://docs.opentrons.com/v2/new_labware.html) for more information on labware.


## The script generation process
### Overview of requirements
Name | Description
------------ | ------------- | -------------
Reagents and master mixes | `moclo_function()` must define master mixes and reagents, the reagents being ligase, restriction enzyme (e.g. BsaI or BpiI), buffer, and water. Water is stored in the first well of the trough, and given a required volume of 1.5 mL as this is guaranteed to be both significantly above the actual required volume and below the maximum volume per well (2.2 mL). The volumes of ligase, restriction enzyme, and buffer are dependent on which master mixes need to be created, and reagent wells are mapped to master mix wells. More than one master mix for the same number of parts per assembly if often needed, as there is not sufficient master mix per well to supply more than a few assemblies. More than one master mix for the same number of parts per assembly if often needed, as there is not sufficient master mix per well to supply more than a few assemblies.
Master mixes | Three master mixes must be defined, for use in upstream digests, downstream digests, and plasmid digests. Per digest, each master mix has 1 μL of one enzyme, 1 μL of another enzyme, and 5μL of NEB Buffer 10X. The enzymes are EcoRI and SpeI for the upstream master mix, XbaI and PstI for the downstream master mix, and EcoRI and PstI for the plasmid master mix. Enough must be made so that there is 7 μL per digest plus two digests worth of dead volume (14 μL)
Agar plate | The locations of each assembly's transformation on an agar plate must be specified, and saved as a CSV.
Protocols | Information must be inserted into templates, producing protocols. This includes dictionaries of transfers, labware information, and other parameters such as whether to use the thermocycle module.
Metainformation | Detailed information is saved in a CSV format. 

### Steps

#### 1. Read in and save parts in dictionary
Create dictionaries for each part path, with the key = part CSV name, values = list of lists of parts. Combine dictionaries if there are multiple part paths, to form `dna_plate_map_dict`. Uses the function `generate_plate_maps(path)`.

#### 2. Read in and save constructs in list of dictionaries
`generate_combinations(construct_path)` returns a list of dictionaries, `combinations_to_make`, in which each dictionary corresponds to a construct, with one key - the construct name, and one value - the list of parts in the construct.

#### 3. Generate agar plate positions and save in CSV
`generate_and_save_output_plate_maps(combinations_to_make, combinations_limit, config['output_folder_path'])` allocates positions for each transformed construct to be placed on the agar plate. A CSV of the form `agar_plate.csv` is generated. This returns `triplicate` and `agar_path` - `triplicate` should be ignored as at this point it simply returns `False`. `agar_path` is the path to `agar_plate.csv`.

#### 4. Create assembly metainformation and save in CSV
`create_metainformation(assembly_metainformation_path, dna_plate_map_dict, combinations_to_make,` `labware_dict, thermocycle, triplicate)` is responsible for producing a parts dataframe (`parts`), a constructs dataframe (`comb`), a master mix dataframe (`mm`), and a reagents dataframe (`reagents`). It saves all this information in the path given by `assembly_metainformation_path`, which will end with `assembly_metainformation.csv`.

The parts dataframe is created with `parts_df = create_parts_df(dna_plate_map_dict)`, which is called by `create_metainformation()`. The parts dataframe is generating by iterating through the keys values of `dna_plate_map_dict`, and converting the position of parts in a list of lists to a well, e.g. `'A1'`. The columns are `'name', 'well', 'plate', 'combinations'`. The plate column is filled with the keys of `dna_plate_map_dict`, and the combinations column is filled with dummy placeholders.

The construct dataframe `combinations_df` is created by iterating through the list of dictionaries `combinations_to_make`. The index is converted into a well name with `index_to_well_name(comb_index)`. The combinations column of `parts_df` is filled with a list of the names of constructs that contain the part. 

The master mix dataframe is created by `mm_df = create_mm_df(combinations_df)`. The columns of the master mix dataframe are: `'well', 'no_parts', 'vol_per_assembly', 'combinations', 'no_assemblies', 'buffer_vol',` `'ligase_vol', 'enzyme_vol', 'water_vol', 'plate'` The well is chosen from one of the free wells on the construct plate, first filling the last well and working backwards (i.e. filling `'H12'`, then `'G12'`, then `'F12'`, etc.).
`'no_parts'` is a number from 2 to 8, depending on how many parts there are in constructs. Different master mixes need to be created for different numbers of parts. `'combinations'` gives the names of the constructs the master mix will be used in making. `no_assemblies` is the number of assemblies the master mix can be used in. The buffer volume, ligase volume, enzyme volume, and water volume dictate the different volumes in μL needed to create the master mix.

The reagents dataframe is defined by `reagents_df = create_reagents_df(mm_df)`, and has the columns: `'name', 'well', 'plate', 'volume', 'mm_wells'`. This defines all of the reagents used, including those used in making the master mix, and their respective required volumes. There may need to be more than one well per reagent. `mm_wells` gives the master mix wells the reagent is used in.

#### 5. Obtain reagent and master mix dictionaries
`reagent_to_mm_dict, mm_dict = get_mm_dicts(mm, reagents)` generates dictionaries that can be used to direct master mix creation and distribution in the assembly protocol. `reagent_to_mm_dict` has keys as the reagent well, and values as a list of tuples, with each tuple equaling (plate the reagent is in, master mix well, volume to be transferred). `mm_dict` is simply `mm_df` in dictionary form.

#### 6. Create assembly and transformation protocols
`create_protocol()` inserts dictionaries and non-path input parameters into template files, saving them as protocols. The paths of the assembly protocol and transform protocol are returned.
