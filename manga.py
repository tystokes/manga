from bs4 import BeautifulSoup
from re import search
from os import makedirs
from os.path import dirname, exists, isfile, getsize
from sys import getfilesystemencoding
from urllib.request import urlopen
from multiprocessing import Process

encoding = getfilesystemencoding()

def ensure_dir(f):
    d = dirname(f)
    if not exists(d):
        makedirs(d)

class Option():
    def __init__(self, text, value):
        self.text = text
        self.value = value

class series(Process):
    def __init__(self, site, title, sort=True, digits=3):
        Process.__init__(self)
        self.sort = sort
        self.site = site
        self.title = title
        self.digits = digits

    def get_chapters(self):
        my_str = self.site + '/' + self.title + '/'
        page = urlopen(my_str)
        soup = BeautifulSoup(page.read())
        links = soup.find_all('a')
        all_chapters = set()
        for l in links:
            try:
                if search(my_str + r'.*?c?([0-9]+)/([0-9]+)?', l['href']):
                    all_chapters.add(l['href'])
            except:
                continue
        return all_chapters

    def work_chapter(self, my_str):
        search_str = self.site + '/' + self.title
        prefix = search(search_str + r'.*?c?[0-9]+/', my_str).group(0)
        c = search(search_str + r'.*?c?([0-9]+)/([0-9]+)?', my_str).group(1)
        padded_chapter = '0' * (self.digits - len(str(c))) + str(c)
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
            p = o[1]
            padded_page = '0' * (self.digits - len(str(p))) + str(p)
            filename = './' + self.title + '/' + padded_chapter + '.' + padded_page + '.jpg'
            ensure_dir(filename)
            if not isfile(filename) or getsize(filename) < 1000:
                print(self.title, padded_chapter, padded_page)
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

if __name__ == '__main__':
    manga = ['oukoku_game', 'minamoto_kun_monogatari', 'sankarea',
        'nisekoi_komi_naoshi', 'noblesse', 'kimi_no_iru_machi',
        'the_breaker_new_waves', 'shokugeki_no_soma', 'noragami',
        'tora_kiss_a_school_odyssey', 'ao_no_exorcist']

    raws = ['Nisekoi']

    mangahere = 'http://www.mangahere.co/manga'
    for m in manga:
        series(mangahere, m).start()

    senmanga = 'http://raw.senmanga.com'
    for r in raws:
        series(senmanga, r).start()
