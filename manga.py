import urllib, urllib.request, sys, os
from bs4 import BeautifulSoup
from threading import Thread
from re import search

encoding = sys.getfilesystemencoding()

mangawall = 'http://www.mangahere.co/manga'

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

class series(Thread):
    def __init__(self, title, digits=3):
        Thread.__init__(self)
        self.title = title
        self.digits = digits

    def get_chapters(self):
        my_str = mangawall + '/' + self.title + '/'
        page = urllib.request.urlopen(my_str)
        soup = BeautifulSoup(page.read())
        links = soup.find_all('a')
        all_chapters = set()
        for l in links:
            if search(my_str + r'.*c[0-9]+', l['href']):
                all_chapters.add(l['href'])
        return all_chapters

    def work_chapter(self, my_str):
        search_str = mangawall + '/' + self.title + '/'
        c = search(search_str + r'.*c([0-9]+)', my_str).group(1)
        padded_chapter = '0' * (self.digits - len(str(c))) + str(c)
        page = urllib.request.urlopen(my_str)
        soup = BeautifulSoup(page.read())
        opts = soup.find_all('option')
        all_opts = set()
        opts_list = list()
        for o in opts:
            all_opts.add(o.get("value"))
        for o in all_opts:
            s = search(my_str + r'([0-9]+)\.html', o)
            if s and s.group(1):
                opts_list.append([o, s.group(1)])
            else:
                opts_list.append([o, 1])
        for o in opts_list:
            p = o[1]
            padded_page = '0' * (self.digits - len(str(p))) + str(p)
            filename = './' + self.title + '/' + padded_chapter + '.' + padded_page + '.jpg'
            ensure_dir(filename)
            if not os.path.isfile(filename) or os.path.getsize(filename) < 4000:
                print(self.title, padded_chapter, padded_page)
                page = urllib.request.urlopen(o[0])
                if not page:
                    continue
                soup = BeautifulSoup(page.read())
                image = soup.find('img',{'id':'image'})
                if not image:
                    continue
                with open(filename,'wb') as f:
                    f.write(urllib.request.urlopen(image['src']).read())

    def run(self):
        chapters = self.get_chapters()
        for c in sorted(chapters):
            self.work_chapter(c)
        print('**************** ' + self.title + ' finished ****************')

    def old_algorighm(self):
        for c in range(1,10**self.digits):
            padded_chapter = '0' * (self.digits - len(str(c))) + str(c)
            for p in range(1,10**self.digits):
                padded_page = '0' * (self.digits - len(str(p))) + str(p)
                filename = './' + self.title + '/' + padded_chapter + '.' + padded_page + '.jpg'
                ensure_dir(filename)
                if not os.path.isfile(filename) or os.path.getsize(filename) < 4000:
                    string = mangawall + '/' + self.title + '/c' + padded_chapter + '/' + str(p) + '.html'
                    print(string)
                    page = urllib.request.urlopen(string)
                    if not page:
                        break
                    soup = BeautifulSoup(page.read())
                    image = soup.find('img',{'id':'image'})
                    if not image:
                        if p == 1:
                            return
                        break
                    print(image['src'])
                    with open(filename,'wb') as f:
                        f.write(urllib.request.urlopen(image['src']).read())

manga = ['oukoku_game', 'minamoto_kun_monogatari', 'sankarea',
    'nisekoi_komi_naoshi', 'noblesse', 'kimi_no_iru_machi',
    'the_breaker_new_waves', 'shokugeki_no_soma', 'noragami',
    'tora_kiss_a_school_odyssey']

for m in manga:
    series(m).start()