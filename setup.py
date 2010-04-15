#! /usr/bin/env python
# -*- coding: utf-8 -*-

u"""
Install the fortran2cheader tool.

:author: `Berthold Hoellmann <hoel@GL-group.com>`__
:newfield project: Project
:project: Fortran2CHeader
:copyright: Copyright (C) 2010 by Germanischer Lloyd AG"""

#  ID: $Id$
__date__      = u"$Date$"[5:-1]
__version__   = "$Revision$"[10:-1]
__docformat__ = "restructuredtext en"

from distutils.core import setup

setup(name='Fortran2CHeader',
      version='0.1',
      package_dir = {'': 'lib'},
      py_modules = ['fortran2cheader'],
      scripts=['app/fortran2cheader'],
      )

# Local Variables:
# mode:python
# mode:flyspell
# compile-command:"python setup.py build"
# End:
