def test_version():
    import terseparse
    assert hasattr(terseparse, '__version__')
    assert len(terseparse.__version__) > 0
