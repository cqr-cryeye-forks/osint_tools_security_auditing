import argparse
import codecs
import csv
import json
import pathlib
from typing import Final

import requests
from bs4 import BeautifulSoup


def csv_to_json(csv_file, json_file):
    with open(csv_file, 'r', newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        data = []
        for row in csv_reader:
            data.append(row)

    with open(json_file, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4)


#
# Searches the Common Crawl Index for a domain.
#
def search_domain(domain):
    record_list = []
    index_list = ["2016-36"]

    print("[*] Trying target domain: %s" % domain)

    for index in index_list:

        print("[*] Trying index %s" % index)

        cc_url = "http://index.commoncrawl.org/CC-MAIN-%s-index?" % index
        cc_url += "url=%s&matchType=domain&output=json" % domain
        print(cc_url)
        response = requests.get(cc_url)

        if response.status_code == 200:

            records = response.content.splitlines()

            for record in records:
                record_list.append(json.loads(record.decode('utf-8')))

            print("[*] Added %d results." % len(records))

    print("[*] Found a total of %d hits." % len(record_list))

    return record_list


#
# Download Page
#
def download_page(url):
    https = 'http://'
    if not url.startswith(https):
        response = requests.get(https + url)
    else:
        response = requests.get(url)
    print(response)

    return response.text


#
# Extract links from the HTML
#
def extract_external_links(html_content, link_list):
    try:
        parser = BeautifulSoup(html_content, 'html.parser')

        links = parser.find_all("a")

        if links:

            for link in links:
                href = link.attrs.get("href")

                if href is not None:

                    if target not in href:
                        if href not in link_list and href.startswith("http"):
                            print("[*] Discovered external link: %s" % href)
                            link_list.append(href)

        return link_list
    except Exception as e:
        print(e)
        pass


def main():
    link_list = []
    record_list = [target]
    for record in record_list:
        html_content = download_page(record)

        print("[*] Retrieved %d bytes for %s" % (len(html_content), record))

        link_list = extract_external_links(html_content.encode('ascii', 'ignore'), link_list)

    print("[*] Total external links discovered: %d" % len(link_list))

    with codecs.open("data.csv", "w", encoding="utf-8") as cf:
        fields = ["URL"]

        logger = csv.DictWriter(cf, fieldnames=fields)
        logger.writeheader()

        for link in link_list:
            logger.writerow({"URL": link})

        search_domain_list = search_domain(target) or []
        for link in search_domain_list:
            logger.writerow({"URL": link['url']})

    csv_to_json(output_csv, output_json)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", help="The domain to target ie. cnn.com")
    parser.add_argument('--output', help='output file data.json.')

    args = parser.parse_args()

    if args.domain is None or args.output is None:
        parser.error('You need write two args: -d/--domain и -o/--output')

    target: str = args.domain
    output: str = args.output

    PATH_TO_OUTPUT_DIR: Final[pathlib.Path] = pathlib.Path(__file__).parent
    output_json = PATH_TO_OUTPUT_DIR / output
    json_csv = output[:-4] + "csv"
    output_csv = PATH_TO_OUTPUT_DIR / json_csv
    # list of available indices
    # http://index.commoncrawl.org

    # # #
    main()
    # # #
