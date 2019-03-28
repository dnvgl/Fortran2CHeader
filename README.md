Fortran2CHeader
===============

Python based tool to generate Cython `pxd` and C/C++ header file from
Fortran file using `C_ISO_BINDINGS`. To user from Python `setup.py`
file use

```python
...
from dnvgl.fortran2cheader import Fortran2CHeader

HEADER = Fortran2CHeader(
    data=open(os.path.join('xx.f90')),
    signed_to_unsigned_char=False)
HEADER.parse()
CHEAD_NAME = 'xx.h'
PXD_NAME = 'xx.pxd'
HEADER.gen_output(CHEAD_NAME, PXD_NAME)

...
```

Then use `xx.pxd` in your Cython module.


```
usage: fortran2cheader [-h] [--signed-to-unsigned-char] infile

Generate a C/C++ header file from a Fortran file using C_ISO_BINDINGS.

positional arguments:
  infile                Fortran input file

optional arguments:
  -h, --help            show this help message and exit
  --signed-to-unsigned-char, -s
                        use 'unsigned char' instead for 'signed char' for
                        'c_signed_char'
```
