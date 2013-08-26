"""
A subclass of tiddlywebplugins.sqlalchemy with postgresql specific
tune ups.

http://github.com/cdent/tiddlywebplugins.postgresql
http://tiddlyweb.com/
http://tiddlyweb-sql.tiddlyspace.com

You will need to create a database:

    createdb tiddlyweb

Add the following to `tiddlywebconfig.py`:

    'server_store': ['tiddlywebplugins.postgresql', {
        'db_config': 'postgresql+psycopg2:///tiddlyweb'}],
    'indexer': 'tiddlywebplugins.postgresql', # optional

See http://tiddlyweb-sql.tiddlyspace.com/ for additional documentation
and assistance.
"""

from sqlalchemy.engine import create_engine
from sqlalchemy.exc import DataError

from tiddlywebplugins.sqlalchemy3 import (Store as SQLStore, Base, Session,
        index_query)

import logging

#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
#logging.getLogger('sqlalchemy.orm.unitofwork').setLevel(logging.DEBUG)
#logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)

__version__ = '0.1.2'

ENGINE = None
MAPPED = False


LOGGER = logging.getLogger(__name__)


class Store(SQLStore):
    """
    An adaptation of the generic sqlalchemy store, to work well
    with postgresql.
    """

    def __init__(self, store_config=None, environ=None):
        super(Store, self).__init__(store_config, environ)

    def _init_store(self):
        """
        Establish the database engine and session,
        creating tables if needed.
        """
        global ENGINE, MAPPED
        if not ENGINE:
            ENGINE = create_engine(self._db_config())
            Base.metadata.bind = ENGINE
            Session.configure(bind=ENGINE)
        self.session = Session()

        if not MAPPED:
            Base.metadata.create_all(ENGINE)
            MAPPED = True

    def tiddler_put(self, tiddler):
        """
        Override the super to trap a DataError when title or other
        attribute is too long.
        """
        try:
            SQLStore.tiddler_put(self, tiddler)
        except DataError, exc:
            raise TypeError('postgresql refuses to store tiddler: %s' % exc)
