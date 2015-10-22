import unittest

from terseparse import Arg, Parser

class TestParsedArgs(unittest.TestCase):
    def setUp(self):
        self.parser = Parser('name', 'description',
            Arg('a', 'arg a'),
            Arg('b', 'arg b'),
            Arg('c', 'arg c'))

    def test_to_dict(self):
        _, args = self.parser.parse_args('1 2 3'.split())
        dic = dict(args.ns)
        self.assertEqual(dic['a'], '1')
        self.assertEqual(dic['b'], '2')
        self.assertEqual(dic['c'], '3')
