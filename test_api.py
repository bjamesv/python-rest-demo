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

class TestUser(TestApi):
    """Test the /user API url path"""
    def test_get(self):
        user_url = '/user'
        expected = {}
        result = self.simulate_get(user_url)
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
        expected = {'message': "Login success!"} #TODO: check for session token
        result = self.simulate_post(auth_url, params = test_params)
        self.assertEqual(result.json, expected)
