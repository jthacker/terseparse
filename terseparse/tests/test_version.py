def test_version():
    import terseparse
    assert hasattr(terseparse, '__version__')
    assert len(terseparse.__version__) > 0
    assert terseparse.__version__ == '1.1.1'

