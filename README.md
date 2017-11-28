# SolOasis API Server

## Prerequisites:

See requirements.txt.

* python 3.6, with threading support
* flask
* flask-cor
* flask-httpauth
* ...
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

## Prototype
![Prototype](./images/prototype.png?raw=true)


## Files

```
src/                    Directory for main app
    .env                Setting for Database and Config
    __init__.py         Empty for library
    API.py              API server in flask
    Mangager.py         Manager class and tests
    config.py           Configuration for flask environment
    dbMangage.py        DB migration manager
    dbModel.py          Used to clean database version problem
    migrations/         Directory for database migration
    SolOasisStation.py  SolOasis Station class
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

1. Test for microcontroller side

The API server is deployed on [https://desolate-depths-35197.herokuapp.com/]

Use POST method on https://desolate-depths-35197.herokuapp.com/SolOasis/api/v1.0/update/ with json data to update battery percentage.


The json data would be like 
```
{"ID": (ID of the SolOasis Station),

 "data": (data in dictionary)}
```
For example (using curl on Linxu):
```
 curl -H "Content-Type: application/json" -X POST -d '{"ID":0,"data":{"percentage":40}}' https://desolate-depths-35197.herokuapp.com/SolOasis/api/v1.0/update/
```

Then the update result could be seen using GET method:

https://desolate-depths-35197.herokuapp.com/SolOasis/api/v1.0/battery/0

Ther result should be like:
```
{
      "StationID": "0", 
      "battery": (the updated value), 
      "function": "getStationBattery()"
}
```


## API commands

```
POST
/SolOasis/api/v1.0/update


GET
/SolOasis/api/v1.0/stations
/SolOasis/api/v1.0/battery/(ID)
/SolOasis/api/v1.0/gps/(ID)
```

## Status

This project is a work in progress, and thus is not stable.

## Authors

[Ya-Liang Chang](https://github.com/amjltc295)

## License

MIT

## Acknowledgments

I have to thank Dr. Samuel Dickerson and Dr. Ahmed Dallal for their assistance and amazing design of the Senior Design Project course schedule. They are really helpful. 
I would also like to thank my teammates Aric, Chris and Sofia. Without their great efforts this project would have never been accomplished.

