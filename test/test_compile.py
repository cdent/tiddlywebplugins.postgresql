


def test_compile():
    try:
        import tiddlywebplugins.postgresql
        assert True
    except ImportError, exc:
        assert False, exc
