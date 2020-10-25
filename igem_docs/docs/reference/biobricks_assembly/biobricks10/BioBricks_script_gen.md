# BioBricks Script Generation
Script generation file: bbinput.py
Script generation run by `biobricks()` function in bbinput.py

The following sources were used in writing template scripts:
* [NEB BioBrick Assembly](https://international.neb.com/applications/cloning-and-synthetic-biology/dna-assembly-and-cloning/biobrick-assembly)
* [Uppsala BioBrick Manual](http://2013.igem.org/wiki/images/1/1c/Uppsala2013_BioBrick_Assembly_Manual.pdf)
* [BioBrick Assembly Standards and Techniques and Associated Software Tools](https://link.springer.com/protocol/10.1007%2F978-1-62703-764-8_1)

## Inputs
### `output_folder`
The full path to the folder the user wants the output files to be in. The folder **must** already be made. Example: `'C:/Users/yourname/Documents/iGEM/SOAPLab/output'`

### `construct_path`
A list of the full path to the construct CSV file - this is simply a list of length one. If the list has more than one element, only the first element will be accessed. Example: `['C:/Users/yourname/Documents/iGEM/SOAPLab/myDesign/constructs.csv']` 

The format of a BioBricks constructs CSV is:
Construct | Well | Upstream | Downstream | Plasmid
------------ | ------------- | -------------| -------------| -------------
pro_rbs_1_Var_BBa_J23119	| A1 |	BBa_J23119 |	BBa_B0030	| ColE1_AmpR
cds_ter_2_Var_BBa_I746916 |	A2 |	BBa_I746916 |	BBa_B0015	| ColE1_AmpR
pro_rbs_1_Var_BBa_J23108 | A3 | BBa_J23108 |BBa_B0030 | ColE1_AmpR
cds_ter_1_Var_BBa_I746916 | A4 | BBa_I746916 | BBa_B0015 | ColE1_AmpR
cds_ter_2_Var_BBa_E1010	| A5 | BBa_E1010 | BBa_B0015 | ColE1_AmpR
pro_rbs_2_Var_BBa_J23119 | A6 | BBa_J23119 | BBa_B0030 | ColE1_AmpR
pro_rbs_2_Var_BBa_J23108 | A7 | BBa_J23108 | BBa_B0030 | ColE1_AmpR
cds_ter_1_Var_BBa_E1010	| A8 |BBa_E1010 | BBa_B0015 | ColE1_AmpR


### `part_path`
A list of the full path(s) to the construct CSV file(s). Only two plate can be handled - if the list is longer than length 2, only the first two paths will be used. The first path will be assigned the deck position '2', and the second path (if given) the deck position '5'.
Example: `['C:/Users/yourname/Documents/iGEM/SOAPLab/myDesign/parts.csv']` 

The format of a BioBricks parts CSV is:
Part/linker | Well | Part concentration (ng/uL)
------------ | ------------- | -------------
BBa_B0015 |	A1 |	100
BBa_B0030	| A2 | 100
BBa_E1010	| A3 | 100
BBa_I746916 |	A4 | 100
BBa_J23108 | A5	| 100
BBa_J23119 | A6 | 100
ColE1_AmpR | A7	| 100

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

`p300_type`: `'p300_single'` or `'p300_single_gen2'`, indicating the pipette used for transferring large amounts. Multi-channel pipettes are not permitted. This is only used in transformation.

See [Pipettes Python API Reference](https://docs.opentrons.com/v2/new_pipette.html) for more information on pipettes. 
#### Labware
`well_plate`: This must be an Opentrons compatible 96-well plate. The default value is `'biorad_96_wellplate_200ul_pcr'`. This plate type is used for the part plate or plates, the digest plate, and the construct plate. 
Opentrons compatible well plates can be found at: [Opentrons Labware Library: Well Plate](https://labware.opentrons.com/?category=wellPlate). Custom 96 well plate can also be created at: [Labware Creator](https://labware.opentrons.com/create).

`tube_rack`: This must be an Opentrons compatible tube rack, ideally with a maximum well volume of 1 mL or above. The reagents will be stored here. The default value is `'opentrons_24_tuberack_nest_1.5ml_snapcap'`.
Opentrons compatible tube racks can be found at: [Opentrons Labware Library: Tube Rack](https://labware.opentrons.com/?category=tubeRack). Custom tube racks can also be created at: [Labware Creator](https://labware.opentrons.com/create).

`soc_plate`: A well plate or trough with a capacity of at least 2 mL per well, used to hold SOC. The default value is: `'usascientific_96_wellplate_2.4ml_deep'`. This is only used in transformation. Opentrons compatible well plates can be found at: [Opentrons Labware Library: Well Plate](https://labware.opentrons.com/?category=wellPlate), and troughs can be found at [Opentrons Labware Libary: Reservoir](https://labware.opentrons.com/?category=reservoir). Custom labware can also be created at: [Labware Creator](https://labware.opentrons.com/create).

`transformation_plate`: A 96 well plate with a capacity of at least 300 μL per well, used to hold the transformed cells in the tranformation protocol. The default value is: `'corning_96_wellplate_360ul_flat'` Opentrons compatible well plates can be found at: [Opentrons Labware Library: Well Plate](https://labware.opentrons.com/?category=wellPlate). Custom 96 well plate can also be created at: [Labware Creator](https://labware.opentrons.com/create).

See [Labware Python API Reference](https://docs.opentrons.com/v2/new_labware.html) for more information on labware.

## The script generation process
### Overview of requirements
Name | Description
------------ | ------------- | -------------
Digests | `biobricks()` must determine the digests needed to be created as intermediary steps between parts and constructs. Each part must be mapped to a digest, and each digest must be mapped to a construct or constructs.
Master mixes | Three master mixes must be defined, for use in upstream digests, downstream digests, and plasmid digests. Per digest, each master mix has 1 μL of one enzyme, 1 μL of another enzyme, and 5μL of NEB Buffer 10X. The enzymes are EcoRI and SpeI for the upstream master mix, XbaI and PstI for the downstream master mix, and EcoRI and PstI for the plasmid master mix. Enough must be made so that there is 7 μL per digest plus two digests worth of dead volume (14 μL)
Reagents | The reagents needed and their volumes and wells are specified in tandem with defining the master mixes. The reagents needed are upstream master mix, downstream master mix, plasmid master mix, T4 Ligase Buffer 10X, and T4 Ligase.
Transformation reactions | The function must determine the transformation reactions needed to occur, combining competent cells with assemblies and control cells with water.
Protocols | Information must be inserted into templates, producing protocols. This includes dictionaries of transfers, labware information, and other parameters such as whether to use the thermocycle module.
Metainformation | Detailed information is saved in a CSV format. 

### Steps
This is a simplified list of the steps the function `biobricks()` takes in order to produce the output files.
#### 1. Read in constructs
Read in constructs CSV file with `get_constructs(construct_path)`, in which `construct_path = construct_path[0]` is run beforehand, and save as a dataframe of constructs. The construct dataframe `constructs` and a list of construct wells `dest_wells` are returned.

The function `process_construct()` is called for each full row of the construct CSV, returning a dictionary. The dictionary is converted into a dataframe and appended to a list of dataframes, which is then merged, producing the construct dataframe.

The constructs dataframe has the columns `'name', 'well', 'upstream', 'downstream', 'plasmid'`. `dest_wells` is equal to the entries in the `'well'` column. See Constructs under Metainformation for an example and an explanation of all of the columns. 

#### 2. Read in parts
Read in a list of parts CSV files with `get_parts(part_paths, constructs)`. This returns a dataframe of parts `parts`. The function `process_part()` is called on each full row of the CSV file or files, returning a dictionary. The dictionary is converted into a dataframe and appended to a list of dataframes, which is then merged, producing the parts dataframe.

The parts dataframe has the columns `'name', 'well', 'occurences', 'roles', 'digests', 'concentration', 'part_vol',` `'water_vol', 'part_vol_tot', 'water_vol_tot', 'constructs_in', 'plates'`. See Parts under Metainformation for an example and an explanation of all of the columns. Note that at this point the parts dataframe is incomplete, and will go through more processing before it is saved in metainformation.

#### 3. Specify reagents and master mixes
Uses the function `get_reagents_wells(constructs, parts)` to obtain a dataframe of reagents `reagents`, a list of reagent wells `reagents_well_list`, and a dataframe of master mixes `mm_df`.

The reagents are: `'water', 'mm_upstream', 'mm_downstream', 'mm_plasmid', 'T4Ligase10X', 'T4Ligase'`

The total amount of water needed for digestion is found by summing the `'water_vol_tot'` column of the parts dataframe. The total amount of water needed for digestion is found by multiplying the amount of water needed for ligation (11 μL) with the total number of constructs.  The volume of water in total needed is the sum of these two values, plus a minimum dead volume of 10 μL. The minimum dead volume could also be found by adding two times the transfer volume needed, but as transfer volumes are variable it was easier to simply add 10 μL.

The number of upstream digests, downstream digests, and plasmid digests are calculated by iterating through the parts dataframe and adding one to a counter for a digest type everytime that digest type is found in the part `'roles'`. 

The volume of the upstream digest master mix (`'mm_upstream'`) is found by multiplying the master mix volume needed per digest (7 μL) by the number of upstream digests, and then adding 14 μL to account for dead volume. 14 μL is used here as it is above our minimum dead volume of 10 μL, and is also equal to the volume needed for two digests.

The same procedure for finding the volume of the upstream master mix (`'mm_upstream'`) is also carried out for the downstream and plasmid master mixes (`'mm_downstream', 'mm_plasmid'`), multiplying 7 μL by the number of downstream digests and plasmid digests respectively, and adding dead volumes of 14 μL. 

`'T4Ligase10X'` refers to T4 Ligase Buffer 10X. 2 μL is used in ligation, making the total volume used equal to 2 μL times the number of constructs. 10 μL is chosen as the added dead volume as using the alternate formula (2 times transfer volume) gives a dead volume of only 4 μL.

`'T4Ligase'` refers to T4 Ligase. 1 μL is used in ligation, making the total volume used equal to 1 μL times the number of constructs. 10 μL is chosen as the added dead volume as using the alternate formula (2 times transfer volume) gives a dead volume of only 2 μL.

The master mix dataframe has the columns: `'reagent', 'volume in upstream mm', 'volume in downstream mm', 'volume in plasmid mm'`. The reagents are: `'NEB Buffer 10X', 'EcoRI-HF', 'SpeI', 'XbaI', 'PstI'`.

Per digest, each master mix contains:
* 5 μL NEB Buffer 10X
* 1 μL restriction enzyme 1
* 1 μL restriction enzyme 2

Accounting for dead volume, a table of the following form is produced:
reagent | volume in upstream mm | volume in downstream mm | volume in plasmid mm
| ------------- | ------------- | ------------- | -------------
NEB Buffer 10X | 5 μL x (no_upstream + 2) | 5 μL x (no_downstream + 2) | 5 μL x (no_plasmid + 2)
EcoRI-HF | 1 μL x (no_upstream + 2) | 0 | 1 μL x (no_plasmid + 2)
SpeI | 1 μL x (no_upstream + 2) | 0 | 0
XbaI | 0 | 1 μL x (no_downstream + 2) | 0
PstI | 0 | 1 μL x (no_downstream + 2) | 1 μL x (no_plasmid + 2)

More information can be seen in Metainformation: Reagents and Metainformation: Master mix.

#### 4. Create digests dataframe and update parts dataframe with digest wells
The function `get_digests(constructs, parts, reagents)` is used to define a digests dataframe (`digest_loc`), and assign digest wells. The parts dataframe `parts` is updated by adding digest wells. Digests are found by iterating through the parts dataframe and creating a new digest of the type specified in the `'roles'` column. Digests are also mapped to the constructs they will be used in. 

#### 5. Create assembly dictionaries
Extracts dictionaries on transfers from the dataframes with `create_assembly_dicts(constructs, parts, digest_loc, reagents)`. The dictionaries are `source_to_digest, reagent_to_digest, digest_to_construct, reagent_to_construct, reagents_dict`. `source_to_digest` has part wells as its keys and a list of tuples as its values - each tuple contains a digest well that the part is being transferred to, and the volume that is being transferred. The other dictionaries have similar formats, with `reagent_to_digest` mapping reagent wells to digest wells, etc., with the exception of `reagents_dict`, which has reagent names as its keys and reagent wells as its values. 

#### 6. Write to an assembly protocol
The five assembly dictionaries and the non-path input parameters are written to an assembly template file, which is saved in the output folder as `bb_assembly_protocol.py`. This is done by the function `create_assembly_protocol()`, which returns the path of the assembly protocol. 

#### 7. Create transformation dictionaries
`create_tranformation_dicts(constructs, water_well='A1', controls_per_cons=False)` produces `competent_source_to_dest, control_source_to_dest, assembly_source_to_dest, water_source_to_dest, transform_df`.
`competent_source_to_dest` dictates the transfers of competent cells to destination wells where transformation reactions take place, while `control_source_to_dest` does this for control cells. `assembly_source_to_dest` dictates the transfers from the construct plate to the transformation plate. Assemblies are transferred into the wells with competent cells. `water_source_to_dest` defines the transfers from the water well (specified as 'A1') to the control cells in the transformation plate.

`transform_df` contains the information about each filled well in the transformation plate and has the columns `'name', 'number', 'cell_type', 'construct', 'construct_well', 'cell_well', 'dest_well', 'reagent_well'`.

#### 8. Write to a transformation protocol
The four transformation dictionaries and the non-path input parameters are written to an transformation template file, which is saved in the output folder as `bb_transformation_protocol.py`. This is done by the function `create_transformation_protocol()`, which returns the path of the transformation protocol. 

#### 9. Save metainformation in a CSV
This saves all of the labware information and dataframes into a CSV. 

## Metainformation
### Constructs
#### Example
construct | well | upstream | downstream | plasmid
------------ | ------------- | -------------| -------------| -------------
pro_rbs_1_Var_BBa_J23119	| A1 |	BBa_J23119 |	BBa_B0030	| ColE1_AmpR
cds_ter_2_Var_BBa_I746916 |	A2 |	BBa_I746916 |	BBa_B0015	| ColE1_AmpR
pro_rbs_1_Var_BBa_J23108 | A3 | BBa_J23108 |BBa_B0030 | ColE1_AmpR
cds_ter_1_Var_BBa_I746916 | A4 | BBa_I746916 | BBa_B0015 | ColE1_AmpR
cds_ter_2_Var_BBa_E1010	| A5 | BBa_E1010 | BBa_B0015 | ColE1_AmpR
pro_rbs_2_Var_BBa_J23119 | A6 | BBa_J23119 | BBa_B0030 | ColE1_AmpR
pro_rbs_2_Var_BBa_J23108 | A7 | BBa_J23108 | BBa_B0030 | ColE1_AmpR
cds_ter_1_Var_BBa_E1010	| A8 |BBa_E1010 | BBa_B0015 | ColE1_AmpR
#### Explanation
This is pretty self-explanatory: the construct column gives the name of the construct, the well column gives the well that the construct is in, upstream gives the name of the part used in the upstream position, etc.

### Parts
#### Example
name | well | occurences | roles | digests | concentration | part_vol | water_vol | part_vol_tot | water_vol_tot | constructs_in | plate | digest_wells
------------ | ------------- | -------------| -------------| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | -------------
BBa_B0015 | A1 | [0, 4, 0] | ['downstream'] | 1 | 100 | 5 | 38 | 5 | 38 | [[], [1, 3, 4, 7], []] | 2 | ['A1']
BBa_B0030 | A2 | [0, 4, 0] | ['downstream'] | 1 | 100 | 5 | 38 | 5 | 38 | [[], [0, 2, 5, 6], []] | 2 | ['A2']
BBa_E1010 | A3 | [2, 0, 0] | ['upstream'] | 1 | 100 | 5 | 38 | 5 | 38 | [[4, 7], [], []] | 2 | ['A3']
BBa_I746916 | A4 | [2, 0, 0] | ['upstream'] | 1 | 100 | 5 | 38 | 5 | 38 | [[1, 3], [], []] | 2 | ['A4']
BBa_J23108 | A5 | [2, 0, 0] | ['upstream'] | 1 | 100 | 5 | 38 | 5 | 38 | [[2, 6], [], []] | 2 | ['A5']
BBa_J23119 | A6 | [2, 0, 0] | ['upstream'] | 1 | 100 | 5 | 38 | 5 | 38 | [[0, 5], [], []] | 2 | ['A6']
ColE1_AmpR | A7 | [0, 0, 8] | ['plasmid'] | 1 | 100 | 5 | 38 | 5 | 38 | [[], [], [0, 1, 2, 3, 4, 5, 6, 7]] | 2 | ['A7']
#### Explanation
* name = name of the part
* well = well of the part in the source plate (defined by the column plate)
* occurences = list of counts of the number of times a part appears in the upstream, downstream, and plasmid positions of a construct. For example [1, 0, 0] means a part is used once in the upstream position, and not anywhere else.
* roles = list of the positions the part has in constructs, e.g. if the part has been used in the upstream and downstream positions, roles will equal `['upstream', 'downstream']`.
* digests = number of digests that the part goes in to, e.g. 2 if the part is used both in the upstream and downstream position 
* concentration = concentration of the part in ng/μL
* part_vol = volume of part used by digest in μL
* water_vol = volume of water used by digest in μL
* part_vol_tot = total volume of the part used for all of the digests in μL
* water_vol_tot =  total volume of water used for all of the digests with the part μL
* constructs_in = list of lists
  * 0th list = the indices of constructs the part is upstream in
  * 1st list = the indices of constructs the part is downstream in
  * 2nd list = the indices of constructs the part is a plasmid in
* plate = deck position in the assembly protocol, in this case '2'
* digest_wells = list of wells for the digests the part is in

### Digests
#### Example
name | role | part | source_well | dest_well | construct_wells
------------ | ------------- | -------------| -------------| ------------- | -------------
BBa_B0015-downstream | downstream | BBa_B0015 | A1 | A1	| ['A2', 'A4', 'A5', 'A8']
BBa_B0030-downstream | downstream | BBa_B0030 | A2 | A2	| ['A1', 'A3', 'A6', 'A7']
BBa_E1010-upstream | upstream | BBa_E1010 | A3 | 	A3 | ['A5', 'A8']
BBa_I746916-upstream | upstream | BBa_I746916 | A4 | A4	| ['A2', 'A4']
BBa_J23108-upstream | upstream | BBa_J23108 | A5 | A5 | ['A3', 'A7']
BBa_J23119-upstream | upstream | BBa_J23119 | A6 | A6 | ['A1', 'A6']
ColE1_AmpR-plasmid | plasmid | ColE1_AmpR | A7 | A7 | ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8']
#### Explanation
* name = name of digest = part + '-' + role
* role = upstream, downstream, or plasmid
* part = the name of the part the digest is for
* source_well = the well of the part in the source plate
* dest_well = the digest well in the digest plate
* construct_wells = the list of wells for constructs that the digest is used in
### Reagents
#### Example
name | well | total_vol
------------ | ------------- | -------------
water | A1 | 364
mm_upstream | A2 | 42
mm_downstream | A3 | 28
mm_plasmid | A4 | 21
T4Ligase10X | A5 | 26
T4Ligase | A6 | 18
#### Explanation
* name = the name of the reagent, mm stands for master mix
* well = the well of the reagent in the reagents tube rack
* total_vol = the total volume of reagent needed, including dead volume, in μL
### Master mix
#### Example
reagent | volume in upstream mm | volume in downstream mm | volume in plasmid mm
| ------------- | ------------- | ------------- | -------------
NEB Buffer 10X | 30 | 20 | 15
EcoRI-HF | 6 | 0 | 3
SpeI | 6 | 0 | 0
XbaI | 0 | 4 | 0
PstI | 0 | 4 | 3
#### Explanation
This should be made by the user and placed in the reagent wells defined in the reagents table above.
* reagent = the name of the reagent used in making the master mix (not a reagent in the reagent plate)
* volume in upstream mm = how much of the reagent in μL should be put in the upstream master mix well
* volume in downstream mm = how much of the reagent in μL should be put in the downstream master mix well
* volume in plasmid mm = how much of the reagent in μL should be put in the plasmid master mix well
### Transforms
#### Example
name | number | cell_type | construct | construct_well | cell_well | dest_well | reagent_well
------------ | ------------- | -------------| -------------| -------------| -------------| -------------| -------------
pro_rbs_1_Var_BBa_J23119-0 | 0 | competent | pro_rbs_1_Var_BBa_J23119 | A1 | A9 | A1 | 
pro_rbs_1_Var_BBa_J23119-1 | 1 | competent | pro_rbs_1_Var_BBa_J23119 | A1 | A9 | A2 | 
pro_rbs_1_Var_BBa_J23119-2 | 2 | competent | pro_rbs_1_Var_BBa_J23119 | A1 | A9 | A3 | 
pro_rbs_1_Var_BBa_J23119-3 | 3 | competent | pro_rbs_1_Var_BBa_J23119 | A1 | A10 | A4 | 
cds_ter_2_Var_BBa_I746916-0 | 0 | competent | cds_ter_2_Var_BBa_I746916 | A2 | A10 | A5 | 
cds_ter_2_Var_BBa_I746916-1 | 1 | competent | cds_ter_2_Var_BBa_I746916 | A2 | A10 | A6 | 
cds_ter_2_Var_BBa_I746916-2 | 2 | competent | cds_ter_2_Var_BBa_I746916 | A2 | A11 | A7 | 
cds_ter_2_Var_BBa_I746916-3 | 3 | competent | cds_ter_2_Var_BBa_I746916 | A2 | A11 | A8 | 
pro_rbs_1_Var_BBa_J23108-0 | 0 | competent | pro_rbs_1_Var_BBa_J23108 | A3 | A11 | A9 | 
pro_rbs_1_Var_BBa_J23108-1 | 1 | competent | pro_rbs_1_Var_BBa_J23108 | A3 | A12 | A10 | 
pro_rbs_1_Var_BBa_J23108-2 | 2 | competent | pro_rbs_1_Var_BBa_J23108 | A3 | A12 | A11 | 
pro_rbs_1_Var_BBa_J23108-3 | 3 | competent | pro_rbs_1_Var_BBa_J23108 | A3 | A12 | A12 | 
cds_ter_1_Var_BBa_I746916-0 | 0 | competent | cds_ter_1_Var_BBa_I746916 | A4 | B1 | B1 | 
cds_ter_1_Var_BBa_I746916-1 | 1 | competent | cds_ter_1_Var_BBa_I746916 | A4 | B1 | B2 | 
cds_ter_1_Var_BBa_I746916-2 | 2 | competent | cds_ter_1_Var_BBa_I746916 | A4 | B1 | B3 | 
cds_ter_1_Var_BBa_I746916-3 | 3 | competent | cds_ter_1_Var_BBa_I746916 | A4 | B2 | B4 | 
cds_ter_2_Var_BBa_E1010-0 | 0 | competent | cds_ter_2_Var_BBa_E1010 | A5 | B2 | B5 | 
cds_ter_2_Var_BBa_E1010-1 | 1 | competent | cds_ter_2_Var_BBa_E1010 | A5 | B2 | B6 | 
cds_ter_2_Var_BBa_E1010-2 | 2 | competent | cds_ter_2_Var_BBa_E1010 | A5 | B3 | B7 | 
cds_ter_2_Var_BBa_E1010-3 | 3 | competent | cds_ter_2_Var_BBa_E1010 | A5 | B3 | B8 | 
pro_rbs_2_Var_BBa_J23119-0 | 0 | competent | pro_rbs_2_Var_BBa_J23119 | A6 | B3 | B9 | 
pro_rbs_2_Var_BBa_J23119-1 | 1 | competent | pro_rbs_2_Var_BBa_J23119 | A6 | B4 | B10 | 
pro_rbs_2_Var_BBa_J23119-2 | 2 | competent | pro_rbs_2_Var_BBa_J23119 | A6 | B4 | B11 | 
pro_rbs_2_Var_BBa_J23119-3 | 3 | competent | pro_rbs_2_Var_BBa_J23119 | A6 | B4 | B12 | 
pro_rbs_2_Var_BBa_J23108-0 | 0 | competent | pro_rbs_2_Var_BBa_J23108 | A7 | B5 | C1 | 
pro_rbs_2_Var_BBa_J23108-1 | 1 | competent | pro_rbs_2_Var_BBa_J23108 | A7 | B5 | C2 | 
pro_rbs_2_Var_BBa_J23108-2 | 2 | competent | pro_rbs_2_Var_BBa_J23108 | A7 | B5 | C3 | 
pro_rbs_2_Var_BBa_J23108-3 | 3 | competent | pro_rbs_2_Var_BBa_J23108 | A7 | B6 | C4 | 
cds_ter_1_Var_BBa_E1010-0 | 0 | competent | cds_ter_1_Var_BBa_E1010 | A8 | B6 | C5 | 
cds_ter_1_Var_BBa_E1010-1 | 1 | competent | cds_ter_1_Var_BBa_E1010 | A8 | B6 | C6 | 
cds_ter_1_Var_BBa_E1010-2 | 2 | competent | cds_ter_1_Var_BBa_E1010 | A8 | B7 | C7 | 
cds_ter_1_Var_BBa_E1010-3 | 3 | competent | cds_ter_1_Var_BBa_E1010 | A8 | B7 | C8 | 
control-0 | 0 | control |  |  | B8 | C9 | A1
control-1 | 1 | control |  |  | B8 | C10 | A1
control-2 | 2 | control |  |  | B8 | C11 | A1

#### Explanation
* name = the construct name + '-' + number or if a control well control + '-' + number
* number = for assemblies goes from 0 to 3, giving each assembly four different wells to be transformed in; for controls goes from 0 to 2, giving 3 controls
* cell_type = competent (assemblies are being transformed) or control
* construct = the name of the construct being tranformed; left blank if control
* construct_well = the well that the construct is in in the construct plate; left blank if control
* cell_well = the well the competent or control cells are transferred from 
* dest_well = the well in the transformation plate that the transformations occur in
* reagent_well = the well where water is taken from in the case of the control; left blank if competent
