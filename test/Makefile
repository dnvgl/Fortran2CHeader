# Copyright (C) 2012 by Germanischer Lloyd SE

# ======================================================================
# Task      Tests for Fortran2CHeader
# ----------------------------------------------------------------------
# Author    Berthold Hoellmann <hoel@GL-group.com>
# Project   Fortran2CHeader
# ======================================================================

# ID: $Id$

SHELL = /bin/sh

PYPLAT=$(shell python -c "from distutils import util; print util.get_platform()")
PYVER=$(shell python -c "import sys ; print sys.version[:3]")

USE_COMPILED=0

ifeq ($(USE_COMPILED),1)
  export BASE_PATH=../lib
  BPATH=../build/lib:../build/lib.$(PYPLAT)-$(PYVER)
else
  BPATH=../lib
endif

PYTHON = PYTHONPATH=$(BPATH) python #-v

PYBASE = ../lib
PY = $(shell $(FINDDIR)find $(PYBASE) -name \*.py -not -name .\#\* -and -not -name config.py )
UTESTS = $(subst /,.,$(subst $(PYBASE)/,,$(patsubst %.py,%_test,$(PY))))

ifeq ("$GL_ARCH","")
FINDDIR=/bin/
endif

DTEST = $(subst /,_,$(PY))


TESTS  = $(UTESTS)
TESTS += $(DTESTS)

all:
	@true

test:	py_dep build $(TESTS)

test_all:	test	$(BIG_TESTS)

build:
	make -C .. build

%_test:	%_test.py
	$(PYTHON) $< -v
	touch $@

%_rtest:	%.py	$(PY)	validate_hcm.py
	$(PYTHON) $<
	touch $@

py_dep: gen_py_dep.py $(addsuffix .py,$(UTESTS))
	$(PYTHON) $^ $(PYBASE) > $@

include py_dep

clean:
	-find .. -name \*.pyc | xargs rm
	svn propget svn:ignore | xargs rm -rf
	-find . -type l -and -not -name .\#\* | xargs rm

gen_py_dep.py:
	svn export https://svnsrv.germanlloyd.org/svn/GLPyFramework/trunk/test/gen_py_dep.py

%_test.py:	__generic_test_.py
	[ -f $@ ] || ln -s $< $@

vpath %.py $(shell $(FINDDIR)find ../lib -type d|grep -v .svn)

# Local Variables:
# mode:makefile
# mode:flyspell
# ispell-local-dictionary:"en"
# compile-command:"make"
# coding:utf-8
# End:
