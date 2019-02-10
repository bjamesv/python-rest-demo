# Module defining simple REST API for user signup & data retrieval

import falcon

class BaseResource:
    """Falcon resource to handle requests with no URL path"""
    def on_get(self, req, resp):
        """Handle GET requests"""
        json_body = ["Hello World"] #default
        #TODO: if session exists, return username+user JSON data
        resp.media = json_body

class UserResource:
    def on_post(self, req, resp, username=None):
        """Handle POST requests for user creation"""
        pass

    def on_get(self, req, resp, username=None):
        """Handle GET requests for user data"""
        user_data = {} #TODO: implement
        resp.media = user_data

    def on_put(self, req, resp, username=None):
        """Handle PUT requests for user data update"""
        pass

    def on_delete(self, req, resp, username=None):
        """Handle DELETE requests to remove user"""
        pass

class AuthResource:
    pass #TODO: implement

api = falcon.API()
api.add_route('/', BaseResource())
api.add_route('/user', UserResource())
api.add_route('/user/{username}', UserResource())
#TODO: add auth routes
