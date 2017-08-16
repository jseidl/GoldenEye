# GoldenEye 

GoldenEye is an python app for SECURITY TESTING PURPOSES ONLY!

GoldenEye is a HTTP DoS Test Tool. 

Attack Vector exploited: HTTP Keep Alive + NoCache

## Usage

     USAGE: ./goldeneye.py <url> [OPTIONS]
    
     OPTIONS:
        Flag           Description                     Default
        -u, --useragents   File with user-agents to use                     (default: randomly generated)
        -w, --workers      Number of concurrent workers                     (default: 50)
        -s, --sockets      Number of concurrent sockets                     (default: 30)
        -m, --method       HTTP Method to use 'get' or 'post'  or 'random'  (default: get)
        -d, --debug        Enable Debug Mode [more verbose output]          (default: False)
        -n, --nosslcheck   Do not verify SSL Certificate                    (default: True)
        -h, --help         Shows this help


## Utilities
* util/getuas.py - Fetchs user-agent lists from http://www.useragentstring.com/pages/useragentstring.php subpages (ex: ./getuas.py http://www.useragentstring.com/pages/Browserlist/) *REQUIRES BEAUTIFULSOUP4*
* res/lists/useragents - Text lists (one per line) of User-Agent strings (from http://www.useragentstring.com)

## Changelog
* 2016-02-06  Added support for not verifying SSL Certificates
* 2014-02-20  Added randomly created user agents (still RFC compliant). 
* 2014-02-19  Removed silly referers and user agents. Improved randomness of referers. Added external user-agent list support.
* 2013-03-26  Changed from threading to multiprocessing. Still has some bugs to resolve like I still don't know how to propperly shutdown the manager.
* 2012-12-09  Initial release

## To-do
* Change from getopt to argparse
* Change from string.format() to printf-like

## License
This software is distributed under the GNU General Public License version 3 (GPLv3)

## LEGAL NOTICE
THIS SOFTWARE IS PROVIDED FOR EDUCATIONAL USE ONLY! IF YOU ENGAGE IN ANY ILLEGAL ACTIVITY THE AUTHOR DOES NOT TAKE ANY RESPONSIBILITY FOR IT. BY USING THIS SOFTWARE YOU AGREE WITH THESE TERMS.
