#!/usr/bin/env python
from Manager import Manager
from flask import Flask, jsonify, request, send_file, render_template

app = Flask(__name__, static_url_path="")

drone_manager = Manager()


@app.route('/')
@app.route('/index', methods=['GET'])
def index():
    """ Index of the API server. """
    return render_template('index.html')


@app.route('/drone/api/v1.0/search', methods=['GET'])
def searchAllDevices():
    """ Search all available devices.
    Use when boot.

    Returns:
        function: function name
        controller_name, d2c_port: controller infomations
        devicesNum: device number
    """
    all_devices = drone_manager.searchAllDevices()
    return jsonify({'controller_name': drone_manager.discovery.controller_name,
                    'd2c_port': drone_manager.discovery.d2c_port,
                    'function': 'searchAllDevices()',
                    'devicesNum': len(all_devices)})


@app.route('/drone/api/v1.0/connecteddrones', methods=['GET'])
def getAllDrones():
    """ Get all connected drones infomations.

    Returns:
        function: function name
        dict of connected drones: (droneID: droneName)

    """
    drones = dict()
    for key in drone_manager.all_drones:
        each_drone = drone_manager.all_drones[key]
        ID, name = each_drone.getInfo()
        drones[ID] = name
    drones['function'] = 'getAllDrones()'
    return jsonify(drones)


@app.route('/drone/api/v1.0/drones', methods=['GET'])
def getAllDevices():
    """ Get all devices informations.

    Returns:
        function: function name
        dict of devices: (droneID: droneName)

    """
    devices = dict()
    for each_device in drone_manager.all_devices:
        devices[len(devices)] = each_device
    devices['function'] = 'getAllDevices()'
    return jsonify(devices)


@app.route('/drone/api/v1.0/assign', methods=['GET'])
def assignDrone():
    """ Connect and assign a new drone to client.

    Returns:
        function: function name
        droneID: assigned droneID for further instuctions.

    """
    droneID = drone_manager.assignDrone()
    print (drone_manager.getDroneBattery(droneID))
    return jsonify({'droneID': droneID,
                    'function': 'assignDrone()'})


@app.route('/drone/api/v1.0/battery/<drone>', methods=['GET'])
def getDroneBattery(drone):
    """ Get battery percentage of the drone.

    Args:
        drone: droneID of the drone.

    Returns:
        function: function name
        drone: droneID of the drone.
        battery: battery in percentage of the drone.

    """
    battery = drone_manager.getDroneBattery(drone)
    return jsonify({'drone': drone,
                    'function': 'getDroneBattery()',
                    'battery': battery})


@app.route('/drone/api/v1.0/drones/<drone>', methods=['GET'])
def getDroneState(drone):
    """ Get internal state of the drone.

    Args:
        drone: droneID of the drone.

    Returns:
        function: function name
        drone: droneID of the drone.
        state: internal state of the dron in multi-layer dictinary.

    """
    state = drone_manager.getDroneState(drone)
    return jsonify({'drone': drone,
                    'function': 'getDroneState()',
                    'state': state})


@app.route('/drone/api/v1.0/regain/<drone>', methods=['GET'])
def regainDrone(drone):
    """ Regain drone control from the client.
    Used when lost connection as well.

    Args:
        drone: droneID of the drone.

    Returns:
        function: function name
        drone: droneID of the drone.
        state: if regain drone successfully.
               False for undefinded drones or other errors.

    """
    state = drone_manager.regainDrone(drone)
    return jsonify({'drone': drone,
                    'state': state,
                    'function': 'regainDrone()'})


@app.route('/drone/api/v1.0/getpicture/<drone>', methods=['GET'])
def getPicture(drone):
    """ Get the last picture in the drone.
    If new picture are just taken, it may not get the latest one.

    Args:
        drone: droneID of the drone.

    Returns:
        stringIO of the image.
    """
    img = drone_manager.getPicture(drone)
    img.seek(0)
    return send_file(img, 'image/jpg')


@app.route('/drone/api/v1.0/navigate/<drone>', methods=['PATCH'])
def navigate(drone):
    """ Move to the given GPS location.

    Form Args:
        x: latitude
        y: longitude
        z: altitude
        o: orientation mode
        h: heading

    Returns:
        function: function name
        drone: droneID of the drone.
        state: 0 OK, 1 ERROR, 2 TIMEOUT
    """

    droneID = int(request.form['droneID'])
    x = int(request.form['x'])
    y = int(request.form['y'])
    z = int(request.form['z'])
    o = int(request.form['o'])
    h = int(request.form['h'])
    destination = (x, y, z, o, h)
    state = drone_manager.navigate(droneID, destination)
    return jsonify({'drone': droneID,
                    'state': state,
                    'function': 'navigate()'})


if __name__ == "__main__":
    app.run(debug=True)
