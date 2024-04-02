#!/usr/bin/env python

import argparse
import json
import logging
import os
import pathlib
import re
from typing import Final

import dns.resolver
import geoip2
import geoip2.database
import requests


def checkIpDetails(query=None):
    """
        Method that obtain ip details:
        {
            "as": "AS8560 1\u00261 Internet AG",
            "city": "",
            "country": "Germany",
            "countryCode": "DE",
            "isp": "1\u00261 Internet AG",
            "lat": 51,
            "lon": 9,
            "org": "1\u00261 Internet AG",
            "query": "217.160.251.126",
            "region": "",
            "regionName": "",
            "status": "success",
            "timezone": "",
            "zip": ""
        }
    """
    try:
        apiURL = "http://ip-api.com/json/" + query

        # Accessing the ip-api.com RESTful API
        data = requests.get(apiURL)

        # Reading the text data onto python structures
        apiData = json.loads(data.text)

        # json structure to be returned
        jsonData = []

        if apiData["status"] == "success":
            for key in apiData:
                value = apiData[key]
                if value != "":
                    aux = {}
                    if key == "city":
                        aux["type"] = "location.city"
                        aux["value"] = value
                        # Appending to the list of results                        
                        jsonData.append(aux)
                    elif key == "country":
                        aux["type"] = "location.country"
                        aux["value"] = value
                        # Adding a new attribute
                        att = {}
                        att["value"] = apiData["countryCode"]
                        att["attributes"] = []
                        aux["attributes"] = [att]
                        # Appending to the list of results
                        jsonData.append(aux)
                    elif key == "isp":
                        aux["type"] = "isp"
                        aux["value"] = value
                        # Appending to the list of results                        
                        jsonData.append(aux)
                    elif key == "lat":
                        aux["type"] = "location.geo"
                        aux["value"] = str(apiData["lat"]) + ", " + str(apiData["lon"])
                        # Appending to the list of results                        
                        jsonData.append(aux)
                    elif key == "region":
                        aux["type"] = "location.province"
                        aux["value"] = value
                        # Adding a new attribute
                        att = {}
                        att["value"] = apiData["regionName"]
                        aux["attributes"] = [att]
                        # Appending to the list of results                        
                        jsonData.append(aux)
                    elif key == "timezone":
                        aux["type"] = "location.timezone"
                        aux["value"] = value
                        # Appending to the list of results                        
                        jsonData.append(aux)
                    elif key == "zip":
                        aux["type"] = "location.postalcode"
                        aux["value"] = value
                        # Appending to the list of results                        
                        jsonData.append(aux)
                    elif key == "query":
                        aux["type"] = "ipv4"
                        aux["value"] = value
                        # Appending to the list of results                        
                        jsonData.append(aux)
        elif jsonData == []:
            jsonData = {"Error": "Invalid value"}
        return jsonData
    except:
        # No information was found, then we return a null entity
        return {"Error": "Invalid value"}


def getGeo(domain):
    ip = ip_resolver(domain)
    response = ''
    if is_ipv4(domain):
        pass
    else:
        if not os.path.exists('GeoLite2-City.mmdb'):
            msg = "[*] GeoLite2-City.mmdb is not found ..."
            logging.error(msg)
        else:
            reader = geoip2.database.Reader('GeoLite2-City.mmdb')
            response = reader.city(ip)

    return response


def is_ipv4(address):
    ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    if re.match(ipv4_pattern, address):
        return True
    else:
        return False


def ip_resolver(domain):
    ip = ''
    c_name = ''
    res = dns.resolver.Resolver()
    res.timeout = 1
    # if is_ipv4(domain):
    #     print("ipv4")
    # else:
    #     print("domain")
    try:
        answers = dns.resolver.resolve(domain)
        ip = str(answers[0]).split(": ")[0]
        c_name = answers.canonical_name
    except Exception as e:
        msg = '[*] No IP Addressed: Timeout, NXDOMAIN, NoAnswer or NoNameservers'
        logging.info(msg)
    return ip


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check IP or Domain details')

    parser.add_argument('-d', '--domain', help='query to be resolved by ip-api.com.')
    parser.add_argument('-o', '--output', help='output file data.json')

    args = parser.parse_args()

    if args.domain is None or args.output is None:
        parser.error('You need write two args: -d/--domain и -o/--output')

    target: str = args.domain
    output: str = args.output

    PATH_TO_OUTPUT_DIR: Final[pathlib.Path] = pathlib.Path(__file__).parent
    output_json = PATH_TO_OUTPUT_DIR / output

    res = checkIpDetails(target)

    try:
        response = getGeo(target)
    except Exception as e:
        response = None

    data = {
        "country": response.country.name if response and response.country else None,
        "city": response.city.name if response and response.city else None,
        "Latitude": response.location.latitude if response and response.location else None,
        "Longitude": response.location.longitude if response and response.location else None,
    }
    with open(output_json, 'w') as json_file:
        result = {
            "result": res,
            **data,
        }
        json.dump(result, json_file, indent=2)
