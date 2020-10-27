---
sidebar_label: basic_assembly.dna_bot.dnabot_app
title: basic_assembly.dna_bot.dnabot_app
---

#### dnabot

```python
dnabot(output_folder: str, ethanol_well_for_stage_2: str, deep_well_plate_stage_4: str, input_construct_path: List[str], output_sources_paths: List[str], p10_mount: str = 'right', p300_mount: str = 'left', p10_type: str = 'p10_single', p300_type: str = 'p300_multi', well_plate: str = 'biorad_96_wellplate_200ul_pcr', reagent_plate: str = 'usascientific_12_reservoir_22ml', mag_plate: str = 'biorad_96_wellplate_200ul_pcr', tube_rack: str = 'opentrons_24_tuberack_nest_1.5ml_snapcap', aluminum_block: str = 'opentrons_96_aluminumblock_biorad_wellplate_200ul', bead_container: str = 'usascientific_96_wellplate_2.4ml_deep', soc_plate: str = 'usascientific_96_wellplate_2.4ml_deep', agar_plate: str = 'thermofisher_96_wellplate_180ul') -> List[str]
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
  

**Returns**:

  List of output paths
  If there is an exception, the list of output paths will contain
  only one element = the error path
  Otherwise the list of output paths will contain:
  OT-2 script paths (clip, thermocycle, purification, assembly,
  transformation), metainformation (clip run info, final assembly
  dict, wells - ethanol well and soc well)

#### generate\_constructs\_list

```python
generate_constructs_list(path: str) -> List[pd.DataFrame]
```

Generates a list of dataframes corresponding to each construct. Each
dataframe lists components of the CLIP reactions required.
Args: path = the absolute path of the constructs file
Returns: List of dataframes, in which each dataframe = construct

#### generate\_clips\_df

```python
generate_clips_df(constructs_list: List[pd.DataFrame]) -> pd.DataFrame
```

Generates a dataframe containing information about all the unique clip
reactions required to synthesise the constructs in constructs_list.
Args: list of constructs stored as dataframes
Returns: dataframe of all constructs

#### generate\_sources\_dict

```python
generate_sources_dict(paths: List[str]) -> Tuple[Dict[str, Tuple], pd.DataFrame]
```

Imports csvs files containing a series of parts/linkers with
corresponding information into a dictionary where the key corresponds with
part/linker and the value contains a tuple of corresponding information.

**Arguments**:

- `paths` _list_ - list of strings each corresponding to a path for a
  sources csv file.

**Returns**:

- `sources_dict` - a dictionary with keys = part names, values = tuple of
  values - either well, concentration, plate or well, plate depending on
  whether concentration is provided for the part
- `parts_df` - dataframe of parts with cols = concentration, name, well,
  plate

#### fill\_parts\_df

```python
fill_parts_df(clips_df: pd.DataFrame, parts_df_temp: pd.DataFrame) -> pd.DataFrame
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
generate_clips_dict(clips_df: pd.DataFrame, sources_dict: Dict[str, Tuple], parts_df: pd.DataFrame) -> Dict[str, List]
```

Using clips_df and sources_dict, returns a clips_dict which acts as the
sole variable for the opentrons script &quot;clip.ot2.py&quot;.

**Arguments**:

- `clips_df` - dataframe of clip reactions
- `sources_dict` - dictionary of parts with csv values as keys
- `parts_df` - dataframe of parts

**Returns**:

- `clips_dict` - dictionary to be used by 1_clip.ot2.py

#### generate\_final\_assembly\_dict

```python
generate_final_assembly_dict(constructs_list: pd.DataFrame, clips_df: pd.DataFrame, parts_df: pd.DataFrame) -> Tuple[Dict[str, List[str]], pd.DataFrame, pd.DataFrame]
```

Using constructs_list and clips_df, returns a dictionary of final
assemblies with keys defining destination plate well positions and
values indicating which clip reaction wells are used.

**Arguments**:

- `constructs_list` - list of constructs, constructs = dataframes
- `clips_df` - dataframe of clip reactions
- `parts_df` - dataframe of parts

**Returns**:

  dictionary of final assemblies with keys = destination plate,
  values = list of clip wells
  clips_df and parts_df updated with construct well column

#### calculate\_final\_assembly\_tipracks

```python
calculate_final_assembly_tipracks(final_assembly_dict: Dict[str, List[str]]) -> int
```

Calculates the number of final assembly tipracks required ensuring
no more than MAX_FINAL_ASSEMBLY_TIPRACKS are used.
Args: final_assembly_dict = dictionary with keys = final assembly
wells, values = list of clip wells
Returns: number of tipracks needed in final assembly
(3_assembly.ot2.py)
Raises: ValueError if final assembly tiprack number &gt; tiprack slots

#### generate\_spotting\_tuples

```python
generate_spotting_tuples(constructs_list: List[pd.DataFrame], spotting_vols_dict: Dict[int, int]) -> List[Tuple]
```

Using constructs_list, generates a spotting tuple
(Refer to &#x27;transformation_spotting_template.py&#x27;) for every column of
constructs, assuming the 1st construct is located in well A1 and wells
increase linearly. Target wells locations are equivalent to construct well
locations and spotting volumes are defined by spotting_vols_dict.

**Arguments**:

- `spotting_vols_dict` _dict_ - Part number defined by keys, spotting
  volumes defined by corresponding value.

**Returns**:

  List of three tuples as instructions for transformation script

#### generate\_ot2\_script

```python
generate_ot2_script(parent_dir, ot2_script_path, template_path, **kwargs)
```

Generates an ot2 script named &#x27;ot2_script_path&#x27;, where kwargs are
written as global variables at the top of the script. For each kwarg, the
keyword defines the variable name while the value defines the name of the
variable. The remainder of template file is subsequently written below.

**Arguments**:

- `parent_dir` _str_ - output folder dir
- `ot2_script_path` _str_ - where the script should be saved, relative to
  the parent_dir
- `template_path` _str_ - where the template script can be found

**Returns**:

  absolute path of script (str)

#### generate\_master\_mix\_df

```python
generate_master_mix_df(clip_number: int) -> pd.DataFrame
```

Generates a dataframe detailing the components required in the clip
reaction master mix.
Args: Number of clips needed in total
Returns: master mix dataframe containing reagents + volumes

#### generate\_sources\_paths\_df

```python
generate_sources_paths_df(paths: List[str], deck_positions: List[str]) -> pd.DataFrame
```

Generates a dataframe detailing source plate information.

**Arguments**:

- `paths` _list_ - list of strings specifying paths to source plates.
- `deck_positions` _list_ - list of strings specifying candidate deck
  positions.

**Returns**:

  Dataframe containing source plate information

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
final_well(sample_number: int) -> str
```

Determines well containing the final sample from sample number.
Args: sample_number = integer, e.g. 0 = well index
Returns: well in string form, e.g. &#x27;A1&#x27; if sample_number = 0

