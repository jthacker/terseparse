[![Build Status](https://travis-ci.org/jthacker/terseparse.svg?branch=master)](https://travis-ci.org/jthacker/terseparse.svg?branch=master)

# terseparse: Terse argument parsing
Terseparse was designed for user friendly typing of arguments and constructing parsers with minimal boiler plate.

## Install
```
$ pip install git+git://github.com/jthacker/terseparse.git@v1.0
```

## Features
- A composable syntax for constructing parsers
- Extensive set of types with helpful error messages
- All arguments and parsers require documentation strings
- Metavars are created automatically
- Metavars provide type information
- Subparser names and descriptions are displayed in help messages
- Arguments in subparsers are added to all childer parsers
- Debugging of the parser can be done at runtime


## Usage
```python
p = Parser('cmd', 'Process some integers',
    Arg('integers', 'an integer for the accumulator',
        metavar='N', type=int, nargs='+'),
    Arg('--sum', 'sum the integers (default: find the max)',
        dest='accumulate', action='store_const',
        const=sum, default=max))
_, args = p.parse_args('1 2 3 4'.split())
print(args.ns.integers)
```
