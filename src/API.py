#!/usr/bin/env python
from Manager import Manager
from flask import Flask, jsonify, request

app = Flask(__name__, static_url_path="")

drone_manager = Manager()


@app.route('/drone/api/v1.0/search', methods=['GET'])
def searchAllDevices():
    all_devices = drone_manager.searchAllDevices()
    return jsonify({'controller_name': drone_manager.discovery.controller_name,
                    'd2c_port': drone_manager.discovery.d2c_port,
                    'devicesNum': len(all_devices)})


@app.route('/drone/api/v1.0/drones', methods=['GET'])
def getAllDrones():
    drones = dict()
    for each in drone_manager.all_devices:
        print (type(each))
        drones[len(drones)] = each
    return jsonify(drones)


@app.route('/drone/api/v1.0/assign', methods=['GET'])
def assignDrone():
    droneID = drone_manager.assignDrone()
    print (drone_manager.getDroneBattery(droneID))
    return jsonify({'droneID': droneID})


@app.route('/drone/api/v1.0/battery/<drone>', methods=['GET'])
def getDroneBattery(drone):
    battery = drone_manager.getDroneBattery(drone)
    return jsonify({'drone': drone,
                    'battery': battery})


@app.route('/drone/api/v1.0/state/<drone>', methods=['GET'])
def getDroneState(drone):
    state = drone_manager.getDroneState(drone)
    return jsonify({'drone': drone,
                    'state': state})


@app.route('/drone/api/v1.0/regain/<drone>', methods=['GET'])
def regainDrone(drone):
    state = drone_manager.regainDrone(drone)
    return jsonify({'drone': drone,
                    'state': state,
                    'regain': True})


@app.route('/drone/api/v1.0/navigate/<drone>', methods=['POST'])
def navigate(drone):
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
                    'navigation': True})


if __name__ == "__main__":
    app.run(debug=True)
