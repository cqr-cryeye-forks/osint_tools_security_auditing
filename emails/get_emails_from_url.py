import requests
import re
import argparse
from validate_email import validate_email


def get_emails(domain):
    response = requests.get(domain)
    text = response.text
    emails = re.findall(r"\w+[a-zA-Z_0-9]+@\w+\.\w+", text)
    emails = set(emails)
    result = []
    for email in emails:
        if validate_email(email):
            result.append({"valid": "exists", "value": str(email)})
        else:
            result.append({"valid": "does not exist", "value": str(email)})
    if not result:
        print("no emails")
    else:
        print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gets emails from domain.', prog='get_emails_from_url.py', epilog="",
                                     add_help=False)
    # Adding the main options
    general = parser.add_mutually_exclusive_group(required=True)
    general.add_argument('-d', '--domain', metavar='<domain>', action='store', help='domain to be resolved.')
    args = parser.parse_args()
    get_emails(args.domain)
