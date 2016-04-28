import unittest

from terseparse import Arg, Parser

class TestParsedArgs(unittest.TestCase):
    def test_to_named_params(self):
        parser = Parser('name', 'description',
            Arg('a', 'arg a'),
            Arg('b', 'arg b'),
            Arg('c', 'arg c'))

        _, args = parser.parse_args('a b c'.split())
        self.assertEqual(args.ns.a, 'a')
        self.assertEqual(args.ns.b, 'b')
        self.assertEqual(args.ns.c, 'c')

    def test_to_dict(self):
        parser = Parser('name', 'description',
            Arg('a', 'arg a'),
            Arg('b', 'arg b'),
            Arg('c', 'arg c'))

        _, args = parser.parse_args('1 2 3'.split())
        dic = dict(args.ns)
        self.assertEqual(dic['a'], '1')
        self.assertEqual(dic['b'], '2')
        self.assertEqual(dic['c'], '3')

    def test_positional_args(self):
        parser = Parser('', '',
            Arg(('-a', '--arg'), 'arg'))

        _, args = parser.parse_args('-a asdf'.split())
        self.assertEqual(args.ns.arg, 'asdf')

        _, args = parser.parse_args('--arg asdf'.split())
        self.assertEqual(args.ns.arg, 'asdf')
