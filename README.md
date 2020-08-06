# DJANGO-Assembly-Methods 🔬

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/Imperial-iGEM/DJANGO-Assembly-Methods/Django%20CI)
![GitHub repo size](https://img.shields.io/github/repo-size/Imperial-iGEM/DJANGO-Assembly-Methods)
![GitHub search hit counter](https://img.shields.io/github/search/Imperial-iGEM/DJANGO-Assembly-Methods/goto)

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

`$ cd ..`

`$ virtualenv -p $(which python3.7) venv`

activate the virtual enviroment

`$ source venv/bin/activate`

Install our repositry dependencies inside requirements.txt

`$ cd DJANGO-Assembly-Methods`

`$ pip install -r requirements.txt`

Run server

`$ python manage.py migrate`

`$ python manage.py runserver`

## testing the RESTAPI 🧬

once your server in running as we left our machine in the previous stage, we can use the GUI django rest framework provides to test out our two end points!

### Basic DNA Assembly 🦠
You can acess the root of the end point on your local machine when the server is running by navigating to the link
> http://127.0.0.1:8000/

and click on the `/Basic` end point or alternatively navigate directly to
> http://127.0.0.1:8000/Basic

Whilst here you can post a request to our backend with the test parameters

`ethanol_well_for_stage_2 = "A11"`

`deep_well_plate_stage_4 = "A1"`

`input_construct_path = ...` file can be downloaded from https://cutt.ly/kdF6sHw

`output_sources_paths = ...` file can be downloaded from https://cutt.ly/jdF6k15

Once these four attributes of the GUI's post request are filled we can submit the post request by clicking post in the bottom left corner. The object is returned with 4 additional attributes containing the output OT2 opentrons python API scripts

### Moclo DNA Assembly 🧑‍🔬
You can acess the root of the end point on your local machine when the server is running by navigating to the link
> http://127.0.0.1:8000/Moclo

and click on the `/Basic` end point or alternatively navigate directly to
> http://127.0.0.1:8000/Moclo/Moclo

Whilst here you can post a request to our backend with the test parameters

`combinations_limit = "single"`

`dna_plate_map_file = ...` file can be downloaded from https://cutt.ly/kdF59QR

`combinations file = ...` file can be downloaded from https://cutt.ly/PdF6qNP

Once these four attributes of the GUI's post request are filled we can submit the post request by clicking post in the bottom left corner. The object is returned with 2 additional attributes containing the output OT2 opentrons python API script as well as agar plate locations csv file

## Interested in Contributing 🤔💡

We welcome everyone interested in contrubuting if your a seasoned open source professional or interested in learning something new fell free to open issues and pull requests.

If you have any specific questions feel free to send an email to the 2020 imperial igem team 🚀
> imperialigem2020@gmail.com


