#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Install the fortran2cheader tool.
"""

from __future__ import division, print_function, absolute_import

# Standard libraries.
import os
from setuptools import setup, find_packages

# DNV GL libraries.
import dnvgl.setup_utils.version as version

# ID: $Id$"
__date__ = "$Date$"[6:-1]
__version__ = "$Revision$"[10:-1]
__author__ = "`Berthold Höllmann <berthold.hoellmann@dnvgl.com>`__"
__copyright__ = "Copyright © 2010 by DNV GL SE"


INSTALL_REQUIRES = ['DNVGLPyFramework']


VERSION = version.Version("version.txt")
VERSION.write((os.path.join('dnvgl', 'fortran2cheader', '__version__.py'),))


if __name__ == '__main__':
    setup(
        name='Fortran2CHeader',
        version=VERSION(),
        license='Other/Proprietary License',
        author='Berthold Höllmann, DNV GL SE',
        author_email='berthold.hoellmann@dnvgl.com',
        url='http://www.dnvgl.com',
        description='''
Generate a C/C++ header file from a Fortran source file using those
subroutines decorated with Fortran2003 `C_ISO_BINDINGS` `BIND` and
`C_*` types.  `INTERFACE` blocks are ignored to allow direct usage of
C function calls in the `FORTRAN` code.''',
        keywords='DNVGL Framework',
        setup_requires=['tox', 'pytest-runner'],
        install_requires=INSTALL_REQUIRES,
        tests_require=['pytest', 'pytest-cov', 'pytest-pep8', 'packaging'],
        packages=find_packages('.', exclude=[
            "*.__pycache__", "*.__pycache__.*", "__pycache__.*",
            "__pycache__", "flycheck*.py[cd]?"]),
        use_2to3=True,
        entry_points={
            'console_scripts': [
                'fortran2cheader = dnvgl.fortran2cheader:main']})

# Local Variables:
# mode: python
# compile-command: "python setup.py test"
# End:
