---
sidebar_label: sbol_parser_api.sbolParserApi
title: sbol_parser_api.sbolParserApi
---

## ParserSBOL Objects

```python
class ParserSBOL()
```

#### generate\_csv

```python
 | generate_csv(assembly: str, dictOfParts: Dict[str, Dict[str, Union[str, int, float]]] = None, repeat: bool = False, maxWellsFilled: int = 96, numRuns: int = 1) -> Dict[str, List[str]]
```

Create construct and parts/linkers CSVs for DNABot input

**Arguments**:

- `assembly(str)` - Assembly type.
  dictOfParts (Dict[str, Dict[str, Union[str, int, float]]]):
  Dictionary of information regarding parts to be assembled.
  Structure:
  {&lt;display ID&gt;: {&#x27;concentration&#x27;:..., &#x27;plate&#x27;:..., &#x27;well&#x27;:...}}
- `repeat` _bool_ - If False, removes constructs that contain repeated
  components. (default: False)
- `maxWellsFilled` _int_ - Number of wells to be filled in the
  constructs plate. (default: 96)
- `numRuns` _int_ - Number of runs (i.e. construct plates) to be
  created. (default: 1)

**Returns**:

- `Dict[str,List[str]]` - Dictionary containing lists of paths to csvs
  generated.

#### getRootComponentDefinitions

```python
 | getRootComponentDefinitions(sbolDocument: Document = None) -> List[ComponentDefinition]
```

Get the root component definitions of an SBOL document.

**Arguments**:

- `sbolDocument` _Document_ - SBOL document from
  which to get root component definitions (default: self.doc)

**Returns**:

- `list` - List of root component definitions.

#### getRootCombinatorialDerivations

```python
 | getRootCombinatorialDerivations(sbolDocument: Document = None) -> List[CombinatorialDerivation]
```

Get the root combinatorial derivations of an SBOL Document.

**Arguments**:

- `sbolDocument` _Document_ - SBOL document from
  which to get root combinatorial derivations (default: self.doc)

**Returns**:

- `list` - List of root combinatorial derivations.

#### getListOfConstructs

```python
 | getListOfConstructs(listOfNonCombUris: List[str] = [], listOfCombUris: List[str] = []) -> List[ComponentDefinition]
```

Get the list of constructs (component definitions) specified by
the list of non-combinatorial URIs and combinatorial derivation URIs.
Expands combinatorial derivations.

**Arguments**:

- `listOfNonCombUris` _list_ - List of component definition
  URIs pointing to non-combinatorial designs.
- `listOfCombUris` _list_ - List of combinatorial derivation
  URIs pointing to combinatorial designs.

**Returns**:

- `list` - List of component definitions specifying constructs
  to be assembled

#### enumerator

```python
 | enumerator(derivation: CombinatorialDerivation) -> List[ComponentDefinition]
```

Get the list of constructs enumerated from a combinatorial derivation..

**Arguments**:

- `derivation` _CombinatorialDerivation_ - Combinatorial derivation
  to be enumerated.

**Returns**:

- `list` - List of component definitions specifying the
  enumerated constructs.

#### addChildren

```python
 | addChildren(originalTemplate: ComponentDefinition, originalComponent: Component, newParent: ComponentDefinition, children: List[ComponentDefinition])
```

Adds children to new parent component definition based on the
original template.

**Arguments**:

- `originalTemplate` _ComponentDefinition_ - Original template
  describing the design of the new parent
- `originalComponent` _Component_ - Variable component in the
  original template to be replaced in new parent
- `newParent` _ComponentDefinition_ - New component definition
  describing an enumerated design
- `children` _List[ComponentDefinition]_ - Children to be added
  to the new parent based on the variants

#### removeConstraintReferences

```python
 | removeConstraintReferences(newParent: ComponentDefinition, newComponent: Component)
```

Remove sequence constraints of the component in the component definition

**Arguments**:

- `newParent` _ComponentDefinition_ - Component definition containing
  the new component.
- `newComponent` _Component_ - Component to remove sequence
  constraints from.

#### createTemplateCopy

```python
 | createTemplateCopy(template: ComponentDefinition, displayId: str, version: str) -> ComponentDefinition
```

Create a copy of the template of the combinatorial derivation.

**Arguments**:

- `template` _ComponentDefinition_ - Template of the
  combinatorial derivation.
- `displayId` _str_ - Display ID to be assigned to the copy.
- `version` _str_ - Version of the copy.

**Returns**:

- `ComponentDefinition` - Copy of template.

#### getUniqueDisplayId

```python
 | getUniqueDisplayId(comp: ComponentDefinition = None, derivation: CombinatorialDerivation = None, displayId: str = None, version: str = None, dataType: str = None, doc: Document = None) -> str
```

Creates a unique display ID for an SBOL object.

**Arguments**:

- `comp` _ComponentDefinition_ - Component definition containing
  the SBOL object
- `derivation` _CombinatorialDerivation_ - Combinatorial derivation
  containing the SBOL object
- `displayId` _str_ - Base display ID for SBOL object.
- `version` _str_ - Version of SBOL object.
- `dataType` _str_ - Type of SBOL object.
- `doc` _str_ - SBOL Document containing the SBOL object.

**Returns**:

- `str` - Unique display ID of SBOL object.

#### concatenateChildrenDisplayId

```python
 | concatenateChildrenDisplayId(children: List[ComponentDefinition]) -> str
```

Concatenate the names of the variant child components.

**Arguments**:

- `children` _List[ComponentDefinition]_ - List of variant
  child components of an enumerated design (as
  component definition).

**Returns**:

- `str` - Concanated names of variant child components.

#### collectVariants

```python
 | collectVariants(vc: VariableComponent) -> List[ComponentDefinition]
```

Collect all variants within a variable component
of a combinatorial derivation.

**Arguments**:

- `vc` _VariableComponent_ - Variable component of a
  combinatorial derivation.

**Returns**:

- `List[ComponentDefinition]` - List of variants (as
  component definitions) contained within a
  variable component of a combinatorial derivation.

#### group

```python
 | group(variants: List[ComponentDefinition], repeat: str) -> List[List[ComponentDefinition]]
```

Groups variants based on combinatorial strategy.

**Arguments**:

- `variants` _List[ComponentDefintiion]_ - List of variants
  in a variable component.

**Returns**:

- `List[List[ComponentDefinition]]` - Groups of variants.

#### generateCombinations

```python
 | generateCombinations(groups: List[List[ComponentDefinition]], variants: List[ComponentDefinition], i: int, sets: List[ComponentDefinition])
```

Generate all possible subsets in a set of variants.

**Arguments**:

- `groups` _List[List[ComponentDefintiion]]_ - Groups of variants.
- `variants` _List[ComponentDefinition]_ - List of variants (as
  component definitions).
- `i` _int_ - Iterator.
- `sets` _List[ComponentDefinition]_ - Sets of variants.

#### filterConstructs

```python
 | filterConstructs(allConstructs: List[ComponentDefinition]) -> List[ComponentDefinition]
```

Removes constructs with repeated components.

**Arguments**:

- `allConstructs` _List[ComponentDefinition]_ - List of constructs
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

#### displayListOfParts

```python
 | displayListOfParts() -> List[str]
```

Displays list of parts used in the assembly of the constructs
in the SBOL document used to initialize the parser.

**Returns**:

- `List[str]` - List of display IDs of parts.

#### getListOfParts

```python
 | getListOfParts(allConstructs: List[ComponentDefinition] = []) -> List[ComponentDefinition]
```

Get list of parts (component defintions) from the list of
all constructs.

**Arguments**:

- `allConstructs` _list_ - List of all constructs to be assembled.

**Returns**:

- `list` - List of component definitions specifying parts used across
  all constructs to be assembled.

#### getSortedListOfParts

```python
 | getSortedListOfParts(listOfParts: List[ComponentDefinition]) -> List[ComponentDefinition]
```

Get a sorted list of parts (str) from the list of parts.
Sort by sbol2 displayId

**Arguments**:

- `listOfParts` _list_ - List of parts to be sorted. (generated
  by getListOfConstructs)

**Returns**:

- `list` - List of sorted parts (str)

#### getDictOfComponents

```python
 | getDictOfComponents(listOfConstructs: List[ComponentDefinition]) -> Dict[str, ComponentDefinition]
```

Get a dictionary of components (as component definitions)
from the list of constructs as
{construct.displayId: construct.components (as component definitions)}

**Arguments**:

- `listOfConstructs` _list_ - List of constructs

**Returns**:

- `dict` - Dictionary of components

#### fillPlateoPlates

```python
 | fillPlateoPlates(allContent: List[ComponentDefinition], contentName: str, numPlate: int = None, plate_class: plateo.Plate = None, maxWellsFilled: int = None, dictOfParts: Dict[str, Dict[str, Union[str, int, float]]] = None) -> List[plateo.Plate]
```

Generate a list of plateo plate objects from list of constructs

**Arguments**:

- `allContent` _list_ - List of constructs.
- `contentName` _str_ - Name of content (Construct or Part).
- `numPlate` _int_ - Number of plates to be generated (default = 1).
  plate_class (plateo.Plate):
  Class of plateo plate (default = Plate96).
- `maxWellsFilled` _int_ - Maximum number of filled wells on a plate.
  dictOfParts (Dict[str, Dict[str, Union[str, int, float]]]):
  Dictionary of parts and associated information

**Returns**:

- `list` - List of plates

#### getAllContentFromPlateoPlate

```python
 | getAllContentFromPlateoPlate(contentPlate: plateo.Plate, contentName: str) -> List[ComponentDefinition]
```

Get a list of all content (as component definitions) from a
Plateo plate.

**Arguments**:

- `contentPlate` _plateo.Plate_ - Plateo plate containing content.
- `contentName` _str_ - Name of content (Construct or Part).

**Returns**:

- `list` - List of all content (as component definitions).

#### getMinNumberOfBasicParts

```python
 | getMinNumberOfBasicParts(allConstructs: List[ComponentDefinition]) -> int
```

Get the minimum number of Part/Linker pairs required to perform
BASIC assembly for all constructs.

**Arguments**:

- `allConstructs` _list_ - List of all constructs as component
  definitions.

**Returns**:

- `int` - Number of Part/Linker paris for BASIC assembly.

#### getConstructCsvHeader

```python
 | getConstructCsvHeader(minNumberOfBasicParts: int) -> List[str]
```

Create header for Construct CSV for DNABot

**Arguments**:

- `minNumberOfBasicParts` _int_ - Minimum number of of Part/Linker
  pairs required to perform BASIC assembly for all constructs.

**Returns**:

- `List[str]` - List of strings describing header for Construct CSV.

#### getWellComponentDictFromPlateoPlate

```python
 | getWellComponentDictFromPlateoPlate(constructPlate: plateo.Plate, assembly: str) -> Dict[str, List[ComponentDefinition]]
```

Get a dictionary of wells containing components comprising
constructs (as component definitions) in the form
{Wellname:[Components]}

**Arguments**:

- `constructPlate` _plateo.Plate_ - Plateo plate containing constructs.
- `assembly` _str_ - Type of assembly.

**Returns**:

- `dict` - Dictionary of wells containing components.

#### getListFromWellComponentDict

```python
 | getListFromWellComponentDict(dictWellComponent: Dict[str, ComponentDefinition], assembly: str) -> List[str]
```

Get a concatenated list of wellname and components (as display ID)
comprising the construct from the dictionary of wells containing
constructs.

**Arguments**:

- `dictWellComponent` - Dictionary of wells containing constructs.
- `assembly` _str_ - Type of assembly.

**Returns**:

- `List[str]` - List of wellnames and components (as display ID).

#### getConstructDfFromPlateoPlate

```python
 | getConstructDfFromPlateoPlate(constructPlate: plateo.Plate, assembly: str) -> pd.DataFrame
```

Get dataframe of constructs from Plateo plate containing constructs.

**Arguments**:

- `constructPlate` _plateo.Plate_ - Plateo plate containing constructs.
- `assembly` _str_ - Type of assembly.

**Returns**:

- `pd.DataFrame` - Dataframe of constructs.

#### getConstructCsvFromPlateoPlate

```python
 | getConstructCsvFromPlateoPlate(constructPlate: plateo.Plate, assembly: str)
```

Convert construct dataframe into CSV and creates CSV file in the same
directory.

**Arguments**:

- `constructPlate` _plateo.Plate_ - Plateo plate containing constructs.
- `uniqueId` _str_ - Unique ID appended to filename.
- `assembly` _str_ - Type of assembly.

#### isLinker

```python
 | isLinker(part: ComponentDefinition) -> bool
```

Check whether a part is a linker.

**Arguments**:

- `part` _ComponentDefinition_ - Part to check.

**Returns**:

- `bool` - True if part is a linker. False otherwise.

#### getLinkerSP

```python
 | getLinkerSP(linker: ComponentDefinition) -> List[ComponentDefinition]
```

Get linker prefixes and suffixes.

**Arguments**:

- `linker` _ComponentDefinition_ - Linker to get prefix and suffix.

**Returns**:

- `List[ComponentDefinition]` - Linker prefix and suffix (as
  component definitions).

#### convertLinkerToSuffixPrefix

```python
 | convertLinkerToSuffixPrefix(listOfParts: List[ComponentDefinition]) -> List[ComponentDefinition]
```

Convert all linkers contained in a list of parts into linker
prefixes and suffixes.

**Arguments**:

- `listOfParts` _List[ComponentDefinition]_ - List of parts
  used in the assembly of all constructs.

**Returns**:

- `List[ComponentDefinition]` - List of parts with linkers
  converted into linker prefixes and suffixes.

#### getWellContentDictFromPlateoPlate

```python
 | getWellContentDictFromPlateoPlate(plateoPlate: plateo.Plate, contentName: str) -> Dict[str, Tuple[ComponentDefinition, float]]
```

Get the contents of a well based on well data.

**Arguments**:

- `plateoPlate` _plate.Plate_ - Plate to get well
  content from.
- `contentName` _str_ - Type of content in well (&quot;Construct&quot;
  or &quot;Part).

**Returns**:

  Dict[str, Tuple[ComponentDefinition, float]]: Dictionary
  of well content with wellname as keys, and component
  definition of the part or construct and concentration
  as values.

#### getListFromWellPartDict

```python
 | getListFromWellPartDict(dictWellPart: Dict[str, Tuple[ComponentDefinition, float]]) -> List[str]
```

Convert a dictionary of well contents into a list.

**Arguments**:

  dictWellPart (Dict[str, Tuple[ComponentDefinition, float]]):
  Dictionary of well contents in a plate.

**Returns**:

- `List[str]` - Formatted list of well contents.

#### getPartLinkerDfFromPlateoPlate

```python
 | getPartLinkerDfFromPlateoPlate(partPlate: plateo.Plate) -> pd.DataFrame
```

Get part/linker dataframe from a plate.

**Arguments**:

- `partPlate` _plateo.Plate_ - Plate containing parts used for the
  assembly of constructs.

**Returns**:

- `pd.DataFrame` - Dataframe of part/linkers and their associated
  wellname and concentration.

#### getPartLinkerCsvFromPlateoPlate

```python
 | getPartLinkerCsvFromPlateoPlate(constructPlate: plateo.Plate, assembly: str, dictOfParts: Dict[str, Dict[str, Union[str, int, float]]] = None)
```

Get part/linker CSV from plate.

**Arguments**:

- `constructPlate` _plateo.Plate_ - Construct plates from which
  parts and linkers are derived.
- `assembly` _str_ - Type of assembly.
  dictOfParts (Dict[str, Dict[str, Union[str, int, float]]]):
  Dictionary of parts and associated information.

#### is\_linkers\_order\_correct

```python
 | is_linkers_order_correct(construct: ComponentDefinition) -> bool
```

Check input construct components has the
order of -linker-part-linker...

**Arguments**:

- `construct` _ComponentDefinition_ - Constructs to check.

**Returns**:

- `bool` - True if linker order is correct.

#### validateBioBricksConstruct

```python
 | validateBioBricksConstruct(construct: ComponentDefinition) -> bool
```

Check that biobricks construct has the structure
plasmid-prefix-suffix.

**Arguments**:

- `construct` _ComponentDefinition_ - Construct to check.

**Returns**:

- `bool` - True if construct structure is correct.

