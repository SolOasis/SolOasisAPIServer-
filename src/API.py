#!/usr/bin/env python
""" API server of drone manager.

Deal with HTTP requests about drone manger.
Build socket for client to get all drones' info.
"""
##########
# Import #
##########
import os
from Manager import Manager
from flask import Flask, jsonify, request, \
        render_template, url_for, \
        abort, g
from flask_cors import cross_origin, CORS
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
# import dbModels
# from werkzeug.security import generate_password_hash  # , check_password_hash

SOCKET_SEND_PERIOD = 0.3
#################
# Initilization #
#################

app = Flask(__name__)
CORS(app)
# logging.basicConfig(level=logging.INFO)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

app.static_folder = 'static'


db = SQLAlchemy(app)
auth = HTTPBasicAuth()
soloasis_manager = Manager()


##############
# User class #
##############


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
        """ Generate token for user. Have expriation time in sec. """
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


###################
# User access API #
###################


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
def register_page():
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
    if username is None or password is None \
            or username == "" or password == "":
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


#########
# Index #
#########


@app.route('/')
@app.route('/index', methods=['GET'])
@cross_origin()
def index():
    """ Index of the API server. """
    return render_template('index.html')


################
# SolOasis API #
################


@app.route('/SolOasis/api/v1.0/stations', methods=['GET'])
@cross_origin()
def getAllStationInfo():
    """ Get all SolOasis station infos.

    Used for staff admin page.

    Returns:
        function: function name
        info: dict of all station info

    """
    result = dict()
    info = soloasis_manager.getAllInfo()
    result['info'] = info
    result['function'] = 'getAllInfo()'
    return jsonify(result)


@app.route('/SolOasis/api/v1.0/battery/<ID>', methods=['GET'])
@cross_origin()
def getBattery(ID):
    """ Get battery percentage of the SolOasis charging station.

    Args:
        ID: station ID.

    Returns:
        function: function name
        StationID: station ID.
        battery: battery in percentage of the station.

    """
    battery = soloasis_manager.getStationBattery(ID)
    return jsonify({'StationID': ID,
                    'function': 'getStationBattery()',
                    'battery': battery})


@app.route('/SolOasis/api/v1.0/update/', methods=['POST'])
@cross_origin()
def update():
    """ Update data of a station.
    Args:
        json form of diagnostic data
    Returns:
        status:
            ok with username
            error with error
    """

    result = request.get_json()
    print (result)
    try:
        ID = request.get_json()['ID']
    except:
        return (jsonify({'status': 'error: cannot get this ID',
                         'function': 'update()'}))

    print (request)
    print (request.form)
    print (request.json)
    ID = 0;
    data = request.get_json()['data']
    if not soloasis_manager.update(ID, data):
        return (jsonify({'status': 'error: cannot update',
                         'function': 'update()'}))

    return (jsonify({'function': 'update()',
                     'status': 'ok',
                     'stationID': ID}))


if __name__ == "__main__":
    #db.create_all()
    app.run(debug=True, threaded=True)
