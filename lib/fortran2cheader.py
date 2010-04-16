#! /usr/bin/env python
# -*- coding: utf-8 -*-

u"""
Generate a C/C++ header file from a Fortran source file using those
subroutines decorated with Fortran2003 `C_ISO_BINDINGS` `BIND` and
`C_*` types. `INTERFACE` blocks are ignored to allow direct usage of C
function calls in the `FORTRAN` code.

:author: `Berthold Hoellmann <hoel@GL-group.com>`__
:newfield project: Project
:project: Fortran2C Header
:copyright: Copyright (C) 2010 by Germanischer Lloyd AG

Parses FORTRAN 90 syntax.

Translation table taken from
<http://de.wikibooks.org/wiki/Fortran:_Fortran_und_C:_Fortran_2003>

+-----------+---------------------------+----------------------+
| Fortran-  | Benannte `iso_c_binding`- | C-Datentyp           |
| Datentyp  | Konstante (kind-Wert)     |                      |
+-----------+---------------------------+----------------------+
|           | c_int                     | int                  |
|           +---------------------------+----------------------+
|           | c_short                   | short int            |
|           +---------------------------+----------------------+
|           | c_long                    | long int             |
|           +---------------------------+----------------------+
|           | c_long_long               | long long int        |
|           +---------------------------+----------------------+
|           | c_signed_char             | signed char,         |
|           |                           | unsigned char        |
|           +---------------------------+----------------------+
|           | c_size_t                  | size_t               |
|           +---------------------------+----------------------+
|           | c_int8_t                  | int8_t               |
|           +---------------------------+----------------------+
|           | c_int16_t                 | int16_t              |
|           +---------------------------+----------------------+
|           | c_int32_t                 | int32_t              |
|           +---------------------------+----------------------+
| integer   | c_int64_t                 | int64_t              |
|           +---------------------------+----------------------+
|           | c_int_least8_t            | int_least8_t         |
|           +---------------------------+----------------------+
|           | c_int_least16_t           | int_least16_t        |
|           +---------------------------+----------------------+
|           | c_int_least32_t           | int_least32_t        |
|           +---------------------------+----------------------+
|           | c_int_least64_t           | int_least64_t        |
|           +---------------------------+----------------------+
|           | c_int_fast8_t             | int_fast8_t          |
|           +---------------------------+----------------------+
|           | c_int_fast16_t            | int_fast16_t         |
|           +---------------------------+----------------------+
|           | c_int_fast32_t            | int_fast32_t         |
|           +---------------------------+----------------------+
|           | c_int_fast64_t            | int_fast64_t         |
|           +---------------------------+----------------------+
|           | c_intmax_t                | intmax_t             |
|           +---------------------------+----------------------+
|           | c_intptr_t                | intptr_t             |
+-----------+---------------------------+----------------------+
|           | c_float                   | float                |
|           +---------------------------+----------------------+
| real      | c_double                  | double               |
|           +---------------------------+----------------------+
|           | c_long_double             | long double          |
+-----------+---------------------------+----------------------+
|           | c_float_complex           | float _Complex       |
|           +---------------------------+----------------------+
| complex   | c_double_complex          | double _Complex      |
|           +---------------------------+----------------------+
|           | c_long_double_complex     | long double _Complex |
+-----------+---------------------------+----------------------+
| logical   | c_bool                    | _Bool                |
+-----------+---------------------------+----------------------+
| character | c_char                    | char                 |
+-----------+---------------------------+----------------------+
"""

#  ID: $Id$
__date__      = u"$Date$"[5:-1]
__version__   = "$Revision$"[10:-1]
__docformat__ = "restructuredtext en"

from optparse import OptionParser
import os
import os.path
import re


def casi(inp):
    """Make string for case insenitive regular expression string::

>>> print casi('abc')
[aA][bB][cC]
"""
    outp = []
    letter = re.compile(r'^\w$')
    ws = re.compile(r'^\s$')
    for char in inp:
        if letter.match(char):
            outp.extend(('[', char.lower(), char.upper(), ']'))
        elif ws.match(char):
            outp.extend(('\\s',))
        else:
            outp.append(char)
    return ''.join(outp)

