---
sidebar_label: basic_assembly.dna_bot.dnabot_app
title: basic_assembly.dna_bot.dnabot_app
---

#### dnabot

```python
dnabot(output_folder, ethanol_well_for_stage_2, deep_well_plate_stage_4, input_construct_path, output_sources_paths, p10_mount='right', p300_mount='left', p10_type='p10_single', p300_type='p300_multi', well_plate='biorad_96_wellplate_200ul_pcr', reagent_plate='usascientific_12_reservoir_22ml', mag_plate='biorad_96_wellplate_200ul_pcr', tube_rack='opentrons_24_tuberack_nest_1.5ml_snapcap', aluminum_block='opentrons_96_aluminumblock_biorad_wellplate_200ul', bead_container='usascientific_96_wellplate_2.4ml_deep', soc_plate='usascientific_96_wellplate_2.4ml_deep', agar_plate='thermofisher_96_wellplate_180ul')
```

Main function, creates scripts and metainformation
Can take specific args or just **labware_dict for all labware

**Arguments**:

- `output_folder` - the full file path of the intended output folder
  for files generated
  ethanol_well_for_stage_2 = ethanol well in letter format e.g.
  &#x27;A1&#x27; to be used in purification
  deep_well_plate_stage_4 = soc well to be used in transformation
  please only enter wells from &#x27;A1&#x27; to &#x27;A12&#x27; as this is a trough
- `construct_path` - a one element list with the full path of the
  construct csv
- `part_path` - a list of full paths to part csv(s) (one or more)
  see labware_dict for rest of arguments

#### generate\_constructs\_list

```python
generate_constructs_list(path)
```

Generates a list of dataframes corresponding to each construct. Each
dataframe lists components of the CLIP reactions required.

#### generate\_clips\_df

```python
generate_clips_df(constructs_list)
```

Generates a dataframe containing information about all the unique CLIP
reactions required to synthesise the constructs in constructs_list.

#### generate\_sources\_dict

```python
generate_sources_dict(paths)
```

Imports csvs files containing a series of parts/linkers with
corresponding information into a dictionary where the key corresponds with
part/linker and the value contains a tuple of corresponding information.

**Arguments**:

- `paths` _list_ - list of strings each corresponding to a path for a
  sources csv file.

#### fill\_parts\_df

```python
fill_parts_df(clips_df, parts_df_temp)
```

Fill dataframe of parts with metainformation to be stored in csv.
Will add final assembly well in generate_final_assembly_dict()

**Arguments**:

- `clips_df` - the dataframe of clips created as intermediate steps
  before assembly
- `parts_df_temp` - the previous parts_df dataframe to be expanded on

**Returns**:

  parts_df, with new columns of &#x27;clip_well&#x27;, &#x27;mag_well&#x27;, &#x27;total_vol&#x27;,
  &#x27;vol_per_clip&#x27;, and &#x27;number&#x27;

#### generate\_clips\_dict

```python
generate_clips_dict(clips_df, sources_dict, parts_df)
```

Using clips_df and sources_dict, returns a clips_dict which acts as the
sole variable for the opentrons script &quot;clip.ot2.py&quot;.

#### generate\_final\_assembly\_dict

```python
generate_final_assembly_dict(constructs_list, clips_df, parts_df)
```

Using constructs_list and clips_df, returns a dictionary of final
assemblies with keys defining destination plate well positions and values
indicating which clip reaction wells are used.

#### calculate\_final\_assembly\_tipracks

```python
calculate_final_assembly_tipracks(final_assembly_dict)
```

Calculates the number of final assembly tipracks required ensuring
no more than MAX_FINAL_ASSEMBLY_TIPRACKS are used.

#### generate\_spotting\_tuples

```python
generate_spotting_tuples(constructs_list, spotting_vols_dict)
```

Using constructs_list, generates a spotting tuple
(Refer to &#x27;transformation_spotting_template.py&#x27;) for every column of
constructs, assuming the 1st construct is located in well A1 and wells
increase linearly. Target wells locations are equivalent to construct well
locations and spotting volumes are defined by spotting_vols_dict.

**Arguments**:

- `spotting_vols_dict` _dict_ - Part number defined by keys, spottting
  volumes defined by corresponding value.

#### generate\_ot2\_script

```python
generate_ot2_script(parent_dir, ot2_script_path, template_path, **kwargs)
```

Generates an ot2 script named &#x27;ot2_script_path&#x27;, where kwargs are
written as global variables at the top of the script. For each kwarg, the
keyword defines the variable name while the value defines the name of the
variable. The remainder of template file is subsequently written below.

#### generate\_master\_mix\_df

```python
generate_master_mix_df(clip_number)
```

Generates a dataframe detailing the components required in the clip 
reaction master mix.

#### generate\_sources\_paths\_df

```python
generate_sources_paths_df(paths, deck_positions)
```

Generates a dataframe detailing source plate information.

**Arguments**:

- `paths` _list_ - list of strings specifying paths to source plates.
- `deck_positions` _list_ - list of strings specifying candidate deck positions.

#### dfs\_to\_csv

```python
dfs_to_csv(path, index=True, **kw_dfs)
```

Generates a csv file defined by path, where kw_dfs are
written one after another with each key acting as a title. If index=True,
df indexes are written to the csv file.

#### handle\_2\_columns

```python
handle_2_columns(datalist)
```

This function has the intent of changing:
(&#x27;A8&#x27;, &#x27;2&#x27;) =&gt; (&#x27;A8&#x27;, &#x27;&#x27;, &#x27;2&#x27;)
(&#x27;A8&#x27;, &#x27;&#x27;, &#x27;2&#x27;) =&gt; (&#x27;A8&#x27;, &#x27;&#x27;, &#x27;2&#x27;)
[(&#x27;E2&#x27;, &#x27;5&#x27;)] =&gt; [(&#x27;E2&#x27;, &#x27;&#x27;, &#x27;5&#x27;)]
[(&#x27;G1&#x27;, &#x27;&#x27;, &#x27;5&#x27;)] =&gt; [(&#x27;G1&#x27;, &#x27;&#x27;, &#x27;5&#x27;)]
with the purpose of handling 2 column csv part file inputs,
as at times when 2 column csv files are input it creates tuples
of length 2 instead of 3

#### final\_well

```python
final_well(sample_number)
```

Determines well containing the final sample from sample number.

