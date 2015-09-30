import unittest

from terseparse import Arg, Group, KW, Parser, SubParsers, types, Lazy
from . import assert_conv_fails


class TestTerseParse(unittest.TestCase):
    def test_argparse_example(self):
        p = Parser(
            'cmd', 'Process some integers',
            Arg('integers', 'an integer for the accumulator',
                metavar='N', type=int, nargs='+'),
            Arg('--sum', 'sum the integers (default: find the max)',
                dest='accumulate', action='store_const',
                const=sum, default=max))
        parser, args = p.parse_args('1 2 3 4'.split())
        self.assertEqual(args.ns.accumulate(args.ns.integers), 4)

        parser, args = p.parse_args('1 2 3 4 --sum'.split())
        self.assertEqual(args.ns.accumulate(args.ns.integers), 10)

    def test_multiple_subparsers(self):
        # Multiple Subparsers are not supported by argpase
        with self.assertRaises(AssertionError):
            Parser(
                'cmd', 'cmd-description',
                SubParsers('sp1', 'sp1-description'),
                SubParsers('sp2', 'sp2-description'))
    
    def test_subparser_common_args(self):
        p = Parser(
            'cmd', 'cmd-description',
            SubParsers('sp', 'sp-description', KW(dest='sp'),
                Arg('arg0', 'arg0-description'),
                Parser('p0', 'p0-description'),
                Parser('p1', 'p0-description',
                    Arg('p1-arg0', 'p1-arg0-description')),
                Arg('arg1', 'arg0-description')))

        parser, args = p.parse_args('p0 1 2'.split())
        self.assertEqual(args.ns.sp, 'p0')
        self.assertEqual(args.ns.arg0, '1')
        self.assertEqual(args.ns.arg1, '2')
        
        parser, args = p.parse_args('p1 a b c'.split())
        self.assertEqual(args.ns.sp, 'p1')
        self.assertEqual(args.ns.arg0, 'a')
        self.assertEqual(args.ns.arg1, 'b')
        self.assertEqual(args.ns.p1_arg0, 'c')

    def test_group(self):
        p = Parser('p', 'p-description',
            Group('grp', 'grp-description',
                Arg('a'),
                Arg('b')))
        parse, args = p.parse_args('a b'.split())
        self.assertEqual(args.ns.a, 'a')
        self.assertEqual(args.ns.b, 'b')

    def test_lazy(self):
        p = Parser('p', 'description',
                Arg('--b', 'description', types.Int.positive,
                    Lazy(lambda ns: ns.a)),
                Arg('a', 'description', types.Int.positive))

        parser, args = p.parse_args('1234'.split())
        self.assertEqual(args.ns.a, 1234)
        self.assertEqual(args.ns.b, 1234)

        parser, args = p.parse_args('--b 4321 1234'.split())
        self.assertEqual(args.ns.a, 1234)
        self.assertEqual(args.ns.b, 4321)


class TestTerseParseTypes(unittest.TestCase):
    def test_Int(self):
        t = types.Int(-0xF, 0x10)
        self.assertEqual(t('-15'), -15)
        self.assertEqual(t('-0xF'), -0xF)
        self.assertEqual(t('0xF'), 15)
        self.assertEqual(t('15'), 15)

        assert_conv_fails(t, '-16')
        assert_conv_fails(t, '-0x10')
        assert_conv_fails(t, '0x10')
        assert_conv_fails(t, '16')

    def test_Int_leading_zero(self):
        t = types.Int()
        self.assertEqual(t('00'), 0)
        self.assertEqual(t('-00'), 0)
        self.assertEqual(t('043'), 43)

    def test_Int_u32(self):
        t = types.Int.u32
        
        self.assertEqual(t('0'), 0)
        self.assertEqual(t('0xFFFFFFFF'), 2**32 - 1)

        assert_conv_fails(t, '-1')
        assert_conv_fails(t, '0xFFFFFFFF + 1')

    def test_Or(self):
        t = types.Or(types.Int.negative, types.Int(1, 10))

        assert_conv_fails(t, '0')

        self.assertEqual(t('-10'), -10)
        self.assertEqual(t('9'), 9)

    def test_Dict(self):
        t = types.Dict({'a': types.Int(0, 2), 'b': str})

        assert_conv_fails(t, 'asdf')
        assert_conv_fails(t, 'a:-1')
        assert_conv_fails(t, 'a:2')
        assert_conv_fails(t, 'a:2 b:asdf')

        self.assertEqual(t('a:0'), {'a': 0})
        self.assertEqual(t('b:asdf'), {'b': 'asdf'})
        self.assertEqual(t('a:0 b:asdf'), {'a': 0, 'b': 'asdf'})
        self.assertEqual(t('a=0,b=asdf'), {'a': 0, 'b': 'asdf'})
        self.assertEqual(t('a:1, b=asdf'), {'a': 1, 'b': 'asdf'})

    def test_Dict_punctuation(self):
        t = types.Dict({'a': str, 'b': str})
        self.assertEqual(t('a:/a/b/c/d,b:/e/f/g'), {'a': '/a/b/c/d', 'b': '/e/f/g'})

    def test_Dict_to_Set(self):
        dt = types.Dict({'a': types.Int(0, 2), 'b': str})
        t = dt.keys_to_set_type()
        self.assertEqual(t('a a'), {'a'})
        self.assertEqual(t('a b'), {'a', 'b'})
        self.assertEqual(t('b, a'), {'a', 'b'})

    def test_List(self):
        t = types.List(types.Or(types.Keyword('a'), types.Keyword('b')))
        assert_conv_fails(t, 'asdf')
        assert_conv_fails(t, 'bsdf')

        self.assertEqual(t('a'), ['a'])
        self.assertEqual(t('b'), ['b'])
        self.assertEqual(t('a b'), ['a', 'b'])
