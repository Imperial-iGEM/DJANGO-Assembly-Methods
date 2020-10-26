---
sidebar_label: moclo_assembly.moclo_transformation.moclo_transform_generator
title: moclo_assembly.moclo_transformation.moclo_transform_generator
---

#### moclo\_function

```python
moclo_function(output_folder: str, construct_path: List[str], part_path: List[str], thermocycle: bool = True, p10_mount: str = 'right', p300_mount: str = 'left', p10_type: str = 'p10_single', p300_type: str = 'p300_multi', well_plate: str = 'biorad_96_wellplate_200ul_pcr', trough: str = 'usascientific_12_reservoir_22ml', reagent_plate: str = 'biorad_96_wellplate_200ul_pcr', agar_plate: str = 'thermofisher_96_wellplate_180ul') -> List[str]
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
  metainformation (assembly, transformation, agar plate)

#### generate\_plate\_maps

```python
generate_plate_maps(filename: str) -> Dict[str, List[List]]
```

Generates dictionaries for the part csvs
Args: filename = absolute path to part csv
Returns: dictionary of plate maps with key = name of part csv,
value = list of rows (= list of lists)

#### generate\_combinations

```python
generate_combinations(combinations_filename: str) -> List[Dict]
```

Generates a list of dictionaries of constructs to be made
Args: combinations_filename = absolute path to construct csv file
Returns: List of construct dictionaries with keys &quot;name&quot; and &quot;parts&quot;

#### check\_number\_of\_combinations

```python
check_number_of_combinations(combinations_limit: str, combinations_to_make: List[Dict])
```

Ensures that the number of constructs does not exceed the maximum

**Arguments**:

- `combinations_limit` - &quot;single&quot; or &quot;triplicate&quot; - if &quot;single&quot; can do
  max 88 constructs, if &quot;triplicate&quot; does every construct 3 times -
  max 24 constructs
- `Raises` - ValueError if there are too many constructs or
  combinations_limit is not &quot;single&quot; or &quot;triplicate&quot;

#### generate\_and\_save\_output\_plate\_maps

```python
generate_and_save_output_plate_maps(combinations_to_make: List[Dict], combinations_limit: str, output_folder_path: str) -> Tuple[str, str]
```

Saves the mapping of the agar plate for use in transformation.

**Arguments**:

  combinations_to_make = list of construct dictionaries
  combinations_limit = &quot;single&quot; or &quot;triplicate&quot;
  output_folder_path = where to save mapping

**Returns**:

- `triplicate` - whether &#x27;single&#x27; (triplicate = False) or &#x27;triplicate&#x27;
  (triplicate = True) is selected
- `output_filename` - the absolute path to the agar plate csv

#### create\_metainformation

```python
create_metainformation(output_path: str, dna_plate_map_dict: Dict[str, List[List]], combinations_to_make: List[Dict], labware_dict: Dict[str, str], thermocycle: bool, triplicate: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]
```

Returns detailed metainformation and saves in a csv.
Includes a parts dataframe, a combinations (constructs)
dataframe, a reagents dataframe, and a master mix dataframe.

**Arguments**:

- `output_path` - the full path of the output folder
- `dna_plate_map_dict` - the dictionary of parts
- `combinations_to_make` - the list of dictionaries of
  constructs
- `labware_dict` - the dictionary of labware chosen
- `thermocyle` - whether the thermocycler module is used
- `triplicate` - whether &#x27;single&#x27; (triplicate = False) or &#x27;triplicate&#x27;
  (triplicate = True) is selected

**Returns**:

- `parts_df` - dataframe of parts
- `combinations_df` - dataframe of constructs
- `mm_df` - master mix dataframe, contains information on all of the
  master mixes needed (different master mix needed for different
  number of parts per construct)
- `reagents_df` - reagents dataframe, contains information on all of the
  reagents, does not include master mix but DOES include reagents to
  go into master mixes

#### create\_parts\_df

```python
create_parts_df(dna_plate_map_dict: Dict[str, List[List]]) -> pd.DataFrame
```

Returns a dataframe of parts and delegates wells.
Takes in the dictionary of parts.

**Arguments**:

- `dna_plate_map_dict` - dictionary with keys = plate names, values =
  list of rows = list of list of parts

**Returns**:

- `parts_df` - dataframe of parts with dummy &#x27;0&#x27; for combinations col

#### create\_mm\_df

```python
create_mm_df(combinations_df: pd.DataFrame) -> pd.DataFrame
```

Creates a master mix dataframe and delegates wells.
Different master mixes must be created depending on
the number of parts per construct.
Args: combinations_df = dataframe of constructs
Returns: dataframe of master mixes with wells and volumes
of different reagents required

#### create\_reagents\_df

```python
create_reagents_df(mm_df: pd.DataFrame) -> pd.DataFrame
```

Creates a dataframe of reagents used to make master mixes.
More than one buffer well may be required, and water is
held on a separate plate.
Also indicates which master mix wells the reagent is
transferred to.
Args: master mix dataframe
Returns: dataframe of reagents used in master mix + water

#### get\_mm\_dicts

```python
get_mm_dicts(mm_df: pd.DataFrame, reagents_df: pd.DataFrame) -> Tuple[Dict[str, List[Tuple[str, str, str]]], Dict]
```

Master mix dictionary purely for use in the assembly script.
Provides instructions on tranfers.

**Arguments**:

  mm_df = dataframe of master mix, gives wells and diff vol needed
  reagents_df = dataframe of reagents to be used in master mix and
  other parts of assembly

**Returns**:

- `reagent_to_mm_dict` - dictionary directing where to transfer each
  reagent to to make master mixes, key = reagent well, value =
  list of tuples of reagent plate (different for water and other
  reagents), master mix well, and volume to be transferred
  mm_dict_list = mm_df rows stored as dictionaries in list

#### index\_to\_well\_name

```python
index_to_well_name(no: int) -> str
```

Converts well from number format to letter format
Args: well in number format e.g. 0
Returns: well in letter format e.g. &#x27;A1&#x27;

#### create\_transform\_metainformation

```python
create_transform_metainformation(output_path: str, labware_dict: Dict[str, str], triplicate: str, multi: bool)
```

Saves transform metainformation and labware informaiton.
SOC used in two steps: adding soc (150 uL) and dilution (45 uL)
times by 96 as reaction plate has 96 wells
Add 300 (150*2) and 90 (45*2) as dead vols
Agar plate positions in agar plate csv

**Arguments**:

- `output_path` - absolute path to transformation metainformation file
- `labware_dict` - dictionary of labware to be used
- `triplicate` - whether &#x27;single&#x27; (triplicate = False) or &#x27;triplicate&#x27;
  (triplicate = True) is selected
- `multi` - whether an 8 channel (multi = True) or single channel
  (mutli = False) p300 pipette is being used

#### create\_protocol

```python
create_protocol(dna_plate_map_dict: Dict[str, List], combinations_to_make: List[Dict], reagent_to_mm_dict: Dict, mm_dict: Dict, assembly_template_path: str, transform_template_path: str, output_folder_path: str, thermocycle: bool, triplicate: str, multi: bool, p10Mount: str, p300Mount: str, p10_type: str, p300_type: str, reaction_plate_type: str, reagent_plate_type: str, trough_type: str, agar_plate_type: str) -> Tuple[str, str]
```

Generates the assembly and transformation protocols used by opentrons.
Returns the paths of the assembly and transform scripts.

**Arguments**:

- `dna_plate_map_dict` - the dictionary of parts
- `combinations_to_make` - the list of dictionaries of
  constructs
- `reagent_to_mm_dict` - dictionary directing where to transfer each
  reagent to to make master mixes, key = reagent well, value =
  list of tuples of reagent plate (different for water and other
  reagents), master mix well, and volume to be transferred
  mm_dict_list = mm_df rows stored as dictionaries in list
- `assembly_template_path` - the absolute path of the assembly template
  script
- `transform_template_path` - the absolute path of the transformation
  template script
- `output_folder_path` - the absolute path to the output folder that
  will contain the assembly and transformation protocols
- `thermocycle` - whether or not the Opentrons thermocycler module
  is being used
- `triplicate` - whether &#x27;single&#x27; (triplicate = False) or &#x27;triplicate&#x27;
  (triplicate = True) is selected
- `multi` - whether an 8 channel (multi = True) or single channel
  (mutli = False) p300 pipette is being used
- `p10_mount` - &quot;left&quot; or &quot;right&quot;, the Opentrons pipette mount options
- `p300_mount` - &quot;left&quot; or &quot;right&quot;, the Opentrons pipette mount options
- `p10_type` - the name of the p10 pipette, e.g. &quot;p10_single&quot;
- `p300_type` - the name of the p300 pipette, e.g. &quot;p300_single&quot;
- `reaction_plate_type` - the name of the well plate type used as the
  source and construct plate
- `reagent_plate_type` - the name of the well plate type used as the
  reagent plate (for master mix and non-water reagents)
- `trough_type` - the name of the trough type used for water and soc
- `agar_plate_type` - the name of the agar plate type used

