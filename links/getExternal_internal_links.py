import argparse
import datetime
import json
import pathlib
import random
import re
import time
from typing import Final

import requests
from bs4 import BeautifulSoup


# Retrieves a list of all Internal links found on a page
def getInternalLinks(bsObj, includeUrl):
    internalLinks = []
    # Finds all links that begin with a "/"
    for link in bsObj.findAll("a", href=re.compile("^(/|.*" + includeUrl + ")")):
        if link.attrs['href'] is not None:
            if link.attrs['href'] not in internalLinks:
                internalLinks.append(link.attrs['href'])
    return internalLinks


# Retrieves a list of all external links found on a page
def getExternalLinks(bsObj, excludeUrl):
    externalLinks = []
    # Finds all links that start with "http" or "www" that do
    # not contain the current URL
    for link in bsObj.findAll("a", href=re.compile("^(http|www)((?!" + excludeUrl + ").)*$")):
        if link.attrs['href'] is not None:
            if link.attrs['href'] not in externalLinks:
                externalLinks.append(link.attrs['href'])
    return externalLinks


def splitAddress(address):
    addressParts = address.replace("http://", "").split("/")
    return addressParts


def crawlExternalLinks(startingPage):
    html = requests.get(startingPage).text
    bsObj = BeautifulSoup(html, "html.parser")
    externalLinks = getExternalLinks(bsObj, splitAddress(startingPage)[0])
    return externalLinks


def crawlInternalLinks(startingPage):
    html = requests.get(startingPage).text
    bsObj = BeautifulSoup(html, "html.parser")
    internalLinks = getInternalLinks(bsObj, splitAddress(startingPage)[0])
    return internalLinks


def crawlSite(startingSite):
    externalLinks = crawlExternalLinks(startingSite)
    internalLinks = crawlInternalLinks(startingSite)
    print("\nExternal links")
    print("-------------------")

    for external in externalLinks:
        print(external)

    print("\nInternal links")
    print("-------------------")
    for internal in internalLinks:
        print(internal)
    data = {
        "externalLinks": externalLinks,
        "internalLinks": internalLinks,
    }
    return data


def main():
    random.seed(time.time())

    parser = argparse.ArgumentParser()
    parser.add_argument('--domain', help='domain to be resolved.')
    parser.add_argument('--output', help='output file data.json.')

    args = parser.parse_args()

    if args.domain is None or args.output is None:
        parser.error('You need write two args: -d/--domain и -o/--output')

    target: str = args.domain
    output: str = args.output

    PATH_TO_OUTPUT_DIR: Final[pathlib.Path] = pathlib.Path(__file__).parent
    output_json = PATH_TO_OUTPUT_DIR / output

    https = "http://"
    if not target.startswith(https):
        target = https + target
    
    data = crawlSite(target)
    
    if data == {}:
        data = {"Error": "Nothing found for your target"}
    print(data)
    with open(output_json, "w") as jf:
        json.dump(data, jf, indent=4)


if __name__ == "__main__":
    main()
