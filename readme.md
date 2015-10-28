[![Build Status](https://travis-ci.org/jthacker/terseparse.svg?branch=master)](https://travis-ci.org/jthacker/terseparse)

# terseparse: Terse argument parsing
Terseparse was designed for user friendly typing of arguments and constructing parsers with minimal boiler plate.

## Install
```
$ pip install -e git+git://github.com/jthacker/terseparse.git@v1.0#egg=terseparse
```

## Features
- A composable syntax for constructing parsers
- Extensive set of types with helpful error messages
- All arguments and parsers require documentation strings
- Metavars are created automatically
- Metavars provide type information
- Subparser names and descriptions are displayed in help messages
- Arguments in subparsers are added to all children parsers
- Debugging of the parser can be done at runtime
- Unique namespace for arguments, no conflicts with other properties


## Usage
This example is taken from the argparse [documentation](https://docs.python.org/3/library/argparse.html#example)
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

### Argument Namespace
Unlike argparse, arguments are stored in a unique namespace under args.ns.
This is done to avoid conflicts between existing methods in args and parameter
values being parsed (e.g. .keys() would conflict with a keys parameter).



### Debugging
Terseparse argument parsing can be debugged by passing in --terseparse-debug
as the first argument. It must be the first argument so that the parsing of the rest
of the arguments can take place as they are parsed.
