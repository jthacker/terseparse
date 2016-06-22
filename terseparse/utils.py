from itertools import chain


class ClassPropertyDescriptor(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()


def classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)
    return ClassPropertyDescriptor(func)


def rep(obj, *attrs, **kwargs):
    """Create a repr of a property based class quickly
    Args:
        obj      -- instance of class
        *attrs   -- list of attrs to add to the representation
        **kwargs -- Extra arguments to add that are not captured as attributes

    Returns: A string representing the class
    """
    s = obj.__class__.__name__
    args = chain(((attr, getattr(obj, attr)) for attr in attrs), kwargs.items())
    s += '(%s)' % ','.join('{}={!r}'.format(k, v) for k, v in args)
    return s
