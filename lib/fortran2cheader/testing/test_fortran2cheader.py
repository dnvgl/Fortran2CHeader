#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for Fortran2CHeader.
"""

from __future__ import (
    division, print_function, absolute_import, unicode_literals)

# Standard libraries.
import re
from cStringIO import StringIO

# Third party libraries.
import pytest

from .. import _ARGS, _BIND, _VARTYPE, _SUBROUTINE, Fortran2CHeader

# ID: $Id$"
__date__ = "$Date$"[6:-1]
__version__ = "$Revision$"[10:-1]
__author__ = "`Berthold Höllmann <berthold.hoellmann@dnvgl.com>`__"
__copyright__ = "Copyright © 2014 by DNV GL SE"


class d_opt(object):

    def __init__(self, signed_to_unsigned_char=False):
        self.signed_to_unsigned_char = signed_to_unsigned_char


class TestRegexps(object):

    def test_c_int(self):
        res = _VARTYPE.match("INTEGER(C_INT), INTENT(IN), VALUE :: iUnit")
        assert res.groupdict() == {
            'kind': 'C_INT', 'ftype': 'INTEGER', 'args': 'iUnit',
            'modifier': ', INTENT(IN), VALUE ', 'len': None}

    def test_caracter_1(self):
        res = _VARTYPE.match("character(kind=c_char), intent(in) :: s(*)")
        assert res.groupdict() == {
            'kind': 'c_char', 'ftype': 'character', 'args': 's',
            'modifier': ', intent(in) ', 'len': None}

    def test_caracter_2(self):
        res = _VARTYPE.match(
            "character(kind=c_char,len=1), intent(in) :: s(*)")
        assert res.groupdict() == {
            'kind': 'c_char', 'ftype': 'character', 'args': 's',
            'modifier': ', intent(in) ', 'len': '1'}

    def test_caracter_3(self):
        res = _VARTYPE.match(
            "character(kind=c_char,len=1), dimension(*), intent(in) :: s")
        assert res.groupdict() == {
            'kind': 'c_char', 'ftype': 'character', 'args': 's',
            'modifier': ', dimension(*), intent(in) ', 'len': '1'}

    def test_args_1(self):
        assert re.compile(_ARGS, re.VERBOSE).match("(s)")

    def test_bind_1(self):
        assert re.compile(_BIND, re.VERBOSE).match("bind(c,name='pstr')")

    def test_subr_1(self):
        assert _SUBROUTINE.match("subroutine pstr(s) bind(c,name='pstr')")

    def test_subr_2(self):
        i_data = """
subroutine pstr(s) bind(c,name='pstr')
  use iso_c_binding
  character(kind=c_char,len=1), intent(in) :: s(*)
end subroutine pstr
"""
        exp = (
            "#ifndef _H\n#define _H\n\n#ifdef __cplusplus\nextern " '"C" '
            "{\n#endif /* __cplusplus */\n\n/*\n  pstr\n  Generated from "
            "FORTRAN routine 'pstr'\n  FORTRAN declaration:\n      "
            "subroutine pstr(s) bind(c,name='pstr')\n */\nextern void "
            'pstr(const char* s);\n\n\n#ifdef __cplusplus\n} /* extern '
            '"C" */\n#endif /* __cplusplus '
            "*/\n\n#endif /* _H */")

        i_data = (i for i in i_data.split("\n"))
        data = Fortran2CHeader(i_data, d_opt(), 'test')
        data.parse()
        res = StringIO()
        data.gen_output(res, 'test')
        res = res.getvalue()
        for i, j in zip(
                res[res.find("#ifndef _H"):].split("\n"), exp.split("\n")):
            assert i == j


# Local Variables:
# mode: python
# ispell-local-dictionary: "english"
# compile-command: "python setup.py build"
# End:
