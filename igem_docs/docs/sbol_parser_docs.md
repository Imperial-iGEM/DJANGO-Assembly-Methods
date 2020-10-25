# SBOLParser

The SBOL Parser interprets and parses the assembly intent from genetic designs described using the SBOL standard (SBOL Version 2.3), and produces the appropriate data files for downstream script generation softwares. The SBOL Parser primarily utilizes [pySBOL2](https://github.com/SynBioDex/pySBOL2) for the processing of SBOL files, and [Plateo](https://github.com/Edinburgh-Genome-Foundry/Plateo) to plan and simulate the set-up of the laboratory environment for assembly protocols.

The assembly plan is inferred at the highest level of a hierarchical design - the root Component Definition. Each root Component Definition is treated as the construct to be assembled, and their corresponding Components are treated as parts that make up the construct. Currently, the SBOL Parser assumes only one level of assembly, and therefore any Components containing more nested designs are assumed to already be fully assembled beforehand.

A major feature of the SBOL standard (SBOL Version 2.2 and later) is the ability to describe large combinatorial design spaces through the use of Combinatorial Derivations. Based on the enumeration feature supported in [SBOL Designer](https://github.com/SynBioDex/SBOLDesigner), the SBOL Parser is capable of expanding Combinatorial Derivations into individual Component Definitions describing each construct variant. This facilitates the construction of large genetic libraries and complex genetic designs, making the experimental workflows such as Design of Experiments more tractable.

Each root Component Definition is distributed into the wells of construct plates, which are Plate objects provided by Plateo. The list of parts used across all assemblies is summarized and their corresponding Component Definitions are then similarly distributed into part plates. For the purposes of the software pipeline we have developed, the Plateo constructs are converted into CSVs as downstream input to the script generation software.

## Going Under the Hood

### Generating CSVs

The main workhorse of the SBOL Parser is the generate_csv() function. This is used to generate the input CSVs to downstream script generation softwares that produces the scripts for BASIC, GoldenGate (MoClo), and BioBricks assemblies on the Opentrons.

The process of generating the CSVs is as follows:

1. Get list of constructs from the SBOL Document (enumerating Combinatorial Derivations if necessary)
2. (Optional) Remove constructs with repeated parts
3. Take a random sample of constructs if the size of the list of constructs is greater than the desired number of constructs to be assembled
4. Distribute constructs and parts into respective Plateo Plateo objects
5. Create CSVs from Plateo Plate objects

```python
sbol_parser_api.ParserSBOL.generate_csv(
    assembly: str,
    part_info: Dict[str, Dict[str, Union[str, int, float]]] = None,
    repeat: bool = False,
    max_construct_wells: int = 96,
    num_runs: int = 1
)
```

#### Parameters

* `assembly (str)`: Assembly type. Currently accepts the values "basic", "moclo", and "bio_bricks".

* `part_info (Dict[str, Dict[str, Union[str, int, float]]])`: Dictionary of information regarding parts to be assembled. If no information is provided, the default value of concentration is 0, and the plates and wells are automatically assigned. Structure: {(Display ID): {'concentration':..., 'plate':..., 'well':...}}

* `repeat (bool)`:** If False, removes constructs that contain repeated components. (default: False)

* `max_construct_wells (int)`: Number of wells to be filled in the constructs plate. (default: 96)

* `num_runs (int)`: Number of runs (i.e. construct plates) to be created. (default: 1)

#### Returns

* `Dict[str, List[str]]`: Dictionary of construct and parts/linkers paths. Keys: 'construct_path', 'part_path'

#### Raises

* `ValueError`: If `assembly` is invalid.

### Enumeration

The enumeration functionality is based on the Java implementation of the same functionality used in SBOL Designer, with minor changes to improve the human readibility of the Component Definition Display IDs generated from enumeration. The purpose of enumeration is to expand the condensed SBOL representation of a combinatorial design space into the set of elements it comprises.

```python
sbol_parser_api.ParserSBOL.enumerator(
    derivation: CombinatorialDerivation
)
```

#### Parameters

* `derivation (CombinatorialDerivation)`: A Combinatorial Derivation to be enumerated. Enumeration is based on strategy assigned to the Combinatorial Derivation.

#### Returns

* `List[ComponentDefinition]`: List of Component Definitions specifying the enumerated constructs

### Filter

The purpose of the filter is to constrain the design space of assembly constructs based on user-defined parameter constraints. Currently, the filter is used to remove constructs that contain repeating parts that may lead to homologous recombination and are therefore undesirable. Future development of the SBOL Parser will focus on an improved adaptive implementation of the filter with more tunable parameters. This will allow the SBOL Parser to be responsive to upstream learning and modelling applications.

```python
filter_constructs(
    all_constructs: List[ComponentDefinition]
)
```

#### Parameters

* `all_constructs:` List of constructs to filter

#### Returns

* `List[ComponentDefinition]`: List of filtered constructs

### Filling Plateo Plates

SBOL objects describing the parts or constructs to be assembled are stored in Plateo classes such as Wells and Plates. The objective was two-fold: to provide an standard description of labware and experimental set-up as an alternative to unstandardized CSV inputs, as well as to pass Plateo objects directly to downstream applications without the need for an intermediary data format such as CSV or JSON. The current implementation of the SBOL Parser contains an in-built Plateo parser to generate the requisite CSVs for downstream script generation softwares.

```python
fill_plates(
    all_content: List[ComponentDefinition],
    content_name: str,
    num_plate: int = None,
    plate_class: plateo.Plate = None,
    max_construct_wells: int = None,
    part_info: Dict[str, Dict[str, Union[str, int, float]]] = None
)
```

#### Parameters

* `all_content (List[ComponentDefinition])`: List of constructs or parts

* `content_name (str)`: Type of well content ("construct" or "part")

* `num_plate (int)`: Number of plates to be filled (default: 1)

* `plate_class (plateo.Plate)`: Class of Plateo Plate (default: Plate96)

* `max_construct_wells`: Maximum number of filled wells on each plate

* `part_info`: Dictionary of parts their associated user-defined information

#### Returns

* `list`: List of Plateo plates

#### Raises

*  `ValueError`: If parameters given are not feasible to carry out

## SBOL Parser API

Refer to the API reference for the SBOL Parser for the full documentation.
