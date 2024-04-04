import json
import pathlib
from typing import Final

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
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gets emails from domain.', prog='get_emails_from_url.py', epilog="",
                                     add_help=False)
    # Adding the main options
    parser.add_argument('--domain', help='domain to be resolved.')
    parser.add_argument('--output', help='output file data.json.')
    args = parser.parse_args()

    if args.domain is None or args.output is None:
        parser.error('You need write two args: -d/--domain и -o/--output')

    target: str = args.domain
    output: str = args.output

    PATH_TO_OUTPUT_DIR: Final[pathlib.Path] = pathlib.Path(__file__).parent
    output_json = PATH_TO_OUTPUT_DIR / output

    result = get_emails(target) or []
    if result == []:
        result = [{"Error": "Nothing found for your target"}]
    print(result)
    with open(output_json, "w") as jf:
        json.dump(result, jf, indent=4)
