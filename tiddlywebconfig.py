import mangler
config = {
    'log_level': 'DEBUG',
    'server_store': ['tiddlywebplugins.postgresql', {
        'db_config': 'postgresql+psycopg2:///tiddlyweb'}],
    'indexer': 'tiddlywebplugins.postgresql',
}
