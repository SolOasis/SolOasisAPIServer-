import os
import unittest
import tempfile
import json
import base64


class TestApiFunctions(unittest.TestCase):

    def setUp(self):
        self.db_fd, API.app.config['DATABASE'] = tempfile.mkstemp()
        API.app.config['TESTING'] = True
        self.app = API.app.test_client()
        # API.db = SQLAlchemy(API.app)
        self.db = API.db
        self.db.drop_all()
        self.db.create_all()
        self.auth = API.auth
        self.drone_manager = API.drone_manager

    def test_tearDown(self):
        os.close(self.db_fd)
        os.unlink(API.app.config['DATABASE'])

    def test_index(self):
        rv = self.app.get('/')
        self.assertTrue("Index" in rv.data)

    def register(self, usr, pwd):
        tmp = json.dumps({
                            'username': usr,
                            'password': pwd
                         })
        return self.app.post('/users/api/v1.0/users',
                             data=tmp,
                             headers={
                                 'Content-Type': 'application/json'}
                             )

    def getUsers(self):
        return self.app.get('/users/api/v1.0/users').data

    def test_register(self):
        users = self.getUsers()
        self.assertTrue('{}' in users)

        rv = self.register("test", "test")
        self.assertTrue("test" in rv.data)

        rv = self.register("test", "test")
        self.assertTrue("existing user" in rv.data)

        rv = self.register("tes", "")
        self.assertTrue("missing data" in rv.data)

        rv = self.register("", "test")
        self.assertTrue("missing data" in rv.data)

        users = self.getUsers()
        self.assertTrue("0" in users)

    def login(self, usr, pwd, token=False):
        if token:
            creds = pwd
        else:
            creds = 'Basic ' + \
                    base64.b64encode(b'%s:%s' % (usr, pwd)).decode('utf-8')
        return self.app.get('/users/api/v1.0/testlogin',
                            headers={'Authorization': creds}
                            ).data

    def test_testlogin(self):
        usr = 'testlogin'
        pwd = 'tmmi'
        self.register(usr, pwd)
        data = self.login(usr, pwd)
        self.assertTrue('data' in data)

    def getToken(self, usr, pwd):
        creds = base64.b64encode(b'%s:%s' % (usr, pwd)).decode('utf-8')
        return self.app.get('/users/api/v1.0/token',
                            headers={'Authorization': 'Basic ' + creds}
                            ).data

    def test_getToken(self):
        self.register("t", "t").data
        token = self.getToken("t", "t")
        self.assertTrue("token" in token)

    def test_verifyByToken(self):
        usr = 'tmd'
        pwd = 'tmm'
        self.register(usr, pwd)
        token = self.getToken(usr, pwd)
        token = token.split('"')[-2]
        data = self.login(token, "unused")
        self.assertTrue('data' in data)


if __name__ == "__main__":
    from os import path
    import sys
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    sys.path.append('../src')
    import API
    unittest.main()
