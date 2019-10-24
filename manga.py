from bs4 import BeautifulSoup
from re import search, sub
from os import makedirs
from os.path import dirname, exists, isfile, getsize
from sys import getfilesystemencoding
from urllib.request import build_opener
from urllib.error import HTTPError
from threading import Thread, Lock, Semaphore
from queue import Queue
from json import load, dump
from collections import MutableMapping, namedtuple
from time import sleep
from gzip import decompress

encoding = getfilesystemencoding()

filesystemLock = Lock()

# max number of simultaneous web requests
max_workers = Semaphore(value=4)

def ensure_dir(f):
    with filesystemLock:
        d = dirname(f)
        if not exists(d):
            makedirs(d)

CHARS = '0123456789abcdefghijklmnopqrstuvwxyz'

def decode(cypher, strs):
    return ''.join(strs[CHARS.index(c)] if c in CHARS and strs[CHARS.index(c)] else c for c in cypher)

Option = namedtuple('Option', ['text', 'value'])

index_file = {}
index_filename = None

def update(filename):
    global index_filename
    index_filename = filename
    with open(filename, "r") as f:
        current_site = None
        for l in f.readlines():
            l = l[:-1].strip()
            if len(l) == 0 or l.startswith("#"):
                continue
            elif l.startswith(">"):
                current_site = sub(r'[\'", ]', '', l[1:].strip())
                index_file[current_site] = []
            else:
                index_file[current_site].append(sub(r'[\'", ]', '', l.strip()))
    for k, v in index_file.items():
        for s in v:
            tmp = series(k, s)
            tmp.start()
            tmp.join()

def comment(site, title):
    if not index_filename:
        return False
    total = ''
    with open(index_filename, "r") as f:
        current_site = None
        for l in f.readlines():
            old_l = l[:-1]
            l = l[:-1].strip()
            if l.startswith(">"):
                current_site = sub(r'[\'", ]', '', l[1:].strip())
            elif not l.startswith("#"):
                tmp_title = sub(r'[\'", ]', '', l.strip())
                if title == tmp_title and current_site == site:
                    indent = search(r'(\s*).+', old_l).group(1)
                    total += "%s# %s - Completed.\n" % (indent, sub(r'[\'", ]', '', l.strip()))
                    continue
            total += "%s\n" % old_l
    with open(index_filename, "w") as f:
        f.write(total)

class JSONDict(MutableMapping):
    """
    A JSONDict is a dictionary that automatically saves itself when modified.
    Used to automatically save changes to the cache/index.
    """

    def new(self):
        self.store = dict()
        with open(self.filename, 'w') as f:
            dump(self.store, f)

    def __init__(self, filename, reindex=False):
        self.filename = filename
        ensure_dir(self.filename)
        if reindex:
            self.new()
            return
        try:
            with open(self.filename, 'r') as f:
                self.store = load(f)
        except:
            self.new()

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        self.store[key] = value
        with open(self.filename, 'w') as f:
            dump(self.store, f)

    def __delitem__(self, key):
        del self.store[key]
        with open(self.filename, 'w') as f:
            dump(self.store, f)

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

# Stores series that are no longer being serialized and are completely downloaded.
main_index = JSONDict('./index.json')

def repeat_urlopen(my_str, url=None, attempts=5):
    """
    Repeatedly tries to open the specified URL.
    After 5 failed attempts it will raise an exception.
    """
    with max_workers:
        for i in range(attempts):
            try:
                # Build up a user-agent header to spoof as a normal browser
                opener = build_opener()
                opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36')]
                if url:
                    opener.addheaders = [('Referer', url)]
                tmp = opener.open(my_str)
                if not tmp:
                    return None
                else:
                    if tmp.info().get('Content-Encoding') == 'gzip':
                        return decompress(tmp.read())
                    return tmp.read()
            except HTTPError as e:
                if e.code == 401:
                    print(my_str, e, 'Skipping.')
                    break
                print(my_str, e)
                sleep(10)
            except Exception as e:
                print(my_str, e)
                sleep(10)
        raise Exception('Unable to resolve URL (%s) after %d attempts.' % (my_str, attempts))

