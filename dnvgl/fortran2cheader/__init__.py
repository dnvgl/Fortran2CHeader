#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate a C/C++ header file from a Fortran source file using those
subroutines decorated with Fortran2003 `C_ISO_BINDINGS` `BIND` and
`C_*` types. `INTERFACE` blocks are ignored to allow direct usage of C
function calls in the `FORTRAN` code.

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

from __future__ import (
    division, print_function, absolute_import, unicode_literals)

# Standard libraries.
import os
import re
import sys
import codecs
import os.path
import argparse

# ID: $Id$
__date__ = "$Date::                            $"[7:-1]
__scm_version__ = "$Revision$"[10:-1]
__author__ = "`Berthold Höllmann <berthold.hoellmann@dnvgl.com>`__"
__copyright__ = "Copyright © 2010 by DNV GL SE"


def casi(inp):
    """Make string for case insenitive regular expression string::

>>> casi('abc') == '[aA][bB][cC]'
True
"""
    outp = []
    letter = re.compile(r'^\w$')
    whitespace = re.compile(r'^\s$')
    for char in inp:
        if letter.match(char):
            outp.extend(('[', char.lower(), char.upper(), ']'))
        elif whitespace.match(char):
            outp.append('\\s')
        else:
            outp.append(char)
    return ''.join(outp)


# SUBROUTINE SXFGeRh (iUnit, oRelName, oNoOAttr, oNoORows, oAttName,
#                     oAttType, oAttLeng) BIND(C,NAME="SXFGeRh")
_BIND = casi("BIND") + r'''
\( \s*
(?:
  (?:
    (?P<C>[Cc]) |
    (?:''' + casi('NAME') + ''' ) \s* =
       \s* (?P<quot>[\'\"]) (?P<cName>[\w]+) (?P=quot)
  ) \s* ,? \s*
)+
\s* \)
'''
# This solution becomes to slow to long argument lists.
# _ARGS = '\( \s* (?P<args> (?: \w+? \s* ,? \s* )* ) \s* \) \s*'
_ARGS = '\( \s* (?P<args> .*? ) \s* \) \s*'
_SUBROUTINE = re.compile(
    r'''
    ^
    (?: ''' + casi("SUBROUTINE") + ''' ) \s+
    (?P<fName> \w+ ) \s*
    ''' + _ARGS + _BIND, re.VERBOSE)

# FUNCTION C_CALLOC(elt_count, elt_size) RESULT(ptr) BIND(C, NAME="calloc")
_FUNCTION = re.compile(
    r'''
    ^
    (?P<prefix> .+)?? \s*
    (?: ''' + casi("FUNCTION") + ''' ) \s+
    (?P<fName> \w+ ) \s*
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
    \( \s*
      (?:
        (?:
          (?: (?: ''' + casi("KIND=") + ''' )? (?P<kind> [\w\d]+ ) )? |
          (?: (?: ''' + casi("LEN=") + ''' ) (?P<len> [\d]+ ) )?
        ) \s* ,?
      )*
    \s* \) \s*
    (?P<modifier> (?: , \s* [*\w()]+ \s* )+ )? :: \s*
    (?P<args> (?: [\w]+ \s* ,? \s* )* )
    ''', re.VERBOSE)

_INTENT = re.compile(".*" + casi("intent") + "\s*\(\s*(?P<dir> " +
                     '(?:' + casi("IN") + ")|" +
                     '(?:' + casi("OUT") + ")|" +
                     '(?:' + casi("INOUT") + ")|" +
                     '(?:' + casi("IN,OUT") + "))\s*\).*", re.VERBOSE)

_TYPE = re.compile(
    r'''(?P<ftype>
      (?: ''' + casi("INTEGER") + ''' ) |
      (?: ''' + casi("REAL") + ''' ) |
      (?: ''' + casi("COMPLEX") + ''' ) |
      (?: ''' + casi("LOGICAL") + ''' ) |
      (?: ''' + casi("CHARACTER") + ''' ) |
      (?: ''' + casi("TYPE") + ''' )
    )
    \( \s* (?P<kind> [\w\d=]+ ) \s* \)
    ''', re.VERBOSE)

_INTERFACE = re.compile('^' + casi('INTERFACE') + '$')
_END_INTERFACE = re.compile('^' + casi('END INTERFACE') + '$')


