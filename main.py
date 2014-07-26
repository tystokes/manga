#!/usr/bin/python
import manga

"""
This is my particular main file. Please, edit it to fit your needs.

Note: I read both raw and translated manga so
I have two different sites to download from
"""

# I download from mangahere.co often:

# The 'root url' for mangahere's manga
mangahere = 'http://www.mangahere.co/manga'
manga_list = ['oukoku_game', 'minamoto_kun_monogatari', 'sankarea',
    'nisekoi_komi_naoshi', 'noblesse', 'kimi_no_iru_machi',
    'the_breaker_new_waves', 'shokugeki_no_soma', 'noragami',
    'tora_kiss_a_school_odyssey', 'ao_no_exorcist', 'ore_monogatari',
    'onepunch_man']
for m in manga_list:
    # The manga.series class is a Thread so it must be '.start()'ed.
    s = manga.series(mangahere, m)
    s.start()
    # Multiple Threads can be running simultaneously
    # s.join()
    # If you would like to only download one series at a time uncomment s.join()
    # this will make it so it waits for the thread to finish before continuing

# And similarly for another manga reader site that has raw scans:

# The 'root url' for senmanga
senmanga = 'http://raw.senmanga.com'
raw_list = ['Nisekoi']
for r in raw_list:
    manga.series(senmanga, r).start()

# I have tuned the algorithm to work for both mangahere and senmanga
# Other sites may work as well but have not been tested
