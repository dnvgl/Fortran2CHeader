#! /bin/bash

# Copyright © 2017 by DNV GL SE

# Task  : Setting SVN properties.

# Author: Berthold Höllmann <berthold.hoellmann@dnvgl.com>

# ID: $Id: propset.sh 3 2018-01-18 16:15:36Z berhol $
author="$Author $"
date="$Date: 2018-01-18 17:15:36 +0100 (Do, 18 Jan 2018) $"
version="$Revision: 3 $"

set +f

RULE=( \( -wholename ./build -prune
       -o -wholename ./.tox -prune
       -o -wholename ./.svn -prune
       -o -wholename ./.mypy_cache -prune
       -o -wholename ./cbuild -prune
       -o -name .svn -prune
       -o -name \*.egg-info -prune
       -o -wholename ./.venv -prune
       -o -wholename ./.eggs -prune
       -o -wholename ./htmlcov -prune
       -o -wholename ./.cache -prune \)
       -o \( -name \*.org
       -o -name \*.cfg
       -o -name \*.h
       -o -name \*.sh
       -o -name \*.txt
       -o -name \*.svg
       -o -name \*.xml
       -o -name \*.py
       -o -name \*.html
       -o -name \*.in
       -o -name \*.tex
       -o -name \*.csv
       -o -name \*.ses
       -o -name \*.txt
       -o -name \*.ini
       -o -name .isort.cfg \) )

find . "${RULE[@]}" -exec svn propset svn:keywords "Author Date Id Revision" {} \;
find . "${RULE[@]}" -exec svn propset svn:eol-style native {} \;


# Local Variables:
# mode: shell-script
# coding: utf-8
# compile-command: "sh propset.sh"
# End:
