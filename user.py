"""
Module defining an API user datastore and access interface
"""
from tempfile import NamedTemporaryFile
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from passlib.hash import argon2

class UserNotFoundException(RuntimeError):
    """Raised when specified user not found in datastore"""
    pass

def hash_password(user_password):
    """
    utilty function to securely hash user password

    Keyword Parameters:
      user_password  -- (String) plain-text password supplied by user

    >>> initial_hash = hash_password('secret2')
    >>> len(initial_hash) # fixed length
    76
    >>> initial_hash[:16] # spot-check hash header
    '$argon2i$v=19$m='
    """
    # generate new salt and secure pw hash
    return argon2.hash(user_password)

def get_user_hash(datastore, username):
    """
    Returns datastore secure hash for referenced user

    Keyword Parameters:
      datastore  -- (Datastore) object providing user persistance
      username  -- (String) name of the user to retrieve hash for

    >>> ds = Datastore()
    >>> hash = hash_password('secret2')
    >>> with ds.get_session() as s:
    ...     ds.add(s, 'salvador.dali', hash)
    >>> test_hash = get_user_hash(ds, 'salvador.dali')
    >>> test_hash == hash
    True
    >>> get_user_hash(ds, 'florence.nightingale')
    Traceback (most recent call last):
       ...
    user.UserNotFoundException: florence.nightingale
    """
    with datastore.get_session() as session:
        stored_user = datastore.get(session, username)
        if stored_user:
            return stored_user.pw_hash
        raise UserNotFoundException(username)

class Datastore:
    """
    Class encapsulating a User persistance backend

    >>> ds = Datastore()
    >>> with ds.get_session() as s:
    ...     ds.add(s, 'salvador.dali', 'FACECAFE')
    >>> user = None # test fetch
    >>> with ds.get_session() as s:
    ...     user = ds.get(s, 'salvador.dali')
    ...     user.name
    ...     user.pw_hash
    'salvador.dali'
    'FACECAFE'
    """
    Base = declarative_base()

    class User(Base):
        """Define user storage model"""
        __tablename__ = 'user'

        name = Column(String, primary_key=True)
        pw_hash = Column(String)
        data = Column(JSON)

    def __init__(self):
        """Default to an ephemeral SQLite3 backend"""
        # create a tempfile for this instance
        self._db_file = NamedTemporaryFile()
        url = 'sqlite:///{}'.format(self._db_file.name)
        # create db & migrate declarative schema
        self.engine = create_engine(url)
        self.Base.metadata.create_all(self.engine)

        self.SessionFactory = sessionmaker()
        self.SessionFactory.configure(bind=self.engine)

    def __del__(self):
        """Clean up db"""
        self._db_file.close()

    @contextmanager
    def get_session(self):
        """Create a transactional storage-access session"""
        session = self.SessionFactory()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def add(self, session, new_name, new_hash, new_json=None):
        """
        Persist a new User to the datastore

        >>> ds = Datastore()
        >>> with ds.get_session() as s:
        ...     ds.add(s, 'salvador.dali', 'FACECAFE')
        """
        session.add(self.User(name=new_name, pw_hash=new_hash, data=new_json))

    def get(self, session, user_name):
        """
        Retrieve a User from the datastore

        >>> ds = Datastore()
        >>> with ds.get_session() as s:
        ...     ds.get(s, 'UserDoesnt@exist')

        """
        user = session.query(self.User).filter_by(name=user_name).one_or_none()
        return user