# SUBROUTINE SXFGeRh (iUnit, oRelName, oNoOAttr, oNoORows, oAttName,
#                     oAttType, oAttLeng) BIND(C,NAME="SXFGeRh")
_BIND = casi("BIND") + r'''
[(] \s*
(?:
  (?:
    (?P<C>C) |
    (?:''' + casi('NAME') + ''' ) \s* =
       \s* (?P<quot>[\'\"]) (?P<cName>[\w]+) (?P=quot)
  ) \s* ,? \s*
)+
\s* [)]
'''
_ARGS = '[(] \s* (?P<args> (?: [\w]+ \s* ,? \s* )* ) \s* [)] \s*'
_SUBROUTINE = re.compile(
    r'''
    ^
    (?: ''' +casi("SUBROUTINE") +''' ) \s+
    (?P<fName> [\w]+ ) \s*
    ''' + _ARGS + _BIND, re.VERBOSE)

# FUNCTION C_CALLOC(elt_count, elt_size) RESULT(ptr) BIND(C, NAME="calloc")
_FUNCTION = re.compile(
    r'''
    ^
    (?P<prefix> .+)?? \s*
    (?: ''' + casi("FUNCTION") + ''' ) \s+
    (?P<fName> [\w]+ ) \s*
    ''' + _ARGS +
    '''
    (?: ''' + casi("RESULT") + ''' \s*
    [(] \s* (?P<result> .+? ) [)] ) \s*
    ''' +
    _BIND, re.VERBOSE)
# INTEGER(C_INT), INTENT(IN), VALUE :: iUnit
_VARTYPE = re.compile(
    r'''
    ^
    (?P<ftype>
      (?: ''' + casi("INTEGER") + ''' ) |
      (?: ''' + casi("REAL") + ''' ) |
      (?: ''' + casi("COMPLEX") + ''' ) |
      (?: ''' + casi("LOGICAL") + ''' ) |
      (?: ''' + casi("CHARACTER") + ''' ) |
      (?: ''' + casi("TYPE") + ''' )
    )
    [(] \s* (?P<kind> [\w\d=]+ ) \s* [)] \s*
    (?P<modifier> (?: , \s* [*\w()]+ \s* )+ )? :: \s*
    (?P<args> (?: [\w]+ \s* ,? \s* )* )
    ''', re.VERBOSE)

_TYPE = re.compile(
r'''(?P<ftype>
      (?: ''' + casi("INTEGER") + ''' ) |
      (?: ''' + casi("REAL") + ''' ) |
      (?: ''' + casi("COMPLEX") + ''' ) |
      (?: ''' + casi("LOGICAL") + ''' ) |
      (?: ''' + casi("CHARACTER") + ''' ) |
      (?: ''' + casi("TYPE") + ''' )
    )
    [(] \s* (?P<kind> [\w\d=]+ ) \s* [)]
    ''', re.VERBOSE)

_INTERFACE = re.compile('^' + casi('INTERFACE') +'$')
_END_INTERFACE = re.compile('^' + casi('END INTERFACE') +'$')

class FortranSourceProvider(object):
    """Provide concatenated Fortran source lines for analysis.
"""

    def __init__(self, fname):
        self.fname = fname
        self.file = open(fname, 'r')

    def __iter__(self):
        return self

    def _read(self):
        """Return next raw line from input file, ignoring empty lines
and comments.
"""
        line = None
        while not line:
            line = self.file.next().strip()
            pos = line.find('!')
            if pos >= 0:
                line = line[:pos]
        return line

    def next(self):
        """Return next line.
"""
        line = self._read()
        while line.endswith('&'):
            line = line[:-1]
            nLine = self._read()
            if nLine.startswith('&'):
                nLine = nLine[1:]
            line += nLine
        return line.strip()

class Comment(object):
    """Provide C comments.
"""
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return "/*\n%s\n */\n" % self.text

class __Routine(object):
    """Base class for representing Fortran routines.
"""
    f_kinds = {
        'integer': {
            "c_int": "int",
            "c_short": "short int",
            "c_long": "long int",
            "c_long_long": "long long int",
            "c_size_t": "size_t",
            "c_int8_t": "int8_t",
            "c_int16_t": "int16_t",
            "c_int32_t": "int32_t",
            "c_int64_t": "int64_t",
            "c_int_least8_t": "int_least8_t",
            "c_int_least16_t": "int_least16_t",
            "c_int_least32_t": "int_least32_t",
            "c_int_least64_t": "int_least64_t",
            "c_int_fast8_t": "int_fast8_t",
            "c_int_fast16_t": "int_fast16_t",
            "c_int_fast32_t": "int_fast32_t",
            "c_int_fast64_t": "int_fast64_t",
            "c_intmax_t": "intmax_t",
            "c_intptr_t": "intptr_t"},
        'real': {
            "c_float": "float",
            "c_double": "double",
            "c_long_double": "long double"},
        'complex': {
            "c_float_complex": "float _Complex",
            "c_double_complex": "double _Complex",
            "c_long_double_complex": "long double _Complex"},
        'logical': {
            "c_bool": "_Bool"},
        'character': {
            "c_char": "char"},
        'type': {
            "c_ptr": "void*",
            "c_funptr": "(*)"}}

    def __init__(self, signed_to_unsigned_char):
        if signed_to_unsigned_char:
            self.f_kinds['integer']["c_signed_char"] = "unsigned char"
        else:
            self.f_kinds['integer']["c_signed_char"] = "signed char"
        self.argdict = None
        self.uargs = None
        self.comment = None
        self.name = None
        self.result = None

    def __str__(self):
        out = "%s" % self.comment
        proto = (" ".join(("extern", self.result, self.name)) +
                 '(%s);\n' % ', '.join(
                     "%s %s" % tuple(self.argdict[arg])
                     for arg in self.uargs))
        out += proto
        return out

    def add_arg(self, args, ftype, kind, modifier):
        """Add argument information to Subroutine information.
"""
        c_type = self.f_kinds.get(ftype.lower(), {}).get(kind.lower(), None)
        if (c_type and
            modifier and
            (not 'value' in modifier.lower()
             or 'dimension' in modifier.lower())):
            c_type += '*'
        # if c_type and modifier and 'dimension' in modifier.lower():
        #     c_type += '*'
        for arg in ( a.strip().upper() for a in args.split(',') ):
            if arg in self.uargs:
                self.argdict[arg][0] = c_type
        return c_type

class Subroutine(__Routine):
    """Representing Fortran SUBBROUTINEs
"""

    def __init__(self, line, cName, fName, args, signed_to_unsigned_char):
        super(Subroutine, self).__init__(signed_to_unsigned_char)
        self.comment = Comment(
            '\n'.join((
                "%s" % cName,
                "Generated from FORTRAN routine '%s'" % fName,
                "FORTRAN declaration:\n    %s" % line)))
        self.name = cName
        args = [ a.strip() for a in args if a ]
        self.uargs = [ a.upper() for a in args ]
        self.argdict = dict(( (a.upper(), [None, a]) for a in args ))
        self.result = "void"

class Function(__Routine):
    """Representing Fortran FUNCTIONs
"""
    def __init__(self, line, cName, fName, prefix, result, args,
                 signed_to_unsigned_char):
        super(Function, self).__init__(signed_to_unsigned_char)
        self.comment = Comment(
            '\n'.join((
                "%s" % cName,
                "Generated from FORTRAN routine '%s'" % fName,
                "FORTRAN declaration:\n    %s" % line)))
        self.name = cName
        args = [ a.strip() for a in args if a ]
        self.uargs = [ a.upper() for a in args ]
        self.argdict = dict(( (a.upper(), [None, a]) for a in args ))
        if result:
            self.resultN = result
        else:
            self.resultN = fName
        prefix = prefix and _TYPE.match(prefix)
        if prefix:
            self.result = self.f_kinds.get(
                prefix.group('ftype').lower(), {}
                ).get(prefix.group('kind').lower(), None)
        else:
            self.result = None

    def add_arg(self, args, ftype, kind, modifier):
        """Add argument information to Subroutine information.
"""
        c_type = super(Function, self).add_arg(args, ftype, kind, modifier)
        args = [ a.strip().upper() for a in args.split(',') ]
        if self.resultN.upper() in args:
            self.result = c_type

class Fortran2CHeader(object):
    """Extract a C header file from a Fortran file using
`BIND(C,name='xxx')` for providing a C compatible interface.

Only arguments with type kinds from `ISO_C_BINDING` module."""

    def __init__(self, fname, options):
        self.options = options
        self.input = fname

        self.basename = ".".join(os.path.basename(self.input).split(".")[:-1])

        self.data = FortranSourceProvider(self.input)

    def parse(self):
        """Parse the input file for `ISO_C_BINDING` information.
"""
        subr = None
        interface = False
        self.info = []
        for i in self.data:
            if not interface and _SUBROUTINE.match(i):
                if subr:
                    self.info.append(subr)
                line = _SUBROUTINE.match(i)
                gdict = line.groupdict()
                if not gdict['C']:
                    subr = None
                    continue
                subr = Subroutine(
                    signed_to_unsigned_char=
                       self.options.signed_to_unsigned_char,
                    fName=gdict['fName'],
                    cName=gdict['cName'],
                    args=gdict['args'].split(','),
                    line = i)
            elif not interface and _FUNCTION.match(i):
                if subr:
                    self.info.append(subr)
                line = _FUNCTION.match(i)
                gdict = line.groupdict()
                if not gdict['C']:
                    subr = None
                    continue
                subr = Function(
                    signed_to_unsigned_char=
                       self.options.signed_to_unsigned_char,
                    fName=gdict['fName'],
                    cName=gdict['cName'],
                    args=gdict['args'].split(','),
                    prefix=gdict['prefix'],
                    result=gdict['result'],
                    line = i)
            elif _INTERFACE.match(i):
                interface = True
            elif _END_INTERFACE.match(i):
                interface = False
            elif not interface and subr and _VARTYPE.match(i):
                line = _VARTYPE.match(i)
                gdict = line.groupdict()
                subr.add_arg(**gdict)

        if subr:
            self.info.append(subr)

    def gen_output(self, name):
        """Generating the output file.
"""
        outf = open(name, 'w')
        print >> outf, "\n".join(
            ( "%s" % s for s in
              (Comment("\n".join((
                  "%s.h" % self.basename,
                  "header file generated from parsing ISO_C_BINDING "
                  "information from %s." % self.input))),
               "",
               "#ifndef %s_H" % self.basename.upper(),
               "#define %s_H" % self.basename.upper(),
               "",
               "#ifdef __cplusplus",
               'extern "C" {',
               "#endif /* __cplusplus */",
               "") ))
        print >> outf, "\n".join(( "%s" % s for s in self.info ))
        print >> outf, "\n".join(
            ( "%s" % s for s in
              ("",
               "#ifdef __cplusplus",
               '} /* extern "C" */',
               "#endif /* __cplusplus */",
               "",
               "#endif /* %s_H */" % self.basename.upper()) ))

class Fortran2CHeaderCMD(Fortran2CHeader):
    """Command line interface for Fortran2CHeader
"""
    def __init__(self):
        options, args = self.parse_cmdline()
        super(Fortran2CHeaderCMD, self).__init__(fname=args[0], options=options)

    @staticmethod
    def parse_cmdline():
        """Parsing the command line options.
"""
        parser = OptionParser()
        parser.add_option("-s", "--signed-to-unsigned-char",
                          action="store_true", default=False,
                          help="\
use 'unsigned char' instead for 'signed char' for 'c_signed_char'")
        (options, args) = parser.parse_args()
        return (options, args)


def main():
    """Main program
"""
    fFile = Fortran2CHeaderCMD()
    fFile.parse()
    fFile.gen_output("%s.h" % fFile.basename)

if __name__ == "__main__":
    main()

# Local Variables:
# mode:python
# mode:flyspell
# compile-command:"cd .. ; python setup.py build"
# End:
