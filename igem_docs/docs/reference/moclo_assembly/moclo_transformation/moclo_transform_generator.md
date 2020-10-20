---
sidebar_label: moclo_assembly.moclo_transformation.moclo_transform_generator
title: moclo_assembly.moclo_transformation.moclo_transform_generator
---

#### moclo\_function

```python
moclo_function(output_folder, construct_path, part_path, thermocycle=True, p10_mount='right', p300_mount='left', p10_type='p10_single', p300_type='p300_multi', well_plate='biorad_96_wellplate_200ul_pcr', trough='usascientific_12_reservoir_22ml', reagent_plate='biorad_96_wellplate_200ul_pcr', agar_plate='thermofisher_96_wellplate_180ul')
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

#### generate\_plate\_maps

```python
generate_plate_maps(filename)
```

Generates dictionaries for the part csvs

#### generate\_combinations

```python
generate_combinations(combinations_filename)
```

Generates a list of dictionaries of constructs to be made

#### check\_number\_of\_combinations

```python
check_number_of_combinations(combinations_limit, combinations_to_make)
```

Ensures that the number of constructs does not exceed the maximum

#### generate\_and\_save\_output\_plate\_maps

```python
generate_and_save_output_plate_maps(combinations_to_make, combinations_limit, output_folder_path)
```

Saves the mapping of the agar plate for use in transformation.

**Arguments**:

  combinations_to_make = list of construct dictionaries
  combinations_limit = &#x27;single&#x27; or &#x27;triplicate&#x27;
  output_folder_path = where to save mapping

#### create\_metainformation

```python
create_metainformation(output_path, dna_plate_map_dict, combinations_to_make, labware_dict, thermocycle, triplicate)
```

Returns detailed metainformation and saves in a csv.
Includes a parts dataframe, a combinations (constructs)
dataframe, a reagents dataframe, and a master mix dataframe.

**Arguments**:

  output_path = the full path of the output folder
  dna_plate_map_dict = the dictionary of parts
  combinations_to_make = the list of dictionaries of
  constructs
  labware_dict = the dictionary of labware chosen
  thermocyle = whether the thermocycler module is used
  triplicate = whether &#x27;single&#x27; or &#x27;triplicate is selected&#x27;

#### create\_parts\_df

```python
create_parts_df(dna_plate_map_dict)
```

Returns a dataframe of parts and delegates wells.
Takes in the dictionary of parts.

#### create\_mm\_df

```python
create_mm_df(combinations_df)
```

Creates a master mix dataframe and delegates wells.
Different master mixes must be created depending on
the number of parts per construct.

#### create\_reagents\_df

```python
create_reagents_df(mm_df)
```

Creates a dataframe of reagents used to make master mixes.
More than one buffer well may be required, and water is
held on a separate plate.
Also indicates which master mix wells the reagent is
transferred to.

#### get\_mm\_dicts

```python
get_mm_dicts(mm_df, reagents_df)
```

Master mix dictionary purely for use in the assembly script. 
Provides instructions on tranfers.

#### index\_to\_well\_name

```python
index_to_well_name(no)
```

Converts well from number format e.g. 1 to letter format e.g.
&#x27;A1&#x27;

#### create\_transform\_metainformation

```python
create_transform_metainformation(output_path, labware_dict, triplicate, multi)
```

Saves transform metainformation and labware informaiton.
SOC used in two steps: adding soc (150 uL) and dilution (45 uL)
times by 96 as reaction plate has 96 wells
Add 300 (150*2) and 90 (45*2) as dead vols
Agar plate positions in agar plate csv

#### create\_protocol

```python
create_protocol(dna_plate_map_dict, combinations_to_make, reagent_to_mm_dict, mm_dict, assembly_template_path, transform_template_path, output_folder_path, thermocycle, triplicate, multi, p10Mount, p300Mount, p10_type, p300_type, reaction_plate_type, reagent_plate_type, trough_type, agar_plate_type)
```

Generates the assembly and transformation protocols used by opentrons.
Returns the paths of the assembly and transform scripts.

