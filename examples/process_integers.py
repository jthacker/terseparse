#!/usr/bin/env python
from terseparse import Parser, Arg

description = '''Process some integers
This example is adapted to terseparse syntax from the argument parser library
'''

p = Parser('cmd', description,
    Arg('integers', 'an integer for the accumulator',
        metavar='N', type=int, nargs='+'),
    Arg('--sum', 'sum the integers (default: find the max)',
        dest='accumulate', action='store_const',
        const=sum, default=max))

_, args = p.parse_args()
args.pprint()
import pdb; pdb.set_trace()
print(args.ns.accumulate(args.ns.integers))
