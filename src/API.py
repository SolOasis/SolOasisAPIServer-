#!/usr/bin/env python
""" API server of drone manager.

Deal with HTTP requests about drone manger.
"""
##########
# Import #
##########
import os
from Manager import Manager
from flask import Flask, jsonify, request, \
        send_file, render_template, url_for, \
        abort, g
import logging
from flask_cors import cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
# import dbModels
# from werkzeug.security import generate_password_hash  # , check_password_hash

#################
# Initilization #
#################

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# Initilize drone manager
drone_manager = Manager()


class User(db.Model):
    """ User class for access control. """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
        """ Encrypt password. """
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        """ Verify password. """
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        """ Generate token for user. 600 sec only. """
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        """ Verify token.

        Note that invalid token may be expired.
        """
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user


@auth.verify_password
def verify_password(username_or_token, password):
    """ Verify user by its token or password. """
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/users/api/v1.0/register')
def register():
    """ Register page. """
    return render_template('register.html')


"""
@app.route('/users/api/v1.0/login')
def login_view():
    return render_template('login.html')
"""


@app.route('/users/api/v1.0/users', methods=['GET'])
def get_users():
    """ Get all user information.

    Returns:
        dict of (id: {
            username: username
            password: hash password })

    """
    users = User.query.order_by(User.id).all()
    users_dict = dict()
    for i in range(len(users)):
        users_dict[i] = {
                'username': users[i].username,
                'password': users[i].password_hash

                }

    print users_dict
    return jsonify(users_dict)


@app.route('/users/api/v1.0/users', methods=['POST'])
def new_user():
    """ Register new user.

    Args:
        json form with username and password

    Returns:
        status:
            ok with username
            error with error
    """
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        return jsonify(status='error', error='missing data')
    if User.query.filter_by(username=username).first() is not None:
        return jsonify(status='error', error='existing user')
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'status': 'ok', 'username': user.username}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/users/api/v1.0/users/<int:id>')
def get_user(id):
    """ Get given user information. """
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/users/api/v1.0/token')
@auth.login_required
def get_auth_token():
    """ Get token. 600 sec duration.

    Returns:
        token: generated token
        duration: 600 sec
    """

    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/users/api/v1.0/testlogin')
@auth.login_required
def test_login():
    """ Used to tets login_required. """
    return jsonify({'data': 'Hello, %s!' % g.user.username})


"""
@app.errorhandler(400)
def bad_request_handler(error):
    return bad_request(error.message)

def bad_request(message):
    response = jsonify({'message': message})
    response.status_code = 400
    return response
"""


######################
# Authentication API #
######################

@app.route('/')
@app.route('/index', methods=['GET'])
@cross_origin()
def index():
    """ Index of the API server. """
    return render_template('index.html')


#############
# Drone API #
#############


@app.route('/drone/api/v1.0/search', methods=['GET'])
@cross_origin()
@auth.login_required
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


@app.route('/drone/api/v1.0/release', methods=['GET'])
@cross_origin()
@auth.login_required
def releaseAllDevices():
    """ Release all drones. Used when turning off the server. """
    status = drone_manager.releaseAllDevices()
    return jsonify({'status': status,
                    'function': 'searchAllDevices()'})


@app.route('/drone/api/v1.0/connecteddrones', methods=['GET'])
@cross_origin()
def getAllDrones():
    """ Get all connected drones infomations.
    Decrepted.

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
@cross_origin()
def getAllDroneStatus():
    """ Get all drones infos.

    Returns:
        function: function name
        dict of devices: (droneID: droneinfo_dict(id, name, assinged, state))

    """
    result = dict()
    drones = drone_manager.getAllDroneStatus()
    result['drones'] = drones
    result['dronesNum'] = len(drones)
    result['function'] = 'getAllDroneStatus()'
    return jsonify(result)


@app.route('/drone/api/v1.0/assign', methods=['GET'])
@cross_origin()
@auth.login_required
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
@cross_origin()
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
@cross_origin()
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
@cross_origin()
@auth.login_required
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
@cross_origin()
@auth.login_required
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
@cross_origin()
@auth.login_required
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
    db.create_all()
    app.run(debug=True)