class FileType(object):

    """Factory for creating file object types

    Instances of FileType are typically passed as type= arguments to the
    ArgumentParser add_argument() method.

    Keyword Arguments:
        - mode -- A string indicating how the file is to be opened. Accepts the
            same values as the builtin open() function.
        - bufsize -- The file's desired buffer size. Accepts the same values as
            the builtin open() function.
    """

    def __init__(self, mode='r', bufsize=-1):
        self._mode = mode
        self._bufsize = bufsize

    def __call__(self, string):
        # the special argument "-" means sys.std{in,out}
        if string == '-':
            if 'r' in self._mode:
                return _sys.stdin
            elif 'w' in self._mode:
                return _sys.stdout
            else:
                msg = _('argument "-" with mode %r') % self._mode
                raise ValueError(msg)

        # all other arguments are used as file names
        try:
            return codecs.open(filename=string, mode=self._mode,
                               encoding='utf8', errors='ignore')
        except IOError as e:
            message = _("can't open '%s': %s")
            raise ArgumentTypeError(message % (string, e))

    def __repr__(self):
        args = self._mode, self._bufsize
        args_str = ', '.join(repr(arg) for arg in args if arg != -1)
        return '%s(%s)' % (type(self).__name__, args_str)


class FortranSourceProvider(object):

    """Provide concatenated Fortran source lines for analysis.
"""

    def __init__(self, data):
        self.file = data

    def __iter__(self):
        return self

    def _read(self):
        """Return next raw line from input file, ignoring empty lines
and comments.
"""
        line = None
        while not line:
            line = next(self.file).strip()
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

    __next__ = next


class Comment(object):

    """Provide C comments.
"""
    flavour = "C"

    def __init__(self, text):
        self.text = text

    def __str__(self):
        text = self.text.split('\n')
        if Comment.flavour == 'C':
            return "/*\n%s\n */\n" % ('\n'.join(
                ('  %s' % i).rstrip() for i in text),)
        elif Comment.flavour == 'pxd':
            return '\n'.join((("# %s" % t).strip() for t in text))
        else:
            return '\n'.join(text)


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
            "c_bool": "char"},  # "_Bool"},
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
        args = ', '.join("%s %s" % tuple(self.argdict[arg])
                         for arg in self.uargs)
        if Comment.flavour == 'C':
            if not args:
                args = 'void'
            proto = (" ".join(("extern", self.result, self.name)) +
                     '(%s);\n' % args)
        elif Comment.flavour == 'pxd':
            proto = "\n    %s" % (" ".join((self.result, self.name)) +
                                  '(%s)\n' % args)

        out += proto
        return out

    def add_arg(self, args, ftype, kind, modifier, len):
        """Add argument information to Subroutine information.
"""
        c_type = self.f_kinds.get(ftype.lower(), {}).get(kind.lower(), None)
        intent = modifier and _INTENT.match(modifier)
        if c_type and modifier and intent and \
           intent.groupdict()['dir'].lower() == 'in':
            c_type = "const " + c_type
        if (c_type and
            modifier and
            ('value' not in modifier.lower() or
             'dimension' in modifier.lower())):
            c_type += '*'
        # if c_type and modifier and 'dimension' in modifier.lower():
        #     c_type += '*'
        for arg in (a.strip().upper() for a in args.split(',')):
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
        args = [a.strip() for a in args if a]
        self.uargs = [a.upper() for a in args]
        self.argdict = {a.upper(): [None, a] for a in args}
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
        args = [a.strip() for a in args if a]
        self.uargs = [a.upper() for a in args]
        self.argdict = {a.upper(): [None, a] for a in args}
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

    def add_arg(self, args, ftype, kind, modifier, len):
        """Add argument information to Subroutine information.
"""
        c_type = super(Function, self).add_arg(args, ftype, kind, modifier,
                                               len)
        args = [a.strip().upper() for a in args.split(',')]
        if self.resultN.upper() in args:
            self.result = c_type


class Fortran2CHeader(object):

    """Extract a C header file from a Fortran file using
`BIND(C,name='xxx')` for providing a C compatible interface.

Only arguments with type kinds from `ISO_C_BINDING` module."""

    def __init__(self, data, options, name):
        self.options = options
        self.input = data

        self.name = name
        self.basename = ".".join(os.path.basename(name).split(".")[:-1])

        self.data = FortranSourceProvider(self.input)

    def parse(self):
        """Parse the input file for `ISO_C_BINDING` information.
"""
        subr = None
        interface = False
        self.info = []
        for i in self.data:
            vartype = _VARTYPE.match(i)
            if not interface and _SUBROUTINE.match(i):
                if subr:
                    self.info.append(subr)
                line = _SUBROUTINE.match(i)
                gdict = line.groupdict()
                if not gdict['C']:
                    subr = None
                    continue
                subr = Subroutine(
                    signed_to_unsigned_char=(
                        self.options.signed_to_unsigned_char),
                    fName=gdict['fName'],
                    cName=gdict['cName'],
                    args=gdict['args'].split(','),
                    line=i)
            elif not interface and _FUNCTION.match(i):
                if subr:
                    self.info.append(subr)
                line = _FUNCTION.match(i)
                gdict = line.groupdict()
                if not gdict['C']:
                    subr = None
                    continue
                subr = Function(
                    signed_to_unsigned_char=(
                        self.options.signed_to_unsigned_char),
                    fName=gdict['fName'],
                    cName=gdict['cName'],
                    args=gdict['args'].split(','),
                    prefix=gdict['prefix'],
                    result=gdict['result'],
                    line=i)
            elif _INTERFACE.match(i):
                interface = True
            elif _END_INTERFACE.match(i):
                interface = False
            elif (not interface and subr and
                  vartype and vartype.groupdict()['kind']):
                gdict = vartype.groupdict()
                subr.add_arg(**gdict)

        if subr:
            self.info.append(subr)

    def gen_output(self, outf, name):
        """Generating the output file.
"""
        Comment.flavour = "C"
        print("\n".join(
            (("%s" % s).rstrip() for s in
             (Comment("\n".join((
                 "%s" % name,
                 "Header file generated from parsing ISO_C_BINDING "
                 "information",
                 "from %s." % self.name,
                 "",
                 "Generated by %s, version %s." % (
                     sys.argv[0], __scm_version__.strip())))),
              "",
              "#ifndef %s_H" % self.basename.upper(),
              "#define %s_H" % self.basename.upper(),
              "",
              "#ifdef __cplusplus",
              'extern "C" {',
              "#endif /* __cplusplus */",
              ""))), file=outf)
        print("\n".join(("%s" % s for s in self.info)), file=outf)
        print("\n".join(
            ("%s" % s for s in
             ("",
              "#ifdef __cplusplus",
              '} /* extern "C" */',
              "#endif /* __cplusplus */",
              "",
              "#endif /* %s_H */" % self.basename.upper()))), file=outf)

    def gen_pxd(self, outf, header=None):
        """Generating the output file.
"""
        if header is None:
            header = "%s.h" % self.basename
        Comment.flavour = "pxd"
        print("\n".join(
            (("%s" % s).rstrip() for s in
             (Comment("\n".join((
                 "%s.pxd" % self.name,
                 "Cython Header file generated from parsing ISO_C_BINDING "
                 "information",
                 "from %s." % self.input,
                 "",
                 "Generated by %s, version %s." % (
                     os.path.split(sys.argv[0])[-1],
                     __scm_version__.strip())))),
              "",
              'cdef extern from "%s" nogil:' % (header,)))), file=outf)
        print("\n".join((("%s" % s).rstrip() for s in self.info)), file=outf)


class Fortran2CHeaderCMD(Fortran2CHeader):

    """Command line interface for Fortran2CHeader
"""

    def __init__(self):
        options = self.parse_cmdline()
        super(Fortran2CHeaderCMD, self).__init__(
            data=options.infile, options=options, name=options.infile.name)

    @staticmethod
    def parse_cmdline():
        """Parsing the command line options.
"""
        parser = argparse.ArgumentParser(description='''Generate a C/C++
header file from a Fortran file using C_ISO_BINDINGS.''')
        parser.add_argument("infile", type=FileType('r'),
                            help="Fortran input file")
        parser.add_argument("--signed-to-unsigned-char", "-s",
                            action="store_true", default=False,
                            help="""use 'unsigned char' instead for
'signed char' for 'c_signed_char'""")
        options = parser.parse_args()
        return options


def main():
    """Main program
"""
    fFile = Fortran2CHeaderCMD()
    fFile.parse()
    name = "%s.h" % fFile.basename
    with open(name, 'w') as ofile:
        fFile.gen_output(ofile, name)


if __name__ == "__main__":
    main()

# Local Variables:
# mode: python
# compile-command: "cd ../.. ; python setup.py test"
# End:
