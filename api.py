# Module defining simple REST API for user signup & data retrieval

import falcon

import user, auth, session

user_storage = user.Datastore()

class BaseResource:
    """Falcon resource to handle requests with no URL path"""
    def on_get(self, req, resp):
        """Handle GET requests"""
        json_body = ["Hello World"] #default
        if session.get_user_name(req):
            json_body = {'username': session.get_user_name(req)}
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
        # securely hash user password & attempt to add new user
        new_hash = user.hash_password(request_password)
        with user_storage.get_session() as storage_session:
            user_storage.add(storage_session,
                             new_name = request_username,
                             new_hash = new_hash,
                             new_json = new_data)
        msg = 'Successfully signed up new user: {}'.format(request_username)
        resp.media = {'message': msg}

    def on_get(self, req, resp, username=None):
        """Handle GET requests for user data"""
        session_user = session.get_user_name(req)
        if not session_user:
            raise falcon.HTTPUnauthorized(title='Login required')
        if session_user != username:
            raise falcon.HTTPUnauthorized(title='Permission denied')

        # fetch data
        user_data = user.get_user_data(user_storage, username)
        resp.media = user_data

    def on_put(self, req, resp, username=None):
        """Handle PUT requests for user data update"""
        pass

    def on_delete(self, req, resp, username=None):
        """Handle DELETE requests to remove user"""
        pass

class AuthResource:
    """Falcon Resource to handle authentication requests"""
    def on_post(self, req, resp):
        """Handle user login POST requests.

        Returns an authenticated API session token

        HTTP POST parameters:
          username  -- New user to create (Required)
          password  -- New user's password (Required)
        """
        username_post_field, password_post_field = 'username', 'password'
        try:
            request_username = req.params[username_post_field]
        except KeyError:
            raise falcon.HTTPMissingParam(username_post_field)
        try:
            request_password = req.params[password_post_field]
        except KeyError:
            raise falcon.HTTPMissingParam(password_post_field)
        stored_hash = user.get_user_hash(user_storage, request_username)
        if auth.check_password(request_password, stored_hash):
            # log in user
            session.create_login_session(request_username, req)
            resp.media = {'message': 'Login success!'}
            return
        raise falcon.HTTPUnauthorized(title='Login incorrect')

    def on_delete(self, req, resp):
        """Handle user logout DELETE requests"""
        session.invalidate_session(req)

api = falcon.API()
api.req_options.auto_parse_form_urlencoded = True # parse POST request bodies

api.add_route('/', BaseResource())
api.add_route('/user', UserResource())
api.add_route('/user/{username}', UserResource())
api.add_route('/auth', AuthResource())

# add WSGI middleware
api = session.wrap_app_with_session_middleware(api) # add web sessions
