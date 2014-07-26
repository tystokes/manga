# manga

Tool useful for downloading manga from online manga reader sites.

## what it does

manga.py will scan the base url for all of the chapters of the manga.
It will then spawn threads to work on getting all of the pages downloaded.
Chapters will be downloaded, sorted by url, one at a time.
Pages will be downloaded by a pool of threads with no guaranteed ordering.
Pages will be saved inside a subdirectory of the series' name.
Pages will be named in such a way that sorting by filename should keep the pages in their proper reading order.
manga.py can be exited and rerun at any time with no ill-effects (hopefully)
Rerun manga.py to keep your manga stash up to date.

## running the code

Edit main.py, which contains an example use-case.
Then simply run main.py
