"""
Module defining integration tests for the simple REST API
"""

from falcon import testing

import api, user

class TestApi(testing.TestCase):
    """
    Base class to simulate Falcon API requests

    per: https://falcon.readthedocs.io/en/stable/api/testing.html
    """
    def setUp(self):
        super(TestApi, self).setUp()
        # reset the user storage
        api.user_storage = user.Datastore()
        self.app = api.api

class TestBase(TestApi):
    """Test the base API url (e.g.: "/")"""
    def test_get(self):
        base_url = '/'
        expected = ['Hello World']
        result = self.simulate_get(base_url)
        self.assertEqual(result.json, expected)

    def test_get_authenticated(self):
        base_url = '/'
        # sign up a user
        user_url = '/user'
        test_params = {'username': 'cruz.bustamante', 'password': 'secret', 'data': '{"cb":"special data"}'}
        result = self.simulate_post(user_url, params = test_params)
        self.assertEqual(result.status_code, 200) # OK
        # log in
        auth_url = '/auth'
        result = self.simulate_post(auth_url, params = test_params)
        session_token, expire_info = result.headers['set-cookie'].lstrip().split(';', 1)
        # check base URL
        expected = {'data': {'cb': 'special data'}, 'username': 'cruz.bustamante'}
        result = self.simulate_get(base_url, headers={'Cookie': session_token})
        self.assertEqual(result.json, expected)

class TestUser(TestApi):
    """Test the /user API url path"""
    def test_get(self):
        user_url = '/user/salvador.dali'
        # no login session
        expected = {'title': 'Login required'} # no data
        result = self.simulate_get(user_url)
        self.assertEqual(result.json, expected)

        # sign up a user
        signup_url = '/user'
        test_params = {'username': 'salvador.dali', 'password': 'secret1'}
        result = self.simulate_post(signup_url, params = test_params)
        self.assertEqual(result.status_code, 200) # OK
        # log in
        auth_url = '/auth'
        result = self.simulate_post(auth_url, params = test_params)
        session_token, expire_info = result.headers['set-cookie'].lstrip().split(';', 1)

        # get data, with session token
        expected = {'data': None, 'username': 'salvador.dali'}
        result = self.simulate_get(user_url, headers={'Cookie': session_token})
        self.assertEqual(result.json, expected)

    def test_post(self):
        """test user sign-up"""
        user_url = '/user'
        expected = {'message': "Successfully signed up new user: cruzbustamante"}
        test_params = {'username': 'cruzbustamante', 'password': 'secret'}
        result = self.simulate_post(user_url, params = test_params)
        self.assertEqual(result.json, expected)
        # test for reject of double-registration
        with self.assertRaises(Exception):
            double_result = self.simulate_post(user_url, params = test_params)

        # test optional JSON sign up data (with comma characters in it)
        signup_url = '/user' # sign up a user
        test_json = '{"address":"1 Microsoft Way", "phone":"1-555-555-5555"}'
        test_params = {'username': 'salvador.dali', 'password': 'secret1', 'data': test_json}
        result = self.simulate_post(signup_url, params = test_params)
        self.assertEqual(result.status_code, 200) # OK
        # log in
        auth_url = '/auth'
        result = self.simulate_post(auth_url, params = test_params)
        session_token, expire_info = result.headers['set-cookie'].lstrip().split(';', 1)

        # get data, with session token
        user_url = '/user/salvador.dali'
        expected = {'data': {'address': '1 Microsoft Way', 'phone': '1-555-555-5555'},
                    'username': 'salvador.dali'} #data should be dict, not array of str
        result = self.simulate_get(user_url, headers={'Cookie': session_token})
        self.assertEqual(result.json, expected)

    def test_put(self):
        user_url = '/user/pat.ng'
        # no login session
        expected = {'title': 'Login required'} # no data
        result = self.simulate_put(user_url)
        self.assertEqual(result.json, expected)

        # sign up a user
        signup_url = '/user'
        test_params = {'username': 'pat.ng', 'password': 'greatpass'}
        result = self.simulate_post(signup_url, params = test_params)
        self.assertEqual(result.status_code, 200) # OK
        # log in
        auth_url = '/auth'
        result = self.simulate_post(auth_url, params = test_params)
        session_token, expire_info = result.headers['set-cookie'].lstrip().split(';', 1)

        # update data, with session token
        new_data = '{"address": "21 Jump St.",' \
                   +'"email": "pat@ng.fake",' \
                   +'"phone": "1-555-555-5555"}'
        result = self.simulate_put(user_url,
                                   body = new_data,
                                   headers = {'Cookie': session_token})
        self.assertEqual(result.status_code, 200) # OK
        # check data
        expected = {'data': {'address': '21 Jump St.',
                             'email': 'pat@ng.fake',
                             'phone': '1-555-555-5555'},
                    'username': 'pat.ng'}
        result = self.simulate_get(user_url, headers={'Cookie': session_token})
        self.assertEqual(result.json, expected)

    def test_delete(self):
        user_url = '/user/d-admin'
        # no login session
        expected = {'title': 'Login required'} # no data
        result = self.simulate_delete(user_url)
        self.assertEqual(result.json, expected)

        # sign up a user
        signup_url = '/user'
        test_params = {'username': 'd-admin', 'password': 'too)short'}
        result = self.simulate_post(signup_url, params = test_params)
        self.assertEqual(result.status_code, 200) # OK
        # log in
        auth_url = '/auth'
        result = self.simulate_post(auth_url, params = test_params)
        session_token, expire_info = result.headers['set-cookie'].lstrip().split(';', 1)

        # delete user
        result = self.simulate_delete(user_url,
                                      headers = {'Cookie': session_token})
        self.assertEqual(result.status_code, 200) # OK
        # check for user data
        base_url = '/'
        expected = ['Hello World'] # no data
        result = self.simulate_get(base_url, headers={'Cookie': session_token})
        self.assertEqual(result.json, expected)

        # test user recreation (should succeed, now)
        result = self.simulate_post(signup_url, params = test_params)
        self.assertEqual(result.status_code, 200) # OK

class TestAuth(TestApi):
    def test_post(self):
        """test authentication"""
        auth_url = '/auth'
        test_params = {'username': 'cruzbustamante', 'password': 'secret'}
        # no user exists yet
        with self.assertRaises(user.UserNotFoundException):
            result = self.simulate_post(auth_url, params = test_params)
        # now sign up a user
        user_url = '/user'
        result = self.simulate_post(user_url, params = test_params)
        # test again
        expected_header = 'set-cookie' # check for session token
        result = self.simulate_post(auth_url, params = test_params)
        self.assertIn(expected_header, result.headers)
        result_token_key_value_pair = result.headers['set-cookie']
        expected_token_prefix = ' api.session.id='
        self.assertEqual(result_token_key_value_pair[:16], expected_token_prefix)

    def test_delete(self):
        """test logout"""
        auth_url = '/auth'

        # sign up a user
        user_url = '/user'
        test_params = {'username': 'cruz.bustamante', 'password': 'secret'}
        result = self.simulate_post(user_url, params = test_params)
        self.assertEqual(result.status_code, 200) # OK
        # log in
        auth_url = '/auth'
        result = self.simulate_post(auth_url, params = test_params)
        session_token, expire_info = result.headers['set-cookie'].lstrip().split(';', 1)
        # confirm session token's valid
        base_url = '/'
        expected = {'data': None, 'username': 'cruz.bustamante'}
        result = self.simulate_get(base_url, headers={'Cookie': session_token})
        self.assertEqual(result.json, expected)

        # logout
        result = self.simulate_delete(auth_url, headers={'Cookie': session_token})
        self.assertEqual(result.status_code, 200) # OK

        # confirm session token is no longer valid
        expected = ['Hello World'] # no user session data
        result = self.simulate_get(base_url, headers={'Cookie': session_token})
        self.assertEqual(result.json, expected)
