"""
Module defining an API user datastore and access interface
"""
from tempfile import NamedTemporaryFile
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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

