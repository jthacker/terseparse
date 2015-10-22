import sys
import logging
from argparse import ArgumentParser, RawTextHelpFormatter, _SubParsersAction, SUPPRESS
from collections import namedtuple, OrderedDict


def is_subparser(action_group):
    for a in action_group._group_actions:
        if isinstance(a, _SubParsersAction):
            return True
    return False


class CustomHelpFormatter(RawTextHelpFormatter):
    def __init__(self, *args, **kwargs):
        super(CustomHelpFormatter, self).__init__(*args, **kwargs)
        self._action_max_length = 10


class Lazy(object):
    """Lazily load a default argument after the args have been parsed"""
    def __init__(self, val):
        self.val = val

    def __call__(self, parsed_args_namespace):
        if callable(self.val):
            return self.val(parsed_args_namespace)
        return self.val


class ParsedArgsNamespace(object):
    def __init__(self, keywords, defaults):
        self._keywords = keywords
        self._defaults = defaults or {}
    
    def __getattr__(self, key):
        val = self._keywords.get(key)
        if val is not None:
            if isinstance(val, Lazy):
                val = val(self)
                self._keywords[key] = val
            return val
        val = self._defaults.get(key)
        if val is not None:
            if callable(val):
                val = val(self)
                self._keywords[key] = val
            return val
   
    def __dir__(self):
        return sorted(set(dir(type(self)) + self._keywords + self._defaults))

    def __repr__(self):
        return 'ParsedArgsNamespace(%r, %r)' % (self._keywords, self._defaults)


class ParsedArgs(object):
    def __init__(self, keywords, defaults):
        self.ns = ParsedArgsNamespace(keywords, defaults)

    def items(self):
        return self.ns._keywords.items()


def _print_args(args):
    spacer = ' ' * 4
    items = args.items()
    arg_len = max(3, max(len(arg) for arg, val in items))
    hfmt = '{:{}}'+spacer+'{}'
    lfmt = '{:{}}'+spacer+'{!r}'
    msg = '\n'.join(lfmt.format(arg, arg_len, val) for arg, val in items)
    title = 'TerseParse Debug Information:' 
    header =  hfmt.format('arg', arg_len, 'value') + '\n'
    header += hfmt.format('---', arg_len, '-----')
    print(title)
    print('=' * len(title))
    print(header)
    print(msg)
    

class RootParser(ArgumentParser):
    """Private Class."""
    @staticmethod
    def add_parser(*args, **kwargs):
        return RootParser(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        kwargs['formatter_class'] = CustomHelpFormatter
        super(RootParser, self).__init__(*args, **kwargs)
        self._debug = False

    """
    def print_usage(self, *args, **kwargs):
        '''overrides print_usage method to always produce verbose output'''
        self.print_help(*args, **kwargs)
    """
  
    def error(self, message):
        """Overrides error to control printing output"""
        if self._debug:
            import pdb
            _, _, tb = sys.exc_info()
            if tb:
                pdb.post_mortem(tb)
            else:
                pdb.set_trace()
        self.print_usage(sys.stderr)
        self.exit(2, ('\nERROR: {}\n').format(message))

    def format_help(self):
        """Overrides format_help to not print subparsers"""
        formatter = self._get_formatter()

        # usage
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups)

        # description
        formatter.add_text(self.description)

        # positionals, optionals and user-defined groups, except SubParsers
        for action_group in self._action_groups:
            if is_subparser(action_group):
                continue
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

        # epilog
        formatter.add_text(self.epilog)

        # determine help from format above
        return formatter.format_help()

    def parse_args(self, args=None, namespace=None, defaults=None):
        if not args:
            args = sys.argv[1:]

        if len(args) > 0 and args[0] == '--terseparse-debug':
            self._debug = True
            logging.getLogger().setLevel(logging.DEBUG)
            logging.basicConfig()
            args = args[1:]

        parser = super(RootParser, self)
        ns = parser.parse_args(args, namespace)
        parsed_args = ParsedArgs(OrderedDict(ns._get_kwargs()), defaults)
        if self._debug:
            _print_args(parsed_args)
        return parser, parsed_args
