from bs4 import BeautifulSoup
from re import search
from os import makedirs
from os.path import dirname, exists, isfile, getsize
from sys import getfilesystemencoding
from urllib.request import urlopen
from threading import Thread, Lock
from queue import Queue

encoding = getfilesystemencoding()

filesystemLock = Lock()

def ensure_dir(f):
    with filesystemLock:
        d = dirname(f)
        if not exists(d):
            makedirs(d)

class Option():
    def __init__(self, text, value):
        self.text = text
        self.value = value

class series(Thread):
    def __init__(self, site, title, sort=True, digits=3, workers=5):
        """
        site specifies the root url for the manga on a site

        title specifes the 'directory' for a particular manga on the site

        sort specifies whether or not to download the chapters in order

        digits specifies the length of the zero-padded chapter and page

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

        workers specifies the maximum number of simultaneous file downloads

        """
        Thread.__init__(self)
        self.sort = sort
        self.site = site
        self.title = title
        self.digits = digits
        self.q = Queue()
        self.workers = []
        for i in range(workers):
            t = Thread(target=self.work_page)
            t.setDaemon(True)
            self.workers.append(t)
            t.start()

    def get_chapters(self):
        my_str = self.site + '/' + self.title + '/'
        page = urlopen(my_str)
        soup = BeautifulSoup(page.read())
        links = soup.find_all('a')
        all_chapters = set()
        for l in links:
            try:
                if search(my_str + r'.*?c?([0-9]+(\.[0-9]+)?)/([0-9]+)?', l['href']):
                    all_chapters.add(l['href'])
            except:
                continue
        return all_chapters

    def work_chapter(self, my_str):
        search_str = self.site + '/' + self.title
        prefix = search(search_str + r'.*?c?[0-9]+(\.[0-9]+)?/', my_str).group(0)
        ch_search = search(search_str + r'.*?c?([0-9]+(\.([0-9]+))?)/([0-9]+)?', my_str)
        c = ch_search.group(1)
        if ch_search.group(2):
            c = ch_search.group(1)[:-len(ch_search.group(2))]
        self.padded_chapter = '0' * (self.digits - len(str(c))) + str(c)
        self.extra_chapter_add = 0
        if ch_search.group(3):
            self.extra_chapter_add = 10**(self.digits-1) * int(ch_search.group(3))
        page = urlopen(my_str)
        soup = BeautifulSoup(page.read())
        opts = soup.find_all('option')
        all_opts = set()
        opts_list = list()
        for o in opts:
            all_opts.add(Option(o.text, o.get("value")))
        for o in all_opts:
            s = search(search_str + r'.*?c?[0-9]+/([0-9]+)?', o.value)
            if not s:
                if o.text and search(r'#?[0-9]+\Z', o.text) and search(r'\A[0-9]+\Z', o.value):
                    opts_list.append([prefix + o.value, o.value])
            elif s.group(1):
                opts_list.append([o.value, s.group(1)])
            else:
                opts_list.append([o.value, 1])
        for o in opts_list:
            self.q.put(o)
        self.q.join()

    def work_page(self):
        while True:
            o = self.q.get()
            p = int(o[1]) + self.extra_chapter_add
            padded_page = '0' * (self.digits - len(str(p))) + str(p)
            filename = './' + self.title + '/' + self.padded_chapter + '.' + padded_page + '.jpg'
            ensure_dir(filename)
            if not isfile(filename) or getsize(filename) < 100:
                print(self.title, self.padded_chapter, padded_page)
                page = urlopen(o[0])
                if not page:
                    continue
                soup = BeautifulSoup(page.read())
                ids = ('image', 'picture')
                for i in ids:
                    image = soup.find('img',{'id':i})
                    if image:
                        break
                if not image:
                    continue
                image_url = image['src']
                if 'http://' not in image_url:
                     image_url = self.site + image_url
                with open(filename,'wb') as f:
                    f.write(urlopen(image_url).read())
            self.q.task_done()

    def sorted(self, c):
        if self.sort:
            return sorted(c)
        return c

    def run(self):
        print('**************** starting ' + self.title + ' ****************')
        chapters = self.get_chapters()
        for c in self.sorted(chapters):
            self.work_chapter(c)
        print('**************** ' + self.title + ' finished ****************')
