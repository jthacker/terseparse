#!/usr/bin/env python
from terseparse import Arg, KW, Parser, SubParsers, types

description = '''shows an example of using subparsers'''


parser = Parser(__file__, description,
        Arg('--arg0', 'arg 0', type=types.Int()),
        SubParsers('command', '', KW(dest='command'),
            Arg('common', 'this argument is common to all sub parsers', type=int),
            Parser('a', 'parser a',
                Arg('arg0', 'arg 0', type=int),
                Arg('arg1', 'arg 1', type=int),),
            Parser('b', 'parser b',
                Arg('arg0', 'arg 0', type=str),
                Arg('arg1', 'arg 1', type=str))))

_, args = parser.parse_args()
args.pprint()
