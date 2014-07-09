import urllib, urllib.request, sys, os
from bs4 import BeautifulSoup

encoding = sys.getfilesystemencoding()

mangawall = 'http://mangawall.com/manga'

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

def series(title, chapters, pages):
	for c in range(1,chapters+1):
		for p in range(1,pages+1):
			string = mangawall + '/' + title + '/' + str(c) + '/' + str(p)
			print(string)
			page = urllib.request.urlopen(string)
			if not page:
				break
			soup = BeautifulSoup(page.read())

			image = soup.find('img',{'class':'scan'})
			if image:
				print(image['src'])
			else:
				break

			filename = './' + title + '/' + str(c) + "." + str(p) + ".jpg"
			ensure_dir(filename)

			if not os.path.isfile(filename):
				f = open(filename,'wb')
				f.write(urllib.request.urlopen(image['src']).read())
				f.close()

series("kangoku-gakuen", 101, 60)