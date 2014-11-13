#!/usr/bin/python
import manga
from os import chdir
from os.path import realpath, dirname

# Switch the current working directory to directory this file is in
chdir(realpath(dirname(__file__)))

"""
This is my particular main file. Please, edit it to fit your needs.

Note: I read both raw and translated manga so
I have two different sites to download from
"""

# I download from mangahere.co often:

# The 'root url' for mangahere's manga
mangahere = 'http://www.mangahere.co/manga'

# List of url_endings corresponding to a particular series:
manga_list = ['nisekoi_komi_naoshi', 'onepunch_man']

for m in manga_list:
    # The manga.series class is a Thread so it must be '.start()'ed.
    s = manga.series(mangahere, m)
    s.start()
    # Multiple Threads can be running simultaneously
    # s.join()
    # If you would like to only download one series at a time uncomment s.join()
    # this will make it so it waits for the thread to finish before continuing

# And similarly for senmanga's raw scans:

senmanga = 'http://raw.senmanga.com' # The 'root url' for raws @ senmanga
raw_list = ['Nisekoi']
for r in raw_list:
    manga.series(senmanga, r).start()

# I have tuned the algorithm to work for both mangahere and senmanga
# Other sites may work, but are not tested for.
# Support for other sites (like those below) are in the works

"""
mangapanda = 'http://www.mangapanda.com'
panda_list = ['tetsugaku-letra']
for p in panda_list:
    manga.series(mangapanda, p).start()
"""
"""
mangapark = 'http://v2012.mangapark.com'
park_list = ['Death-Note']
for p in park_list:
    manga.series(mangapark, p).start()
"""
