---
sidebar_label: biobricks_assembly.biobricks10.bbinput
title: biobricks_assembly.biobricks10.bbinput
---

#### biobricks

```python
biobricks(output_folder: str, construct_path: List[str], part_path: List[str], thermocycle: bool = True, p10_mount: str = 'right', p300_mount: str = 'left', p10_type: str = 'p10_single', p300_type: str = 'p300_single', well_plate: str = 'biorad_96_wellplate_200ul_pcr', tube_rack: str = 'opentrons_24_tuberack_nest_1.5ml_snapcap', soc_plate: str = 'usascientific_96_wellplate_2.4ml_deep', transformation_plate: str = 'corning_96_wellplate_360ul_flat') -> List[str]
```

Main function, creates scripts and metainformation
Can take specific args or just **labware_dict for all labware

**Arguments**:

- `output_folder` - the full file path of the intended output folder
  for files generated
- `construct_path` - a one element list with the full path of the
  construct csv
- `part_path` - a list of full paths to part csv(s) (one or more)
- `thermocyle` - True or False, indicating whether the user has
  and would like to use the Opentrons Thermocycler
  see labware_dict for rest of arguments

**Returns**:

  List of output paths
  If there is an exception, the list of output paths will contain
  only one element = the error path
  Otherwise the list of output paths will contain:
  OT-2 script paths (assembly, transformation),
  metainformation

#### get\_constructs

```python
get_constructs(path: str) -> Tuple[pd.DataFrame, List[str]]
```

Returns construct dataframe from constructs csv
Args: path = path of construct csv

**Returns**:

- `merged_constructs_list` - dataframe of constructs
- `dest_well_list` - list of wells in construct plate that are used

#### process\_construct

```python
process_construct(construct_entry: List) -> Dict[str, List[str]]
```

Returns construct dictionary from row in csv file
Used in get_constructs()
Args: construct_entry = construct row from csv in list
Returns: Dictionary of construct info

#### get\_parts

```python
get_parts(paths: List[str], constructs_list: pd.DataFrame) -> pd.DataFrame
```

Returns a dataframe of parts from part csv file.
Uses constructs_list to record the number of times the part is used
in the constructs and the roles it plays.

**Arguments**:

- `paths` - list of paths to part csvs
- `constructs_list` - dataframe of constructs

**Returns**:

- `merged_parts_list` - dataframe of parts

#### process\_part

```python
process_part(part: List, constructs_list: pd.DataFrame, plate: str) -> Dict[str, List]
```

Returns a part dataframe with detailed information.
Used in get_parts()

**Arguments**:

- `part` - row of part csv file
- `constructs_list` - constructs dataframe
- `plate` - source plate of part

**Returns**:

  Dataframe of individual part

#### get\_reagents\_wells

```python
get_reagents_wells(constructs_list: pd.DataFrame, parts: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], pd.DataFrame]
```

**Arguments**:

- `constructs_list` - dataframe of constructs
- `parts` - dataframe of parts

**Returns**:

  Dataframe with rows as reagent names and cols
  as the reagent well and the volume of the reagent required.
  List of wells used for reagents in reagents tube rack
  Master mix dataframe giving volumes of each reagent

#### get\_digests

```python
get_digests(constructs_list: pd.DataFrame, parts: pd.DataFrame, reagents: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]
```

Creates a dataframe of digests, the intermediate step in assembly
BioBricks constructs.

**Arguments**:

- `constructs_list` - dataframe of constructs
- `parts` - dataframe of parts
- `reagents` - dataframe of reagents

**Returns**:

  dataframe of digests
  updated parts dataframe with digest well column

#### next\_well

```python
next_well(wells_used: List[str]) -> str
```

Finds the next available well from a list of used wells
for a 96 well plate

**Arguments**:

  List of wells used in 96 well plate

**Returns**:

  Next unused well in 96 well plate

#### next\_well\_reagent

```python
next_well_reagent(wells_used: List[str]) -> str
```

Finds the next available well from a list of used wells
for a 24 well plate/tube rack

**Arguments**:

  List of wells used in 24 well plate/tube rack

**Returns**:

  Next unused well in 24 well plate/tube rack

#### count\_part\_occurences

```python
count_part_occurences(constructs_list: pd.DataFrame, part: List) -> Tuple[List[int], List[List[int]]]
```

Counts the number of times a part is used in the constructs.
Differentiates between upstream uses, downstream uses,
and plasmid uses: all require different digests.

**Arguments**:

- `constructs_list` - dataframe of constructs
- `part` - row in part csv file as list

**Returns**:

- `counts` - list where 0th element = upstream counts,
  1st element = downstream counts, 2nd element =
  plasmid counts
- `constructs_in_upstream` - index of constructs a part appears
  in as the upstream part
- `constructs_in_downstream` - index of constructs a part appears
  in as the downstream part
- `constructs_in_plasmid` - index of constructs a part appears
  in as the plasmid part

#### create\_assembly\_dicts

```python
create_assembly_dicts(constructs: pd.DataFrame, parts: pd.DataFrame, digests: pd.DataFrame, reagents: pd.DataFrame) -> Tuple[Dict, Dict, Dict, Dict, Dict]
```

Returns assembly dictionaries to be used in the assembly protocol,
instructing which transfers need to be made.

**Arguments**:

- `constructs` - dataframe of constructs
- `parts` - dataframe of parts
- `digests` - dataframe of digests
- `reagents` - dataframe of reagents

**Returns**:

- `source_to_digest` - dictionary with key = source (part) well,
  key = list of tuples in format (digest well, volume to transfer)
- `reagent_to_digest` - dictionary with key = reagent well,
  key = list of tuples in format (digest well, volume to transfer)
- `digest_to_construct` - dictionary with key = digest well,
  key = list of tuples in format (construct well, volume to transfer)
- `reagent_to_construct` - dictionary with key = reagent well,
  key = list of tuples in format (construct well, volume to transfer)
- `reagents_dict` - dictionary with key = reagent name,
  key = reagent well

#### create\_tranformation\_dicts

```python
create_tranformation_dicts(constructs: pd.DataFrame, water_well: str = 'A1', controls_per_cons: bool = False) -> Tuple[Dict[str, List[Tuple[str, int]]], Dict[str, List[Tuple[str, int]]],
           Dict[str, List[Tuple[str, int]]], Dict[str, List[Tuple[str, int]]],
           pd.DataFrame]
```

Creates transformation dictionaries to be used in the
transformation protocol, instructing which transfers need to be made.
Creates transform_df for metainformation
Competent wells + construct wells -&gt; same well for transformation.
Control wells + water well -&gt; same well for transformation.

**Arguments**:

- `Constructs` - dataframe of constructs
- `water_well` - well that water is stored in
- `controls_per_cons` - create three controls per construct if True
  create three controls total if False

**Returns**:

- `competent_source_to_dest` - dictionary with key = competent cell
  well, value = tuple of destination well + transfer vol
- `control_source_to_dest` - dictionary with key = control cell
  well, value = tuple of destination well + transfer vol
- `assembly_source_to_dest` - dictionary with key = construct
  well, value = tuple of destination well + transfer vol,
- `water_source_to_dest` - dictionary with key = water
  well, value = tuple of destination well + transfer vol
- `transform_df` - dataframe of transformation reactions

#### create\_assembly\_protocol

```python
create_assembly_protocol(template_path: str, output_path: str, source_to_digest: Dict[str, List[Tuple[str, int]]], reagent_to_digest: Dict[str, List[Tuple[str, int]]], digest_to_construct: Dict[str, List[Tuple[str, int]]], reagent_to_construct: Dict[str, List[Tuple[str, int]]], reagents_dict: Dict[str, str], p10_mount: str, p10_type: str, well_plate_type: str, tube_rack_type: str, thermocycle: bool) -> str
```

Generates the assembly protocol used by opentrons.
Returns the path of the assembly script.

**Arguments**:

- `template_path` - absolute path of the Opentrons script template
- `output_path` - absolute path of the output folder to save protocol in
- `source_to_digest` - dictionary of form
  Dict[str, List[Tuple(str, int)]], dictionary key (string) gives
  source (part) well to transfer from, the 0th element of each tuple
  gives well to transfer to (digest well in this case), with the 1st
  element of the tuple giving the volume to transfer.
- `reagent_to_digest` - dictionary of same form as source_to_digest
  (Dict[str, List[Tuple(str, int)]]), instructing transfers from
  reagent wells to digest wells
- `digest_to_storage` - dictionary of same form as source_to_digest
  (Dict[str, List[Tuple(str, int)]]), instructing transfers from
  digest wells to storage wells (wells where digest not used in
  construct is stored after assembly)
- `digest_to_construct` - dictionary of same form as source_to_digest
  (Dict[str, List[Tuple(str, int)]]), instructing transfers from
  digest wells to construct wells
- `reagent_to_construct` - dictionary of same form as source_to_digest
  (Dict[str, List[Tuple(str, int)]]), instructing transfers from
  reagent wells to construct wells
- `p10_mount` - &quot;left&quot; or &quot;right&quot;, the Opentrons pipette mount options
- `p10_type` - the name of the p10 pipette, e.g. &quot;p10_single&quot;
- `well_plate_type` - the name of the well plate type used as the source
  plate and construct plate
- `tube_rack_type` - the name of the tube rack type used for holding the
  reagents
- `thermocycle` - True or False, True = run thermocycle module in
  scripts, False = use benchtop thermocycler

**Returns**:

  path of assembly protocol script

#### create\_transformation\_protocol

```python
create_transformation_protocol(template_path: str, output_path: str, competent_source_to_dest: Dict[str, List], control_source_to_dest: Dict[str, List], assembly_source_to_dest: Dict[str, List], water_source_to_dest: Dict[str, List], p10_mount: str, p300_mount: str, p10_type: str, p300_type: str, well_plate_type: str, transformation_plate_type: str, tube_rack_type: str, soc_plate_type: str) -> str
```

Generates the transformation protocol used by opentrons.

**Arguments**:

- `template_path` - absolute path of the Opentrons script template
- `output_path` - absolute path of the output folder to save protocol in
- `competent_source_to_digest` - dictionary of form
  Dict[str, List[Tuple(str, int)]], dictionary key (string) gives
  competent cell well to transfer from, the 0th element of each tuple
  gives well to transfer to (transformation well), with the 1st
  element of the tuple giving the volume to transfer.
- `control_source_to_digest` - dictionary of same form as
  competent_source_to_digest (Dict[str, List[Tuple(str, int)]]),
  instructing transfers from control wells to transformation wells
- `assembly_source_to_digest` - dictionary of same form as
  competent_source_to_digest (Dict[str, List[Tuple(str, int)]]),
  instructing transfers from construct wells to transformation wells
- `water_source_to_digest` - dictionary of same form as
  competent_source_to_digest (Dict[str, List[Tuple(str, int)]]),
  instructing transfers from water well to transformation wells
- `p10_mount` - &quot;left&quot; or &quot;right&quot;, the Opentrons pipette mount options
- `p300_mount` - &quot;left&quot; or &quot;right&quot;, the Opentrons pipette mount options
- `p10_type` - the name of the p10 pipette, e.g. &quot;p10_single&quot;
- `p300_type` - the name of the p300 pipette, e.g. &quot;p300_single&quot;
- `well_plate_type` - the name of the well plate type used as the
  construct plate
- `transformation_plate_type` - the name of the well plate type used as the
  transformation plate
- `tube_rack_type` - the name of the tube rack type used to store cells
- `soc_plate_type` - the name of the plate type used to store soc

**Returns**:

  path of transform protocol script

#### dfs\_to\_csv

```python
dfs_to_csv(path, index=True, **kw_dfs)
```

Generates a csv file defined by path, where kw_dfs are
written one after another with each key acting as a title. If index=True,
df indexes are written to the csv file.

