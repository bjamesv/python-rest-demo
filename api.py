# Module defining simple REST API for user signup & data retrieval

import falcon

from user import Datastore

user_storage = Datastore()

class BaseResource:
    """Falcon resource to handle requests with no URL path"""
    def on_get(self, req, resp):
        """Handle GET requests"""
        json_body = ["Hello World"] #default
        #TODO: if session exists, return username+user JSON data
        resp.media = json_body

class UserResource:
    def on_post(self, req, resp):
        """Handle POST requests for user creation

        HTTP POST parameters:
          username  -- New user to create (Required)
          password  -- New user's password (Required)
          data  -- JSON text containing user data (Optional)
        """
        username_post_field, password_post_field = 'username', 'password'
        data_post_field = 'data'
        try:
            request_username = req.params[username_post_field]
        except KeyError:
            raise falcon.HTTPMissingParam(username_post_field)
        try:
            request_password = req.params[password_post_field]
        except KeyError:
            raise falcon.HTTPMissingParam(password_post_field)
        new_data = None #optional
        if data_post_field in req.params:
            new_data = req.params[data_post_field]
        new_hash = 'NOTAHASH' #TODO: implement hashing of user password
        with user_storage.get_session() as session:
            user_storage.add(session,
                             new_name = request_username,
                             new_hash = new_hash,
                             new_json = new_data)
        msg = 'Successfully signed up new user: {}'.format(request_username)
        resp.media = {'message': msg}

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
api.req_options.auto_parse_form_urlencoded = True # parse POST request bodies

api.add_route('/', BaseResource())
api.add_route('/user', UserResource())
api.add_route('/user/{username}', UserResource())
#TODO: add auth routes
