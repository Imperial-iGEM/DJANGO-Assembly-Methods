---
sidebar_label: sbol_parser_api.sbol_parser_api
title: sbol_parser_api.sbol_parser_api
---

## ParserSBOL Objects

```python
class ParserSBOL()
```

#### generate\_csv

```python
 | generate_csv(assembly: str, part_info: Dict[str, Dict[str, Union[str, int, float]]] = None, repeat: bool = False, max_construct_wells: int = 96, num_runs: int = 1) -> Dict[str, List[str]]
```

Create construct and parts/linkers CSVs for DNABot input

**Arguments**:

- `assembly` _str_ - Assembly type.
  part_info (Dict[str, Dict[str, Union[str, int, float]]]):
  Dictionary of information regarding parts to be assembled.
  Structure:
  {&lt;display ID&gt;: {&#x27;concentration&#x27;:..., &#x27;plate&#x27;:..., &#x27;well&#x27;:...}}
- `repeat` _bool_ - If False, removes constructs that contain repeated
  components. (default: False)
- `max_construct_wells` _int_ - Number of wells to be filled in the
  constructs plate. (default: 96)
- `num_runs` _int_ - Number of runs (i.e. construct plates) to be
  created. (default: 1)

**Returns**:

- `Dict[str,List[str]]` - Dictionary containing lists of paths to csvs
  generated.

**Raises**:

- `ValueError` - If `assembly` is invalid.

#### get\_root\_compdefs

```python
 | get_root_compdefs(sbol_document: Document = None) -> List[ComponentDefinition]
```

Get the root component definitions of an SBOL document.

**Arguments**:

- `sbol_document` _Document_ - SBOL document from
  which to get root component definitions (default: self.doc)

**Returns**:

- `list` - List of root component definitions.

#### get\_root\_combderivs

```python
 | get_root_combderivs(sbol_document: Document = None) -> List[CombinatorialDerivation]
```

Get the root combinatorial derivations of an SBOL Document.

**Arguments**:

- `sbol_document` _Document_ - SBOL document from
  which to get root combinatorial derivations (default: self.doc)

**Returns**:

- `list` - List of root combinatorial derivations.

#### get\_constructs

```python
 | get_constructs(non_comb_uris: List[str] = [], comb_uris: List[str] = []) -> List[ComponentDefinition]
```

Get the list of constructs (component definitions) specified by
the list of non-combinatorial URIs and combinatorial derivation URIs.
Expands combinatorial derivations.

**Arguments**:

- `non_comb_uris` _list_ - List of component definition
  URIs pointing to non-combinatorial designs.
- `comb_uris` _list_ - List of combinatorial derivation
  URIs pointing to combinatorial designs.

**Returns**:

- `list` - List of component definitions specifying constructs
  to be assembled

#### enumerator

```python
 | enumerator(derivation: CombinatorialDerivation) -> List[ComponentDefinition]
```

Get the list of constructs enumerated from a combinatorial derivation.

**Arguments**:

- `derivation` _CombinatorialDerivation_ - Combinatorial derivation
  to be enumerated.

**Returns**:

- `list` - List of component definitions specifying the
  enumerated constructs.

#### filter\_constructs

```python
 | filter_constructs(all_constructs: List[ComponentDefinition]) -> List[ComponentDefinition]
```

Removes constructs with repeated components.

**Arguments**:

- `all_constructs` _List[ComponentDefinition]_ - List of constructs
  to filter.

**Returns**:

- `List[ComponentDefinition]` - List of filtered constructs.

#### flatten

```python
 | flatten(construct: ComponentDefinition) -> List[ComponentDefinition]
```

Flattens a heirarchical component definition.

**Arguments**:

- `construct` _ComponentDefinition_ - Component definition to
  flatten.

**Returns**:

- `List[ComponentDefinition]` - Returns a list of component
  definitions corresponding to the components contained
  within the component definition including all
  nested components.

#### display\_parts

```python
 | display_parts() -> List[str]
```

Displays list of parts used in the assembly of the constructs
in the SBOL document used to initialize the parser.

**Returns**:

- `List[str]` - List of display IDs of parts.

#### get\_parts

```python
 | get_parts(all_constructs: List[ComponentDefinition] = []) -> List[ComponentDefinition]
```

Get list of parts (component defintions) from the list of
all constructs.

**Arguments**:

- `all_constructs` _list_ - List of all constructs to be assembled.

**Returns**:

- `list` - List of component definitions specifying parts used across
  all constructs to be assembled.

#### get\_sorted\_parts

```python
 | get_sorted_parts(parts: List[ComponentDefinition]) -> List[ComponentDefinition]
```

Get a sorted list of parts (str) from the list of parts.
Sort by sbol2 displayId

**Arguments**:

- `parts` _list_ - List of parts to be sorted.

**Returns**:

- `list` - List of sorted parts (str)

#### get\_comp\_dict

```python
 | get_comp_dict(constructs: List[ComponentDefinition]) -> Dict[str, ComponentDefinition]
```

Get a dictionary of components (as component definitions)
from the list of constructs as
{construct.displayId: construct.components (as component definitions)}

**Arguments**:

- `constructs` _list_ - List of constructs

**Returns**:

- `dict` - Dictionary of components

#### fill\_plates

```python
 | fill_plates(all_content: List[ComponentDefinition], content_name: str, num_plate: int = None, plate_class: plateo.Plate = None, max_construct_wells: int = None, part_info: Dict[str, Dict[str, Union[str, int, float]]] = None) -> List[plateo.Plate]
```

Generate a list of plateo plate objects from list of constructs

**Arguments**:

- `all_content` _list_ - List of constructs.
- `content_name` _str_ - Name of content (construct or part).
- `num_plate` _int_ - Number of plates to be generated (default: 1).
  plate_class (plateo.Plate):
  Class of plateo plate (default: Plate96).
- `max_construct_wells` _int_ - Maximum number of filled
  wells on a plate.
  part_info (Dict[str, Dict[str, Union[str, int, float]]]):
  Dictionary of parts and associated information

**Returns**:

- `list` - List of plates

**Raises**:

- `ValueError` - If parameters are not feasible.

#### get\_all\_content\_from\_plate

```python
 | get_all_content_from_plate(content_plate: plateo.Plate, content_name: str) -> List[ComponentDefinition]
```

Get a list of all content (as component definitions) from a
Plateo plate.

**Arguments**:

- `content_plate` _plateo.Plate_ - Plateo plate containing content.
- `content_name` _str_ - Name of content (&quot;construct&quot; or &quot;part&quot;).

**Returns**:

- `list` - List of all content (as component definitions).

#### get\_construct\_df\_from\_plate

```python
 | get_construct_df_from_plate(construct_plate: plateo.Plate, assembly: str) -> pd.DataFrame
```

Get dataframe of constructs from Plateo plate containing constructs.

**Arguments**:

- `construct_plate` _plateo.Plate_ - Plateo plate containing constructs.
- `assembly` _str_ - Type of assembly.

**Returns**:

- `pd.DataFrame` - Dataframe of constructs.

#### get\_construct\_csv\_from\_plate

```python
 | get_construct_csv_from_plate(construct_plate: plateo.Plate, assembly: str)
```

Convert construct dataframe into CSV and creates CSV file in the same
directory.

**Arguments**:

- `construct_plate` _plateo.Plate_ - Plateo plate containing constructs.
- `uniqueId` _str_ - Unique ID appended to filename.
- `assembly` _str_ - Type of assembly.

#### convert\_linker\_to\_sp

```python
 | convert_linker_to_sp(part_list: List[ComponentDefinition]) -> List[ComponentDefinition]
```

Convert all linkers contained in a list of parts into linker
prefixes and suffixes.

**Arguments**:

- `parts_list` _List[ComponentDefinition]_ - List of parts
  used in the assembly of all constructs.

**Returns**:

- `List[ComponentDefinition]` - List of parts with linkers
  converted into linker prefixes and suffixes.

#### get\_part\_linker\_df\_from\_plate

```python
 | get_part_linker_df_from_plate(part_plate: plateo.Plate) -> pd.DataFrame
```

Get part/linker dataframe from a plate.

**Arguments**:

- `part_plate` _plateo.Plate_ - Plate containing parts used for the
  assembly of constructs.

**Returns**:

- `pd.DataFrame` - Dataframe of part/linkers and their associated
  wellname and concentration.

#### get\_part\_linker\_csv\_from\_plate

```python
 | get_part_linker_csv_from_plate(construct_plate: plateo.Plate, assembly: str, part_info: Dict[str, Dict[str, Union[str, int, float]]] = None)
```

Get part/linker CSV from plate.

**Arguments**:

- `construct_plate` _plateo.Plate_ - Construct plates from which
  parts and linkers are derived.
- `assembly` _str_ - Type of assembly.
  part_info (Dict[str, Dict[str, Union[str, int, float]]]):
  Dictionary of parts and associated information.

