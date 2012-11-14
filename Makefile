# Copyright (C) 2012 by Germanischer Lloyd SE

# ======================================================================
# Task      "Central Command" for building and testing Fortran2CHeader
# ----------------------------------------------------------------------
# Author    Berthold Höllmann <hoel@GL-group.com>
# Project   Fortran2CHeader
# ======================================================================

# ID: $Id$

SHELL = /bin/sh

all:	build
	@echo "nothing to do"

test: build
	make -C test test

doc:
	$(MAKE) -C doc html

%_test:
	make -C test $@

%:
	make -C test $@

build:
	python setup.py build

IGN = $(shell [ -n "$$(svn propget svn:ignore .)" ] && echo "$$(svn propget svn:ignore .)")
clean:
	[ -n "$(IGN)" ] && $(RM) -r $(IGN) || true
	$(MAKE) -C test clean

TAGS:
	find src -name \*.py
	( set -e ;										\
          find src -name \*.c -o -name \*.h -o -name \*.py -o -name \*.pyx -o -name \*.pxi 	\
	  | xargs etags )

.PHONY: build
.PHONY: doc
.PHONY: test

# Local Variables:
# mode:makefile
# mode:flyspell
# ispell-local-dictionary:"en"
# compile-command:"make"
# coding:utf-8
# End:
