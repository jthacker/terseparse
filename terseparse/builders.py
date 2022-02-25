"""Terse command-line parser wrapper around ArgumentParser

Example Usage:
    # First example is the equivalent version of an example from the
    # argparse docs
    p = Parser(
    'cmd', 'Process some integers',
    Arg('integers', 'an integer for the accumulator',
        metavar='N', type=int, nargs='+'),
    Arg('--sum', 'sum the integers (default: find the max)',
        dest='accumulate', action='store_const',
        const=sum, default=max))
    args = p.parse_args('1 2 3 4'.split())

Changes from argparse are as follows:
    * All arguments and parsers require documentation strings
    * A composable syntax for constructing parsers
    * Some default types are provided with user friendly error messages
    * Metavars are created automatically and provide type information
    * SubParser names and descriptions are displayed in help
    * SubParsers support common arguments. Arguments in SubParsers are added
    to all parsers within the SubParsers instance.
    * Debugging information can be enabled with '--terseparse-debug' as first argument
"""

from argparse import SUPPRESS
import six

import sys
import warnings

from terseparse.root_parser import RootParser


class KW(object):
    """Holds keyword arguments for Parser objects.
    Due to the composable style for building parsers and the requirement of
    language that positional arguments are not allowed after keyword arguments,
    this class is used to pass keyword arguments to parsers.

    >>> parser = Parser('name', 'description', KW(epilog='epilog'))
    """
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, parser):
        return parser


class AbstractParser(object):
    """ABC for Parser objects.
    Parser objects can hold Arg and SubParsers.
    Do not update any instance local state outside of init.
    """
    def __init__(self, name, description, *args):
        self._name = name
        self._description = description
        self._args = []
        self._kwargs = {}
        for arg in args:
            if isinstance(arg, KW):
                self._kwargs.update(arg.kwargs)
            else:
                self._args.append(arg)
        self._kwargs['description'] = description
        self.epilog = self._kwargs.pop('epilog', '')
        self._init()

    def _init(self):
        """Subclass init method"""
        pass

    def __call__(self, parser, **kwargs):
        return self._build(parser, self._updated_kwargs(kwargs))

    def _updated_kwargs(self, kwargs):
        return dict(list(self._kwargs.items()) + list(kwargs.items()))

    def _build(self, **kwargs):
        raise NotImplemented()

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def args(self):
        return iter(self._args)


class Parser(AbstractParser):
    def _init(self):
        self._subparser = None
        for arg in self.args:
            if isinstance(arg, SubParsers):
                assert self._subparser is None, (
                        'Only one SubParsers can be added '
                        '(argparse only allows one subparser)')
                self._subparser = arg

    def _build(self, parser, kwargs):
        p = parser.add_parser(self.name, **kwargs)
        for arg in self.args:
            arg(p)
        return p

    @property
    def subparser(self):
        return self._subparser

    def subparsers_summary(self, spacing=2):
        if not self.subparser or not self.subparser.parsers:
            return ''
        parsers = self.subparser.parsers
        name_width = max(len(p.name) for p in parsers) + spacing
        args = ' '.join('{}'.format(a.name) for a in self.subparser.args)

        msg = ''
        spacer = ' ' * spacing
        if parsers:
            msg =  'commands: {}\n'.format(self.subparser.description)
            msg += spacer + 'usage: {} {{{}}} {} ...\n\n'.format(
                    self.name, self.subparser.name, args)
        for p in parsers:
            msg += '{}{:{}} {}\n'.format(
                spacer,
                p.name, name_width,
                p.description)
        return msg

    def parse_args(self, args=None, namespace=None, defaults=None):
        """Parse args, returns a tuple of a parser and ParsedArgs object
        Args:
            args      -- sequence of strings representing the arguments to parse
            namespace -- object to use for holding arguments
            defaults  -- lazily loaded dict like object of default arguments
        Returns: (parser, ParsedArgs)
        parser supports a .error message for displaying an error and exiting with usage
        If a default key is callable then it is called with the current namespace,
        and then returned.
        """
        epilog = self.subparsers_summary()
        epilog += self.epilog
        return self(RootParser, epilog=epilog).parse_args(args, namespace, defaults)


class SubParsers(AbstractParser):
    """SubParsers are used for holding other Parsers.
    They are the building block of sub-commands.
    """
    def _init(self):
        self._parsers = []
        args = []
        for arg in self.args:
            if isinstance(arg, Arg):
                args.append(arg)
            elif isinstance(arg, Parser):
                self._parsers.append(arg)
            else:
                assert False, 'Unknown builder type {!r}'.format(type(arg))
        self._args = args
        for parser in self.parsers:
            parser._args = self._args + parser._args

    def _build(self, parser, kwargs):
        # python 2-3 compatible change
        # see https://stackoverflow.com/a/22994500/9899650
        if "dest" not in kwargs:
            kwargs["dest"] = self._name
        sp = parser.add_subparsers(title=self.name, **kwargs)
        # python 2-3 compatible change
        # see https://stackoverflow.com/a/23354355/9899650
        if "required" not in kwargs:
            sp.required = True
        for parser in self.parsers:
            parser(sp)
        return sp

    @property
    def parsers(self):
        return list(self._parsers)


class Group(object):
    def __init__(self, title, description, *args):
        self.title = title
        self.description = description
        self.args = []
        self._kwargs = {}
        for arg in args:
            if isinstance(arg, KW):
                self._kwargs.update(arg.kwargs)
            else:
                self.args.append(arg)

    def __call__(self, parser):
        grp = parser.add_argument_group(self.title, self.description)
        for arg in self.args:
            arg(grp, **self._kwargs)
        return grp


class Arg(object):
    """Arg wraps parser.add_arguments
    This class will pass all kwargs to the add_arguments call
    """
    def __init__(self, name, help=None, type=None, default=None, hidden=False,
                 **kwargs):
        self.name = name
        self.help = help
        self.type = type
        self.default = default
        self.hidden = hidden
        self.kwargs = kwargs

    def __call__(self, parser, **_kwargs):
        kwargs = self.kwargs.copy()
        if self.type:
            kwargs['type'] = self.type
        if self.help:
            if self.type:
                type_str = '<{}>'.format(str(self.type))
                kwargs['help'] = type_str + ' ' + self.help
            else:
                kwargs['help'] = self.help
        for k, v in _kwargs.items():
            kwargs[k] = v
        if self.hidden:
            kwargs['help'] = SUPPRESS
        kwargs['default'] = self.default
        if isinstance(self.name, six.string_types):
            names = [self.name]
        else:
            names = self.name
        action = parser.add_argument(*names, **kwargs)
        if action.nargs != 0:
            if self.type:
                type_str = '<{}>'.format(str(self.type))
                if action.option_strings != []:
                    action.metavar = type_str
            else:
                action.metavar = action.dest
        action.dest = action.dest.replace('-', '_')
        return parser
