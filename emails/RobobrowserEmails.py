# -*- encoding: utf-8 -*-

import argparse
import re

from robobrowser import RoboBrowser

browser = RoboBrowser()


def get_emails(domain):
    if not domain.startswith("http://"):

        domain = "http://" + domain

        browser.open(domain)

        contents = browser.find_all("a", href=re.compile("[-a-zA-Z0-9._]+@[-a-zA-Z0-9_]+.[a-zA-Z0-9_.]+"))

        for content in contents:
            print(content['href'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gets emails from domain.', prog='get_emails_from_url.py', epilog="",
                                     add_help=False)
    # Adding the main options
    general = parser.add_mutually_exclusive_group(required=True)
    general.add_argument('-d', '--domain', metavar='<domain>', action='store', help='domain to be resolved.')
    args = parser.parse_args()

    get_emails(args.domain)
