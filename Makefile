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

doc:
	$(MAKE) -C doc html

build:
	python setup.py build

IGN = $(shell [ -n "$$(svn propget svn:ignore .)" ] && \
	echo "$$(svn propget svn:ignore .)")
clean:
	[ -n "$(IGN)" ] && $(RM) -r $(IGN) || true
	$(MAKE) -C test clean

TAGS:
	find lib -name \*.py
	( set -e ;							\
	  find lib -name \*.c -o -name \*.h -o -name \*.py -o -name	\
	      \*.pyx -o -name \*.pxi					\
	  | xargs etags )

test:
	true

.PHONY: build
.PHONY: doc

# Local Variables:
# mode: makefile
# compile-command: "make"
# coding: utf-8
# End:
