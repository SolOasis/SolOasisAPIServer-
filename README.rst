drone API Server
================

Prerequisites:
--------------

See requirements.txt.

-  python 2.7, with threading support
-  `arsdkxml <https://pypi.python.org/pypi/arsdkxml>`__
-  `bybop <https://pypi.python.org/pypi?:action=display&name=bybop>`__
-  flask
-  flask-cor
-  ... For testing Manager.py:
-  pygame
-  PIL(pillow) For Heroku:
-  Gunicorn

Installation
------------

::

    pip install -r requirements.txt
    git clone https://amjltc295@bitbucket.org/larvata-tw/1111-drones-fort.git <directory name>

Files
-----

::

    src/                    Directory for main app
        __init__.py         Empty for library
        API.py              API server in flask
        Mangager.py         Manager class and tests
        Monitor.py          Class Monitor and its threads for drones
        dbMangage.py        DB migration manager
        drones/
            __init__.py     Empty for library
            Drone.py        Abstract class for all drones
            ParrotDrones.py Drones and discovery inheritance for Parrot Drones (Bebop)
        migrations/         Directory for database migration

    test/
        __init__.py         Empty for library
        testAPI.sh          Test shell for API URLs
        testPicutre.sh      Test shell for API URLs of getPicture
        data/               Pickle data from real drone for test
        drones/             Testdrone class for test

    LICENSE                 LICENSE file, need to be modified
    Procfile                Specification of main app for Heroku
    README.md               This file
    requirements.txt        For pip installation, need Gunicorn for Heroku
    runtime.txt             Specification of Python version for Heroku

Tests
-----

1. Connect to the Bebop Drone with Wifi

2. Test Manager \`\`\` cd python src/Manager.py

::


    3. Test API server

python src/API.py 
bash test/testAPI.sh 
bash tees/testPicture.sh

or

Open the browser: 
localhost:5000/drone/api/v1.0/search
localhost:5000/drone/api/v1.0/assign
localhost:5000/drone/api/v1.0/battery/0
...

or

Heroku https://young-woodland-12457.herokuapp.com/ Heroku (with
authentication) http://drone-api-server-stage.herokuapp.com/



API commands
------------

::
users 
GET
users/api/v1.0/register
users/api/v1.0/users
users/api/v1.0/users/ 
users/api/v1.0/token 
users/api/v1.0/testlogin

POST users/api/v1.0/users

drone 
GET
drone/api/v1.0/search 
drone/api/v1.0/assign
drone/api/v1.0/connecteddrones 
drone/api/v1.0/drones
drone/api/v1.0/drones/ 
drone/api/v1.0/battery/ 
drone/api/v1.0/regain/
drone/api/v1.0/getpicture/

PATCH drone/api/v1.0/navigate/

Status
------

This project is a work in progress, and thus is not stable, in every
possible way: \* Current error handling is almost non-existant (so most
error will lead to a crash) \* Current API (Bybop\_Device) is non-final
and will probably change in the future

Authors
-------

`Ya-Liang Chang <https://github.com/amjltc295>`__

License
-------

This project is under BSD 3-clause "New" or "Revised" License.

Acknowledgments
---------------

The bybop library was from `Nicolas BRÛLEZ's
bybop <https://github.com/N-Bz/bybop>`__
