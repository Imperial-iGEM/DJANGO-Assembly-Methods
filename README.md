<p align="center">
  <img src="https://github.com/Imperial-iGEM/igem_frontend/blob/master/public/ourlogo.png" height="200"/>
</p>

# SOAPLab Backend

## DJANGO-Assembly-Methods 🔬

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/Imperial-iGEM/DJANGO-Assembly-Methods/Django%20CI)
![GitHub repo size](https://img.shields.io/github/repo-size/Imperial-iGEM/DJANGO-Assembly-Methods)
![GitHub search hit counter](https://img.shields.io/github/search/Imperial-iGEM/DJANGO-Assembly-Methods/goto)

hosted and available at:
http://app.soaplab.io/graphql

A django restframework with 2 endpoints `/Basic` and `/Moclo` to provide OT2 lab automation python scripts for the respective asembly methods from formatted CSV files

## getting set up 👨‍💻

Open your command line and create a directory in which you would like to work

Make a directory (recommended DJANGO-ASSEMBLY-METHODS)

`$ mkdir DJANGO-ASSEMBLY-METHODS`

change directory into your new directory

`$ cd DJANGO-ASSEMBLY-METHODS`

clone our repositry

`$ git clone https://github.com/Imperial-iGEM/DJANGO-Assembly-Methods.git`

create a venv inside root folder
```
$ cd ..
$ pip3 install virtualenv
$ virtualenv -p $(which python3.7) venv
```

activate the virtual enviroment

`$ source venv/bin/activate`

Install our repositry dependencies inside requirements.txt

`$ cd DJANGO-Assembly-Methods`

`$ pip install -r requirements.txt`

Run server

`$ python manage.py migrate`

`$ python manage.py collectstatic`

`$ python manage.py runserver`

## Continuous Intergration and Unittests ✅

For our Ci we use Github Actions, to check progress of you pull request click on the actions folder. Every push request is tested against a build on python 3.6, 3.7 and 3.8.

For out unit tests we use Django's built in offering, before making a pull request trying running this command in the root folder to initiate unit tests

`python manage.py test`

## Ensure PEP8 Code Style Compatability 📚

befor submitting a pull request to ensure high code quality navigate to the root folder of the project and run

```
$ cd ..
$ autopep8 -r --diff DJANGO-Assembly-Methods/
```
## testing the RESTAPI 🧬

once your server in running as we left our machine in the previous stage, we can use the GUI django rest framework provides to test out our two end points!

### Graphql

We implemented graphql technologies into our Django Backend with the python library graphene.
Because of this we only have 1 endpoint "/graphql"

## linkerList
> Note Full docs are available by clicking docs at top right of http://app.soaplab.io/graphql

One graphql mutation present at this endpoint is:

```python
linkerList(sbolFileString: String): LinkerList
```

The only argument sbolFileString is of type String; contains an SBOL file in string format
The only output is an array LinkerList; an array containing strings of each Part/Linker name inside the SBOL file

## Final Spec
> Note Full docs are available by clicking docs at top right of http://app.soaplab.io/graphql

The only other mutation present at the graphql endpoint is:

```python
finalSpec(
  assemblyType: String
  linkerTypes: [LinkerInType]
  sbolFileString: String
  specificationsBasic: InputSpecsBASIC
  specificationsBioBricks: InputSpecsBioBricks
  specificationsMoClo: InputSpecsMoClo
): FinalSpec
```
### AssemblyType

The first argument specifies the assembly type 'basic','moclo' or 'biobricks'

example
> 'basic'

### linkerTypes

The second argument is a json object specifiying partid, concentration, well and location

example
> [{
    "linkerId": "BBa_J23100",
    "concentration": 50,
    "plateNumber": 1,
    "well": "A1"
   },
   {"linkerId": "BBa_J23106",
    "concentration": 50,
    "plateNumber": 1,
    "well": "A2"
   },
   {"linkerId": "BBa_J23114",
    "concentration": 50,
    "plateNumber": 1,
    "well": "A3"
   },
  }]

### sbolFileString

The third argument is the same as the only argument at the linkerList mutation, a stringified SBOL file

example
> https://github.com/Imperial-iGEM/DJANGO-Assembly-Methods/blob/master/examples/sbol/basic_linkers_standard.xml

### specificationsBasic 🦠

The fourth argument is a object called InputSpecsBASIC which has the format displayed withing the example input

```python
"specificationsBasic": {
    "ethanolWellForStage2": "A1",
		"deepWellPlateStage4": "A11",
		"labwareDict": {
			"commonLabware": {
        "p10Mount": "right",
        "p300Mount": "left",
        "p10Type": "p10_single",
        "p300Type": "p300_single",
        "wellPlate": "biorad_96_wellplate_200ul_pcr"
      },
      "wellPlate": 1,
      "reagentPlate": "2",
      "magPlate": "String",
      "tubeRack": "String",
      "aluminumBlock": "String",
      "beadContainer": "String",
      "socPlate": "String",
      "agarPlate": "String"
    }
  },
```

### specificationsBioBricks 🧑‍🔬

The fifth argument is a object called InputSpecsBioBricks which has the format displayed withing the example input

```python
"specificationsBioBricks": {
    "labwareDict": {
      "commonLabware": {
        "p10Mount": "right",
        "p300Mount": "left",
        "p10Type": "p10_single",
        "p300Type": "p300_single",
        "wellPlate": "biorad_96_wellplate_200ul_pcr"
      },
      "tubeRack": "opentrons_24_tuberack_nest_1.5ml_snapcap",
      "socPlate": "usascientific_96_wellplate_2.4ml_deep",
      "transformationPlate": "corning_96_wellplate_360ul_flat"
    },
    "thermocycle": true
  }
```

### specificationsMoClo 🧑‍🔬

The sixth argument is a object called InputSpecsMoClo which has the format displayed withing the example input

```python
"specificationsMoClo": {
    "thermocycle": false, 
    "labwareDict": {
      "commonLabware": {
        "p10Mount": "right",
        "p300Mount": "left",
        "p10Type": "p10_single",
        "p300Type": "p300_single",
        "wellPlate": "4ti_0960_framestar"
      },
      "trough": "4ti-0131",
      "reagentPlate": "4ti_0960_framestar",
      "agarPlate": "thermofisher_96_wellplate_180ul"
    } 
  }
```

## Interested in Contributing 🤔💡

We welcome everyone interested in contrubuting if your a seasoned open source professional or interested in learning something new fell free to open issues and pull requests.

If you have any specific questions feel free to send an email to the 2020 imperial igem team 🚀
> imperialigem2020@gmail.com


