# Module defining simple REST API for user signup & data retrieval

import falcon

import user, auth, session

user_storage = user.Datastore()

class BaseResource:
    """Falcon resource to handle requests with no URL path"""
    def on_get(self, req, resp):
        """Handle GET requests"""
        json_body = ["Hello World"] #default
        login_user = session.get_user_name(req) #check login
        if login_user:
            json_body = user.get_user_data(user_storage, login_user)
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
            # Falcon has special handling of commas in post data,
            # our JSON text may be split on any commas into list of str
            falcon_data = req.params[data_post_field]
            new_data = falcon_data # default, assume text is unmangled
            if isinstance(falcon_data, list): #text was munged
                new_data = ','.join(falcon_data)#merge strings & add commas back in
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
        """
        Handle PUT requests for user data update

        The entire HTTP PUT body will is treated as the new JSON data
        value.
        """
        session_user = session.get_user_name(req)
        if not session_user:
            raise falcon.HTTPUnauthorized(title='Login required')
        if session_user != username:
            raise falcon.HTTPUnauthorized(title='Permission denied')

        # update data
        new_data = req.media
        user.update_user_data(user_storage, username, new_data)

    def on_delete(self, req, resp, username=None):
        """Handle DELETE requests to remove user"""
        session_user = session.get_user_name(req)
        if not session_user:
            raise falcon.HTTPUnauthorized(title='Login required')
        if session_user != username:
            raise falcon.HTTPUnauthorized(title='Permission denied')

        # delete user
        user.delete_user(user_storage, username)
        # and revoke user's session token
        session.invalidate_session(req)

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
