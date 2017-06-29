#!/usr/bin/env python
import sys
from Bybop_Discovery import Discovery, get_name, DeviceID
import Bybop_Device
from Manager import Manager
from flask import Flask, jsonify

app = Flask(__name__, static_url_path="")

drone_manager = Manager()


@app.route('/drone/api/v1.0/search', methods=['GET'])
def searchAllDevices():
    all_devices = drone_manager.searchAllDevices()
    return jsonify({'controller_name': drone_manager.controller_name,
                    'd2c_port': drone_manager.d2c_port,
                    'devicesNum': len(all_devices)})


@app.route('/drone/api/v1.0/drones', methods=['GET'])
def getAllDrones():
    drones = dict()
    each_drone = drone_manager.all_devices.itervalues().next()
    while each_drone:
        state = each_drone.get_state()
        drones[len(drones)] = state
        each_drone = drone_manager.all_devices.itervalues.next()
    return jsonify(drones)


@app.route('/drone/api/v1.0/assign', methods=['GET'])
def assignDrone():
    droneName = drone_manager.assignDrone()
    print (drone_manager.getDroneBattery(droneName))
    return jsonify({'droneName': droneName})


@app.route('/drone/api/v1.0/battery/<drone>', methods=['GET'])
def getDroneBattery(drone):
    battery = drone_manager.getDroneBattery(drone)
    return jsonify({'drone':drone,
                    'battery': battery})


@app.route('/drone/api/v1.0/state/<drone>', methods=['GET'])
def getDroneState(drone):
    state = drone_manager.getDroneState(drone)
    return jsonify({'drone':drone,
                    'state': state})


@app.route('/drone/api/v1.0/regain/<drone>', methods=['GET'])
def regainDrone(drone):
    state = drone_manager.regainDrone(drone)
    return jsonify({'drone':drone,
                    'state': state,
                    'regain': True})

if __name__ == "__main__":
    app.run(debug=True)
