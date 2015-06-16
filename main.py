#!/usr/bin/python
import manga
from os import chdir
from os.path import realpath, dirname

# Switch the current working directory to directory this file is in
chdir(realpath(dirname(__file__)))

manga.update('index.txt')
