GoldenEye 
================

GoldenEye is an python app for SECURITY TESTING PURPOSES ONLY!

GoldenEye is a HTTP DoS Test Tool. 

Attack Vector exploited: HTTP Keep Alive + NoCache

Usage
-----------------------------------------------------------------------------------------------------------
 USAGE: ./goldeneye.py <url> [OPTIONS]

 OPTIONS:
     Flag           Description                     Default
     -t, --threads      Number of concurrent threads                (default: 500)
     -m, --method       HTTP Method to use 'get' or 'post'  or 'random'         (default: get)
     -d, --debug        Enable Debug Mode [more verbose output]         (default: False)
     -h, --help     Shows this help
