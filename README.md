# drone API Server

## Prerequisites:

See requirements.txt.

* python 2.7, with threading support
* [arsdkxml](https://pypi.python.org/pypi/arsdkxml)
* [bybop](https://pypi.python.org/pypi?:action=display&name=bybop)
* flask
* flask-cor
* flask-soketio
* flask-httpauth
* ...
For testing Manager.py:
* pygame
* PIL(pillow)
For Heroku:
* Gunicorn


## Installation

```
git clone <this repository> <directory name>
cd <directory name>
(Create virtual environment)
pip install -r requirements.txt
source src/.env
```

## Documentation generation

```
bash ReadmeMD2RST.sh
cd docs
make html
cd ..
```

HTML files would be in docs/\_build\html


## Heroku deployment

See [here](https://realpython.com/blog/python/flask-by-example-part-1-project-setup/).

Using modified Procfile here for production.

## State
![StateImg](./images/stateImg.png?raw=true)


## Files

```
src/                    Directory for main app
    .env                Setting for Database and Config
    __init__.py         Empty for library
    API.py              API server in flask
    Mangager.py         Manager class and tests
    Monitor.py          Class Monitor and its threads for drones
    config.py           Configuration for flask environment
    dbMangage.py        DB migration manager
    dbModel.py          Used to clean database version problem
    data/               Pickle data from real drone for test
    drones/
        __init__.py     Empty for library
        Drone.py        Abstract class for all drones
        ParrotDrones.py Drones and discovery inheritance for Parrot Drones (Bebop)
        TestDrones.py   Testdrone class for test
    migrations/         Directory for database migration
    templates/          Templates for test websites


test/
    .env                Setting for testing Database and Config
    __init__.py         Empty for library
    testAPI.sh          Test shell for API URLs
    testAPI.py          Unittest for API URLs
    testManager.py      Unittest for Manager
    testPicutre.sh      Test shell for API URLs of getPicture

docs/                   Docstrings gereneration usign Sphinx (make html)
images/                 Images for README
LICENSE                 LICENSE file, need to be modified
Procfile                Specification of main app for Heroku
README.md               This file
ReadmeMD2RST.sh         README.md to README.rst for documentaion
README.rst              README for doc
requirements.txt        For pip installation, need Gunicorn for Heroku
runtime.txt             Specification of Python version for Heroku
```


## Tests

~~ 1. Connect to the Bebop Drone with Wifi ~~

(For Testdrone, a real drone is not required since it get data from the pickle file.)

2. Test Manager
```
cd <directory name>
python src/Manager.py

```

3. Test API server
```
python src/API.py
bash test/testAPI.sh
bash tees/testPicture.sh

or

Open the browser:
localhost:5000
localhost:5000/drone/api/v1.0/search
localhost:5000/drone/api/v1.0/assign
localhost:5000/drone/api/v1.0/battery/0
...

or 

Heroku
https://young-woodland-12457.herokuapp.com/
Heroku
http://drone-api-server-stage.herokuapp.com/
```

4. Unittest

```
cd test
cd test
source .env
python testAPI.py
python testManager.py
```

## API commands

```
users
GET
users/api/v1.0/register
users/api/v1.0/users
users/api/v1.0/users/<id>
users/api/v1.0/token
users/api/v1.0/testlogin

POST
users/api/v1.0/users


drone
GET
drone/api/v1.0/search
drone/api/v1.0/assign
drone/api/v1.0/connecteddrones
drone/api/v1.0/drones
drone/api/v1.0/drones/<droneID>
drone/api/v1.0/battery/<droneID>
drone/api/v1.0/regain/<droneID>
drone/api/v1.0/getpicture/<droneID>

PATCH
drone/api/v1.0/navigate/
```

## Status

This project is a work in progress, and thus is not stable, in every possible way:

 * Current error handling is almost non-existant (so most error will lead to a crash)

 * Current API (Bybop_Device) is non-final and will probably change in the future
 
## Authors

[Ya-Liang Chang](https://github.com/amjltc295)

## License

This project is under BSD 3-clause "New" or "Revised" License.

## Acknowledgments

The bybop library was from [Nicolas BRÛLEZ's bybop](https://github.com/N-Bz/bybop)


