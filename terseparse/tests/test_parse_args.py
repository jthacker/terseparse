import pytest

from terseparse import Arg, Parser, types
from terseparse.builders import SubParsers

def test_to_named_params():
    parser = Parser('name', 'description',
        Arg('a', 'arg a'),
        Arg('b', 'arg b'),
        Arg('c', 'arg c'))

    _, args = parser.parse_args('a b c'.split())
    assert args.ns.a == 'a'
    assert args.ns.b == 'b'
    assert args.ns.c == 'c'

def test_to_dict():
    parser = Parser('name', 'description',
        Arg('a', 'arg a'),
        Arg('b', 'arg b'),
        Arg('c', 'arg c'))

    _, args = parser.parse_args('1 2 3'.split())
    dic = dict(args.ns)
    assert dic['a'] == '1'
    assert dic['b'] == '2'
    assert dic['c'] == '3'

def test_positional_args():
    parser = Parser('', '',
        Arg(('-a', '--arg'), 'arg'))

    _, args = parser.parse_args('-a asdf'.split())
    assert args.ns.arg == 'asdf'

    _, args = parser.parse_args('--arg asdf'.split())
    assert args.ns.arg == 'asdf'

def test_too_few_args():
    parser = Parser('', '', Arg("a", "arg"))
    with pytest.raises(SystemExit) as e:
        _, _ = parser.parse_args()
    assert e.value.code > 0

def test_subparsers_are_required_by_default():
    parser = Parser(
        '',
        '',
        SubParsers(
            'command',
            ''))
    with pytest.raises(SystemExit) as e:
        _, _ = parser.parse_args()
    assert e.value.code > 0

def test_subparsers_with_args_passed_to_parsers():
    parser = Parser(
        '',
        '',
        SubParsers(
            'command',
            '',
            Arg('first_arg', ''),
            Parser('subparser1', ''),
            Parser('subparser2', '')))
    with pytest.raises(SystemExit) as e:
        _, args = parser.parse_args(["subparser1"])
    assert e.value.code > 0
    _, args = parser.parse_args(["subparser1", "arg1"])
    assert args.ns.first_arg == "arg1"
    _, args = parser.parse_args(["subparser2", "arg2"])
    assert args.ns.first_arg == "arg2"

def test_default_arg():
    parser = Parser(
        '',
        '',
        Arg('--optional', '', default='default')
    )
    _, args = parser.parse_args()
    assert args.ns.optional == 'default'

def test_default_arg_keyword():
    parser = Parser(
        '',
        '',
        Arg('--optional', '', types.Keyword('key', 'value'), default='key')
    )
    _, args = parser.parse_args()
    assert args.ns.optional == 'value'
