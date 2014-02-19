#!/usr/bin/env python

import urllib, sys
from bs4 import BeautifulSoup

if len(sys.argv) <= 1:
    print "No URL specified. Please supply a valid http://www.useragentstring.com/ UA list URL"
    sys.exit(1)


ua_url = sys.argv[1]

f = urllib.urlopen(ua_url)

html_doc = f.read()

soup = BeautifulSoup(html_doc)

liste = soup.find(id='liste')

uas = liste.find_all('li')

if len(uas) <= 0:
    print "No UAs Found. Are you on http://www.useragentstring.com/ lists?"
    sys.exit(1)


for ua in uas:
    ua_string = ua.get_text()
    ua_string = ua_string.strip(' \t\n\r')
    print ua_string
