"""
Module defining user session utility functions
"""
import logging

from beaker.middleware import SessionMiddleware
import sqlalchemy

def create_login_session(username, request):
    """
    Establishes a Beaker session for the referenced user

    Keyword Parameters:
    username  -- String, identifying user
    request  -- Falcon HTTP request object representing current API call

    >>> from unittest.mock import Mock
    >>> fake_req = Mock()
    >>> fake_req.env = {'beaker.session': {}}
    >>> # Check login
    >>> create_login_session('pat.ng', fake_req)
    >>> fake_req.env
    {'beaker.session': {'name': 'pat.ng'}}
    """
    session = request.env['beaker.session']
    session['name'] = username

def get_user_name(request):
    """
    Returns string representing username for current API session user

    None is returned for anonymous/unauthenticated sessions

    Keyword Parameters:
    request  -- Falcon HTTP request object representing current API call
    """
    # obtain logged in API username (if available)
    session_user_name = None #default
    if 'beaker.session' in request.env:
        try:
            session_user_name = request.env['beaker.session'].get('name')
        except KeyError:
            pass # return default
    return session_user_name

def wrap_app_with_session_middleware(wsgi_app):
    """
    Install Middleware for session establishment around referenced app

    Keyword Parameters:
      wsgi_app  -- WSGI application to add middleware to & return
    """
    cache_filename = 'beaker.sqlite3'
    session_cache_url = 'sqlite:///{}'.format(cache_filename)
    
    max_session_days = 1 # Cookie invalid after 24h

    session_opts = {
        'session.cookie_expires': max_session_days*24*3600,
        'session.auto': True, # Automatically save session
        'session.key': 'api.session.id',
        'session.type': 'ext:database',# ext:redis may be viable migration path
        'session.url': session_cache_url,
    }

    # attempt to clean up old/expired sessions
    cleanup_sql = "DELETE FROM beaker_cache WHERE accessed < datetime('now', :modifier)"
    delete_older_than_modifier = '-{} days'.format(max_session_days)
    logger = logging.getLogger(wrap_app_with_session_middleware.__name__)
    try:
        engine = sqlalchemy.create_engine(session_cache_url)
        engine.execute(cleanup_sql, [delete_older_than_modifier])
    except Exception as e:
        # dont worry, cleanup will be retried if WSGI app launches again
        logger.error(e)
        # ignore error & continue

    # install the session middleware
    return SessionMiddleware(wsgi_app, session_opts)