class series(Thread):
    def __init__(self, site, title, sort=True, digits=3, workers=5, reindex=False):
        """
        site: specifies the root url for the manga on a site

        title: specifes the 'directory' for a particular manga on the site

        sort: specifies whether or not to download the chapters in order

        digits: specifies the length of the zero-padded chapter and page

            e.g.: digits=3 filenames would look something like '000.000'

            digits=3 handles 0-999 chapters,
            one 'extra chapter' digit,
            and 0-99 pages per chapter

            e.g.: Nisekoi c105.5 p.2 would have the filename '105.502'
                           ^^^-----------------------chapter--^^^
                               ^---------------------extra chptr--^
                                   ^-----------------page number---^^

                  Nisekoi c122 p.12 would be '122.012'
                           ^^^-------chapter--^^^
                              ^------extra(none)--^
                                 ^^--page number---^^

        workers: specifies the maximum number of simultaneous file downloads

        """
        Thread.__init__(self)
        self.sort = sort
        self.site = site
        tmp = site[site.index('//')+2:]
        self.site_root = tmp[:tmp.index('/')]
        self.title = title
        self.digits = digits
        self.reindex = reindex
        self.q = Queue()
        self.workers = []
        for i in range(workers):
            t = Thread(target=self.work_page)
            t.daemon = True
            self.workers.append(t)
            t.start()
        self.index = JSONDict('./%s/index.json' % self.title, self.reindex)

    def clean_link(self, link):
        if link.startswith("//"):
            link = "http:" + link
        if not link.startswith("http"):
            link = "http://" + self.site_root + link
        return link

    def get_chapters(self):
        try:
            my_str = '%s/%s/' % (self.site, self.title)
            soup = BeautifulSoup(repeat_urlopen(my_str), 'html.parser')
        except:
            my_str = '%s/%s' % (self.site, self.title)
            soup = BeautifulSoup(repeat_urlopen(my_str), 'html.parser')
        links = soup.find_all('a')
        all_chapters = set()
        self.completed = False
        try:
            status_li = soup.find("ul", { "class": "detail_topText" }).find_all("li")
            for li in status_li:
                status_label = li.find("label")
                if not status_label:
                    continue
                if 'Status' in status_label.getText() and 'Completed' in li.getText():
                    self.completed = True
                    break
        except Exception as e:
            pass
        for l in links:
            try:
                l = self.clean_link(l['href'])
                if '.' in l and self.title in l and search(r'.*?c?([0-9]+(\.[0-9]+)?)/([0-9]+(\.html)?)?$', l):
                    all_chapters.add(l)
            except:
                continue
        return all_chapters

    def work_chapter(self, my_str):
        search_str = self.title
        prefix = search(r'(.*?c?[0-9]+(\.[0-9]+)?/)([0-9]+(\.html)?)?$', my_str).group(1)
        ch_search = search(search_str + r'.*?c?([0-9]+(\.([0-9]+))?)/([0-9]+(\.html)?)?$', my_str)
        if ch_search is None:
            print('Error:', search_str, my_str)
            return
        c = ch_search.group(1)
        if ch_search.group(2):
            c = int(ch_search.group(1)[:-len(ch_search.group(2))])
        else:
            c = int(c)
        self.padded_chapter = '0' * (self.digits - len(str(c))) + str(c)
        self.extra_chapter_add = 0
        self.extra_chapter = 0
        if ch_search.group(3):
            self.extra_chapter = int(ch_search.group(3))
            self.extra_chapter_add = 10**(self.digits-1) * self.extra_chapter
        index_key = str(c) + '.' + str(self.extra_chapter)
        if index_key in self.index and self.index[index_key]:
            return
        # TODO: What about case when page is 404 or something?
        soup = BeautifulSoup(repeat_urlopen(my_str), 'html.parser')
        for script_tag in soup.find_all('script'):
            contents = script_tag.decode_contents()
            if 'chapterid' in contents:
                comicid = search(r'var comicid *= *(\d+);', contents).group(1)
                chapterid = search(r'var chapterid *= *(\d+);', contents).group(1)
                imagecount = int(search(r'var imagecount *= *(\d+);', contents).group(1))
                print('comicid =', comicid,
                      '; chapterid =', chapterid,
                      '; imagecount =', imagecount)
        dm5_key = soup.find("input", {"id": "dm5_key"})['value']
        self.failure_list = list()
        for i in range(1, imagecount+1):
            fun = my_str.split('1.html')[0] + 'chapterfun.ashx?cid=%s&page=%s&key=%s' % (chapterid, i, dm5_key)
            fun_data = repeat_urlopen(fun, my_str).decode('UTF-8')
            print(fun_data)
            strings = search(r".+'(.+)'\.split", fun_data).group(1).split('|')
            part1 = search(r'{\d .=\"(.+?)\"', fun_data).group(1)
            part2 = search(r';\d .=\[\"(.+?)\"', fun_data).group(1)
            image_url = 'http:' + decode(part1, strings) + decode(part2, strings)
            self.q.put([image_url, i, my_str])
        self.q.join()
        if imagecount > 0 and len(self.failure_list) == 0:
            self.index[index_key] = True

    def work_page(self):
        while True:
            o = self.q.get()
            image_url = o[0]
            p = int(o[1]) + self.extra_chapter_add
            referer_url = o[2]
            print(o)
            padded_page = '0' * (self.digits - len(str(p))) + str(p)
            filename = './%s/%s.%s.jpg' % (self.title, self.padded_chapter, padded_page)
            ensure_dir(filename)
            if not isfile(filename) or getsize(filename) < 100:
                print(self.title, self.padded_chapter, padded_page)
                try:
                    bytes_to_write = repeat_urlopen(image_url, referer_url)
                    with open(filename, 'wb') as f:
                        f.write(bytes_to_write)
                except:
                    self.failure_list.append(o[1])
                    print('Unable to download %s.' % filename)
            self.q.task_done()

    def sorted(self, c):
        if self.sort:
            return sorted(c)
        return c

    def run(self):
        print('**************** starting %s ****************' % self.title)
        chapters = self.get_chapters()
        for c in self.sorted(chapters):
            self.work_chapter(c)
        if self.completed:
            with filesystemLock:
                main_index[self.title] = True
                print('%s is a completed work.'% self.title)
                if self.site in index_file and self.title in index_file[self.site]:
                    comment(self.site, self.title)
        print('**************** %s finished ****************' % self.title)
