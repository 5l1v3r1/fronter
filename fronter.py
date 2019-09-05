#!/usr/bin/python3
# fronter.py 
# Written by Sanjiv Kawa / @kawabungah

from argparse import ArgumentParser
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import sys

# This function has been shamelessly stolen from l0gan's domainCat. It's chill, we're friends. Available here: https://github.com/l0gan/domainCat/
def checkIBMxForce(domain):
    s = requests.Session()
    # Hack to prevent cert warnings
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    useragent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0'
    try:
        url = 'https://exchange.xforce.ibmcloud.com/api/url/{}'.format(domain)
        headers = {
            'User-Agent': useragent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-GB,en;q=0.5',
            'x-ui': 'XFE',
            'Referer': "https://exchange.xforce.ibmcloud.com/url/{}".format(domain),
            'Connection': 'close'
        }
        response = s.get(url, headers=headers, verify=False, timeout=3)

        if response.status_code == 404:
            return "(Unknown)"

        responseJson = json.loads(response.text)

        return ("({})".format(" | ".join(responseJson["result"].get('cats', {}).keys())))
    
    except Exception as e:            
        return "(Unknown)"

parser = ArgumentParser(description='Find Frontable Domains')
parser.add_argument('--domain', '-d', required=True, help='Your CDN endpoint')
parser.add_argument('--file', '-f', required=True, help='File containing domain names')

args = parser.parse_args()
filepath = args.file
hostHeader = args.domain

fileHandler = open (filepath, "r")
lines = fileHandler.readlines()
fileHandler.close()
        
print("[+] CDN Endpoint: " + hostHeader + "\n")
for domain in lines:
    domain = domain.strip()
    categorization = checkIBMxForce(domain)
    categorizationFormatted = categorization.replace(" ","-").replace("|","")
    try:
        requests.get("https://" + domain + "/fronter-" + domain + "-" + categorizationFormatted, headers={'Host': hostHeader})
        print("[+] Testing: " + domain + " " + categorization)
    except:
        print("[!] Testing: " + domain)
        continue

print('\n[+] Done!\nLogin to VPS and find your frontable domains\ncat /var/log/apache2/access.log | grep python-requests | awk -F"fronter-" {\'print $2\'} | cut -d " " -f 1 | sort -u')
