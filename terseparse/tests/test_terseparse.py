import pytest

from terseparse import Arg, Group, KW, Parser, SubParsers, types, Lazy


def test_argparse_example():
    p = Parser(
        'cmd', 'Process some integers',
        Arg('integers', 'an integer for the accumulator',
            metavar='N', type=int, nargs='+'),
        Arg('--sum', 'sum the integers (default: find the max)',
            dest='accumulate', action='store_const',
            const=sum, default=max))
    _, args = p.parse_args('1 2 3 4'.split())
    assert args.ns.accumulate(args.ns.integers) == 4

    _, args = p.parse_args('1 2 3 4 --sum'.split())
    assert args.ns.accumulate(args.ns.integers) == 10

def test_multiple_subparsers():
    # Multiple Subparsers are not supported by argpase
    with pytest.raises(AssertionError):
        Parser(
            'cmd', 'cmd-description',
            SubParsers('sp1', 'sp1-description'),
            SubParsers('sp2', 'sp2-description'))

def test_subparser_common_args():
    p = Parser(
        'cmd', 'cmd-description',
        SubParsers('sp', 'sp-description', KW(dest='sp'),
            Arg('arg0', 'arg0-description'),
            Parser('p0', 'p0-description'),
            Parser('p1', 'p0-description',
                Arg('p1-arg0', 'p1-arg0-description')),
            Arg('arg1', 'arg0-description')))

    _, args = p.parse_args('p0 1 2'.split())
    assert args.ns.sp == 'p0'
    assert args.ns.arg0 == '1'
    assert args.ns.arg1 == '2'

    _, args = p.parse_args('p1 a b c'.split())
    assert args.ns.sp == 'p1'
    assert args.ns.arg0 == 'a'
    assert args.ns.arg1 == 'b'
    assert args.ns.p1_arg0 == 'c'

def test_group():
    p = Parser('p', 'p-description',
        Group('grp', 'grp-description',
            Arg('a'),
            Arg('b')))
    _, args = p.parse_args('a b'.split())
    assert args.ns.a == 'a'
    assert args.ns.b == 'b'

def test_lazy():
    p = Parser('p', 'description',
            Arg('--b', 'description', types.Int.positive,
                Lazy(lambda ns: ns.a)),
            Arg('a', 'description', types.Int.positive))

    _, args = p.parse_args('1234'.split())
    assert args.ns.a == 1234
    assert args.ns.b == 1234

    _, args = p.parse_args('--b 4321 1234'.split())
    assert args.ns.a == 1234
    assert args.ns.b == 4321
