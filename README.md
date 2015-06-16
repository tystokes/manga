# manga

Python 3 tool useful for downloading manga from online manga reader sites.

## Running the code

Edit `index.txt` adding in your personal manga reader urls and desired titles.

Beginning a line with `>` denotes a site url.

Beginning a line with `#` denotes a comment.

Blank lines are ignored.

List manga url titles below site url all on separate lines.

Run main.py (only supports Python 3.3+ atm):
```python main.py```
or
```python3 main.py```.

##Supported
Fully:

- mangahere

Partial:

- senmanga

Possibly:

- mangapanda
- mangapark

## Features

- Easily maintainable main index file.
- Multithreaded.
- Maintains completion indexes in order to save bandwidth and time.
- Comments out titles that are no longer ongoing.

## What it does

manga.py will scan the base url for all of the chapters of the manga.
It will then spawn threads to work on getting all of the pages downloaded.
Chapters will be downloaded, sorted by url, one at a time.
Pages will be downloaded by a pool of threads with no guaranteed ordering.
Pages will be saved inside a subdirectory of the series' name.
Pages will be named in such a way that sorting by filename should keep the pages in their proper reading order.
manga.py can be exited and rerun at any time with no ill-effects (hopefully)
Rerun manga.py to keep your manga stash up to date.
