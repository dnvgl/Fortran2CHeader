#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Install the fortran2cheader tool.
"""

from __future__ import (print_function, division, absolute_import)

# ID: $Id$"
__date__ = "$Date$"[6:-1]
__version__ = "$Revision$"[10:-1]
__author__ = "`Berthold Höllmann <berthold.hoellmann@dnvgl.com>`__"
__copyright__ = "Copyright © 2010 by DNV GL SE"

from setuptools import setup, find_packages

if __name__ == '__main__':
    setup(name='Fortran2CHeader',
          version='0.3',
          package_dir = {'': 'lib'},
          packages=find_packages('lib', exclude=[
              "*.__pycache__", "*.__pycache__.*", "__pycache__.*",
              "__pycache__"]),
          use_2to3=True,
          entry_points={
              'console_scripts': [
                  'fortran2cheader = fortran2cheader:main']})

# Local Variables:
# mode: python
# ispell-local-dictionary: "english"
# compile-command: "python setup.py build"
# End:
