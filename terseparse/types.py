"""Namespace for all type objects"""
import re
import logging
import os
from argparse import ArgumentTypeError

from terseparse.utils import classproperty, rep


log = logging.getLogger('terseparse.types')

# Lists of items are separated by commas, semi-colons and/or whitespace
list_regex = re.compile(r'[^,;\s]+')


class Type(object):
    """ABC for type objects.
    Types are callable, taking a string and converting it
    to their given type. The call method should have no side effects.
    """

    def __call__(self, val):
        return self.convert(val)

    def __str__(self):
        """Implement this method to show a simple representation of the class"""
        return self.name

    def __or__(self, obj):
        if isinstance(obj, str):
            obj = Keyword(obj)
        return Or(self, obj)

    def fail(self, val_str, message):
        msg = "{!r} is an invalid <{}>. {}".format(val_str, self.name, message)
        raise ArgumentTypeError(msg)


class GreedyType(Type):
    """Mixin to indicate that a type will greedily consume arguments."""


class Keyword(Type):
    """A Keyword maps a string to a static value"""

    def __init__(self, name, *value):
        """Initialize Keywords
        Args:
            name  -- keyword name
            value -- Optional value, otherwise name is used

        value is setup as *value to detect if the parameter is supplied, while
        still supporting None. If no value is supplied then name should be used.
        If any value is supplied (even None), then that value is used instead
        """
        self.name = name
        self.key = name
        self.value = name if len(value) != 1 else value[0]
        self.description = "Matches {!r} and maps it to {!r}".format(name, self.value)

    def convert(self, val):
        if val == self.key:
            return self.value
        self.fail(val, "Must be {!r}".format(self.key))

    def __repr__(self):
        return rep(self, 'name', 'value')


class Str(Type):
    """Convert string to string
    Use this instad of str, to get a clean type name
    """
    def __init__(self):
        self.name = 'str'

    def convert(self, val):
        return str(val)

    def __repr__(self):
        return rep(self, 'name')


class Bool(Type):
    """Convert string to bool"""
    def __init__(self):
        self.name = 'bool'
        self.true_vals = ('true', 't', '1', 'yes')

    def __init__(self, val):
        return val.lower() in self.true_vals

    def __repr__(self):
        return rep(self, 'name')


class Set(Type):
    """A Set is a comma separated list of unique values that satisfy the specified type.
    >>> s = Set(Int())
    Set(Int(minval=None, maxval=None))
    >>> s('1,2,3,4')
    {1,2,3,4}
    >>> s('1,1,1,1')
    {1}
    """

    def __init__(self, typ):
        self.name = 'set(<{}>)'.format(typ)
        self.description = 'A set is a comma separated list of unique values ' \
                'of type <{}>.'.format(typ.name)
        self.typ = typ

    def convert(self, val):
        seq = set()
        for k in list_regex.findall(val):
            try:
                seq.add(self.typ(k))
            except ArgumentTypeError as e:
                self.fail(val, self.description + '\n' + str(e))
        return seq

    def __repr__(self):
        return rep(self, 'typ')


class List(Type):
    """A List is a comma separated list of values that satisfy the specified type
    >>> l = List(Int())
    List(Int(minval=None, maxval=None))
    >>> l('1,2,3,4')
    [1,2,3,4]
    >>> l('1,1,1,1')
    [1,1,1,1]
    """

    def __init__(self, typ):
        self.name = 'list(<{}>)'.format(typ)
        self.description = 'A list is a comma separated list of values of type <{}>.' \
                .format(typ)
        self.typ = typ

    def convert(self, val):
        seq = list()
        for k in list_regex.findall(val):
            try:
                seq.append(self.typ(k))
            except ArgumentTypeError as e:
                self.fail(val, self.description + '\n' + str(e))
        return seq

    def __repr__(self):
        return rep(self, 'typ')


class Dict(Type):
    """Converts a string to a dictionary
    Support a comma, semi-colon or space separated list of key value pairs.
    Key-value pairs can be separated by either a colon or and equals sign.

    The following will all parse to {'a': 'b', 'c': 'd'}
    >>> d = Dict({'a': Str, 'c': Str})
    >>> d('a:b c:d')
    {'a': 'b', 'c': 'd'}
    >>> d('a=b,c=d')
    {'a': 'b', 'c': 'd'}
    >>> d('a:b, c=d')
    {'a': 'b', 'c': 'd'}
    >>> d('a=b,,,c=d')
    {'a': 'b', 'c': 'd'}

    If no value is given, then it is passed to the validator as the empty string (ie '')
    >>> Dict({'a': Int() | Keyword('', None)})('a')
    {'a': None}

    Keys can be specified multiple times, the latest (farthest to right) key's
    value will overwrite previous values.
    """
    def __init__(self, validator_map):
        """Create a dictonary type from a dictionary of other types
        Args:
            validator_map -- a mapping from names to types
        Examples:
        >>> Dict({'a': int, 'b': int})('a:1,b:2')
        {'a': 1, 'b': 2}

        >>> Dict({'a': str, 'b': int})('a:asdf b=1234')
        {'a': 'asdf', 'b': 1234}

        >>> Dict({'a': Int() | Keyword('', None), 'b': Int()})('a,b=1')
        {'a': None, 'b': 1}
        """
        self.validators = dict(validator_map)
        v_sorted = sorted(self.validators.items(), key=lambda t: t[0])
        self.validator_descriptions = ['{}:<{}>'.format(k, v) for k, v in v_sorted]
        self.name = 'dict({})'.format(', '.join(self.validator_descriptions))
        self.description = '\nDict options: \n  '
        self.description += '\n  '.join(self.validator_descriptions)
        self.kv_regex = re.compile(r'[=:]+')

    def keys_to_set_type(self):
        kws = tuple(Keyword(k) for k in self.validators)
        return Set(Or(*kws))

    def convert(self, val):
        try:
            return self._convert(val)
        except (AssertionError, ValueError):
            self.fail(val, self.description)
        except ArgumentTypeError as e:
            self.fail(val, self.description + '\n' + str(e))

    def _convert(self, val):
        obj = {}
        for pair in list_regex.findall(val):
            pair = self.kv_regex.split(pair)
            if len(pair) == 1:
                k, v = pair[0], ''
            else:
                k, v = pair
            assert k in self.validators
            val = self.validators[k](v)
            if k in obj:
                log.warn('key: {!r} overwritten '
                         'new: {!r} old: {!r}'.format(k, val, obj[k]))
            obj[k] = val
        return obj

    def __iter__(self):
        return self.validators.items()

    def __repr__(self):
        return rep(self, validator_map=self.validators)


MODE_STRS = {
    'r': 'readable',
    'w': 'writable',
    'r+': 'readable and writeable'}


class File(Type):
    @classproperty
    def r(cls):
        return cls('r')

    @classproperty
    def rw(cls):
        return cls('r+')

    @classproperty
    def w(cls):
        return cls('w')

    def __init__(self, mode):
        self.name = 'file'
        self.mode = mode
        self.mode_str = MODE_STRS[mode]
        self.description = 'file({})'.format(mode)

    def convert(self, val):
        try:
            with open(val, self.mode):
                return val
        except IOError:
            self.fail(val, 'Must be a {} file'.format(self.mode_str))

    def __repr__(self):
        return rep(self, 'mode')


DIR_MODES = {
    'r': os.R_OK,
    'w': os.W_OK,
    'rw': os.R_OK | os.W_OK
}


class Dir(File):
    def __init__(self, mode):
        self.name = 'dir'
        self.mode = DIR_MODES[mode]
        self.mode_str = MODE_STRS[mode]
        self.description = 'dir({})'.format(mode)

    def convert(self, val):
        if not os.access(val, self.mode):
            self.fail(val, 'Must be a {} directory'.format(self.mode_str))
        return val

    def __repr__(self):
        return rep(self, 'mode')


class Int(Type):
    """Int: Integer parseing class that supports range restrictions
    Supports automatic parsing of base 10 and 16 characters
    >>> Int()('0xFF')
    255
    >>> Int()('1234')
    1234
    >>> Int()('01234')
    1234
    """
    @classproperty
    def u8(cls):
        obj = cls(0, 2**8)
        obj.name = 'u8'
        obj.description = 'unsigned 8-bit integer'
        return obj

    @classproperty
    def u16(cls):
        obj = cls(0, 2**16)
        obj.name = 'u16'
        obj.description = 'unsigned 16-bit integer'
        return obj

    @classproperty
    def u32(cls):
        obj = cls(0, 2**32)
        obj.name = 'u32'
        obj.description = 'unsigned 32-bit integer'
        return obj

    @classproperty
    def positive(cls):
        return cls(0)

    @classproperty
    def negative(cls):
        return cls(None, 0)

    def __init__(self, minval=None, maxval=None):
        """Create an Integer that satisfies the requirements minval <= val < maxval
        """
        self.name = 'int'
        self.minval = minval
        self.maxval = maxval
        domain = ''
        if minval is not None and maxval is not None:
            domain = '{} <= val < {}'.format(minval, maxval)
        elif minval is not None:
            domain = '{} <= val'.format(minval)
        elif maxval is not None:
            domain = 'val < {}'.format(maxval)
        self.description = 'int({})'.format(domain) if domain else 'int'
        self.error_message = 'Value must satisfy: {}'.format(domain) if domain else ''

    def convert(self, val_str):
        try:
            val = self._convert(val_str)
        except (ValueError, AssertionError):
            self.fail(val_str, self.error_message)
        if (self.minval is not None and val < self.minval) or (
                self.maxval is not None and val >= self.maxval):
            self.fail(val_str, self.error_message)
        return val

    def _convert(self, val):
        # Not using int(val, 0) because that parses '011' to 9 (in octal), which
        # is a bit misleading if you aren't use to the convention.
        try:
            return int(val, 10)
        except ValueError:
            # have to check for '0x' otherwise 'abcd' would parse to 4391, which
            # on first glance does not appear to be a number
            assert '0x' in val.lower()
            return int(val, 16)

    def __repr__(self):
        return rep(self, 'minval', 'maxval')


class Or(Type):
    """Combine types in a shortcircuit fashion.
    The first type to match wins.
    If an Or is one of the types then its nested types are flattened.
    Automatically convert string to Keywords
    """
    def __init__(self, *types):
        _types = []
        for typ in types:
            if isinstance(typ, Or):
                _types.extend(typ.types)
            else:
                if isinstance(typ, str):
                    typ = Keyword(typ)
                _types.append(typ)

        self.name = '|'.join(map(str, _types))
        self.description = ' or '.join(t.description for t in _types)
        self.types = _types

    def convert(self, val):
        for t in self.types:
            try:
                return t(val)
            except ArgumentTypeError:
                pass
        self.fail(val, 'Must be {}'.format(self.description))

    def __repr__(self):
        return rep(self, 'types')
