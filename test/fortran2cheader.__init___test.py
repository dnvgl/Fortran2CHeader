#! /usr/bin/env python
# -*- coding: utf-8 -*-

u"""
Unit tests for Fortran2CHeader

:author: `Berthold Hoellmann <hoel@GL-group.com>`__
:newfield project: Project
:project: Fortran2CHeader
:copyright: Copyright (C) 2012 by Germanischer Lloyd SE
"""

# ID: $Id$
__date__ = u"$Date$"[6:-1]
__version__ = "$Revision$"[10:-1]
__docformat__ = "restructuredtext en"

import doctest
import unittest

import fortran2cheader


class Test(unittest.TestCase):
    """
Testing the fortran2cheader module.
"""

    def setUp(self):
        pass

if __name__ == '__main__':

    doctest.set_unittest_reportflags(doctest.REPORT_CDIFF)

    SUITE = unittest.TestSuite()
    SUITE.addTest(doctest.DocTestSuite(fortran2cheader))

    RUNNER = unittest.TextTestRunner()
    RUNRES = RUNNER.run(SUITE)
    if RUNRES.errors or RUNRES.failures:
        raise Exception("failed test occured")

    unittest.main()


#Local Variables:
#mode:python
#mode:flyspell
#ispell-local-dictionary:"en"
#compile-command:"python setup.py build"
#End:
