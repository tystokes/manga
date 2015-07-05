# manga

Python 3 tool useful for downloading manga from online manga reader sites.

## What it does

manga.py will scan the base url for all of the chapters of the manga.
It will then spawn threads to work on getting all of the pages downloaded.
Chapters will be downloaded, sorted by url, one at a time.
Pages will be downloaded by a pool of threads with no guaranteed ordering.
Pages will be saved inside a subdirectory of the series' name.
Pages will be named in such a way that sorting by filename should keep the pages in their proper reading order.
manga.py can be exited and rerun at any time with no ill-effects.
Rerun manga.py to keep your manga library up to date.

## Dependencies

Requires beautifulsoup4 module to be installed.

`pip install beautifulsoup4` / `pip3 install beautifulsoup4`

## Running the code

Edit `index.txt` adding in your personal manga reader urls and desired titles.

Beginning a line with `>` denotes a site url.

Beginning a line with `#` denotes a comment.

Whitespace at the beginning of lines is allowed.

Blank lines and commented lines are ignored.

List manga url titles below site url all on separate lines (see index.txt for example).

Run main.py (only supports Python 3.x atm):
```python main.py```
or
```python3 main.py```.

## Features

- Easily maintainable main index file.
- Multithreaded.
- Maintains completion indexes in order to save bandwidth and time.
- Comments out completed works in the index file.

###Supported reader sites

Fully:

- mangahere

Not Yet:

- mangapanda
- mangapark
- senmanga
