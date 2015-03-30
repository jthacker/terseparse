from terseparse import types


def assert_conv_fails(func, val_str, msg=None):
    try:
        func(val_str)
    except types.ArgumentTypeError:
        return
    s = 'Conversion did not fail for value {!r}.'.format(val_str)
    if msg:
        s += ' It should have failed because "{}".'.format(msg)
    raise AssertionError(s)
