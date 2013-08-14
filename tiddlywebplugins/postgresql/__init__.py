"""
A subclass of tiddlywebplugins.sqlalchemy with postgresql specific
tune ups, including geo searches.

http://github.com/cdent/tiddlywebplugins.postgresql
http://tiddlyweb.com/

"""

from sqlalchemy import event
from sqlalchemy.engine import create_engine
from sqlalchemy.exc import DataError

from tiddlywebplugins.sqlalchemy3 import Store as SQLStore, Base, Session

import logging

#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
#logging.getLogger('sqlalchemy.orm.unitofwork').setLevel(logging.DEBUG)
#logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)

__version__ = '0.1.0'

ENGINE = None
MAPPED = False


LOGGER = logging.getLogger(__name__)


class Store(SQLStore):
    """
    An adaptation of the generic sqlalchemy store, to add mysql
    specific functionality, including search.
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
            #_map_tables(self.environ['tiddlyweb.config'],
            #        Base.metadata.sorted_tables)
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
            raise TypeError('postgres refuses to store tiddler: %s' % exc)


def _map_tables(config, tables):
    """
    Transform the sqlalchemy table information into mysql specific
    table information.

    XXX: This ought to be doable in a more declarative fashion.
    """
    fulltext = config.get('mysql.fulltext', False)
    for table in tables:

        if table.name == 'text' and fulltext:
            table.kwargs['mysql_engine'] = 'MyISAM'
        else:
            table.kwargs['mysql_engine'] = 'InnoDB'

        if table.name == 'revision' or table.name == 'tiddler':
            for column in table.columns:
                if (column.name == 'tiddler_title'
                        or column.name == 'title'):
                    column.type = VARCHAR(length=128, convert_unicode=True)

        if table.name == 'text':
            for column in table.columns:
                if column.name == 'text':
                    column.type = LONGTEXT(convert_unicode=True)

        if table.name == 'tag':
            for column in table.columns:
                if column.name == 'tag':
                    column.type = VARCHAR(length=191, convert_unicode=True)

        if table.name == 'field':
            for index in table.indexes:
                # XXX: is the naming system reliable?
                if index.name == 'ix_field_value':
                    index.kwargs['mysql_length'] = 191
