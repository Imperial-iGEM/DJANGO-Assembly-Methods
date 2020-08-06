# DJANGO-Assembly-Methods 🔬

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

once our server in running as we left our machine in the previous state we can use the GUI django rest framework provides to test out two end points work!

### Basic DNA Assembly
You can acess the root of the end point on your local machine when the server is running by navigating to the link
> http://127.0.0.1:8000/

and click on the `/Basic` end point or alternatively navigate directly to
> http://127.0.0.1:8000/Basic

Whilst here you can post a request to our backend with the test parameters
> 

