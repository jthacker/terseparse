import pytest

from terseparse import Arg, Parser

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
