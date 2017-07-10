# drone API Server

## Prerequisites:

* python 2.7, with threading support
* [arsdkxml](https://pypi.python.org/pypi/arsdkxml)
* [bybop](https://pypi.python.org/pypi?:action=display&name=bybop)
* flask
For testing Manager.py:
* pygame
* PIL

## Installation

```
pip install -r requirements.txt
git clone https://amjltc295@bitbucket.org/larvata-tw/1111-drones-fort.git <directory name>
```

## Files

```
src/
    __init__.py         Empty for library
    API.py              API server in flask
    Mangager.py         Manager class and tests
    Monitor.py          Class Monitor and its threads for drones
    drones/
        __init__.py     Empty for library
        Drone.py        Abstract class for all drones
        ParrotDrones.py Drones and discovery inheritance for Parrot Drones (Bebop)

test/
    testAPI.sh          Test shell for API URLs
    testPicutre.sh      Test shell for API URLs of getPicture

LICENSE                 LICENSE file, need to be modified
README.md               This file
requirements.txt        For pip installation
```


## Tests

1. Connect to the Bebop Drone with Wifi

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
localhost:5000/drone/api/v1.0/search
localhost:5000/drone/api/v1.0/assign
localhost:5000/drone/api/v1.0/battery/0
...
```

## API commands

```
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
drone/api/v1.0/navigate/<droneID>
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


