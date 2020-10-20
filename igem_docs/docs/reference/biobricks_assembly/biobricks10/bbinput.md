---
sidebar_label: biobricks_assembly.biobricks10.bbinput
title: biobricks_assembly.biobricks10.bbinput
---

#### biobricks

```python
biobricks(output_folder, construct_path, part_path, thermocycle=True, p10_mount='right', p300_mount='left', p10_type='p10_single', p300_type='p300_single', well_plate='biorad_96_wellplate_200ul_pcr', tube_rack='opentrons_24_tuberack_nest_1.5ml_snapcap', soc_plate='usascientific_96_wellplate_2.4ml_deep', transformation_plate='corning_96_wellplate_360ul_flat')
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

#### get\_constructs

```python
get_constructs(path)
```

Returns construct dataframe from constructs csv

#### process\_construct

```python
process_construct(construct_entry)
```

Returns construct dictionary from row in csv file
Used in get_constructs()

#### get\_parts

```python
get_parts(paths, constructs_list)
```

Returns a dataframe of parts from part csv file.
Uses constructs_list to record the number of times the part is used
in the constructs and the roles it plays.

#### process\_part

```python
process_part(part, constructs_list, plate)
```

Returns a part dictionary with detailed information.
Used in get_parts()

#### get\_reagents\_wells

```python
get_reagents_wells(constructs_list, parts)
```

Returns dataframe with rows as reagent names and cols
as the reagent well and the volume of the reagent required.

#### get\_digests

```python
get_digests(constructs_list, parts, reagents_wells_used, dest_wells_used, reagents)
```

Creates a dataframe of digests, the intermediate step in assembly
BioBricks constructs.

#### next\_well

```python
next_well(wells_used)
```

Finds the next available well from a list of used wells
for a 96 well plate

#### next\_well\_reagent

```python
next_well_reagent(wells_used)
```

Finds the next available well from a list of used wells
for a 24 well plate

#### count\_part\_occurences

```python
count_part_occurences(constructs_list, part)
```

Counts the number of times a part is used in the constructs.
Differentiates between upstream uses, downstream uses,
and plasmid uses: all require different digests.

#### create\_assembly\_dicts

```python
create_assembly_dicts(constructs, parts, digests, reagents)
```

Returns assembly dictionaries to be used in the assembly protocol,
instructing which transfers need to be made.

#### create\_tranformation\_dicts

```python
create_tranformation_dicts(constructs, water_well='A1', controls_per_cons=False)
```

Returns transformation dictionaries to be used in the transformation
protocol, instructing which transfers need to be made.

#### create\_assembly\_protocol

```python
create_assembly_protocol(template_path, output_path, source_to_digest, reagent_to_digest, digest_to_storage, digest_to_construct, reagent_to_construct, p10_mount, p10_type, well_plate_type, tube_rack_type, thermocycle)
```

Generates the assembly protocol used by opentrons.
Returns the path of the assembly script.

#### create\_transformation\_protocol

```python
create_transformation_protocol(template_path, output_path, competent_source_to_dest, control_source_to_dest, assembly_source_to_dest, water_source_to_dest, p10_mount, p300_mount, p10_type, p300_type, well_plate_type, transformation_plate_type, tube_rack_type, soc_plate_type)
```

Generates the transformation protocol used by opentrons.
Returns the path of the transform script.

#### dfs\_to\_csv

```python
dfs_to_csv(path, index=True, **kw_dfs)
```

Generates a csv file defined by path, where kw_dfs are
written one after another with each key acting as a title. If index=True,
df indexes are written to the csv file.

