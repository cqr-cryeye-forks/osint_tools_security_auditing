#!/usr/bin/env python3.5
# coding=UTF-8

from typing import Final
import argparse
import json
import pathlib
import pygeoip


class Geoip:
    def __init__(self, target):
        self.target = target
        self.gip = pygeoip.GeoIP(PATH_TO_OUTPUT_DIR / 'GeoLiteCity.dat', pygeoip.MEMORY_CACHE)
        self.search()

    def search(self):
        addr = self.target
        rec = self.gip.record_by_addr(addr)
        return rec


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Geo localizate IP addresses')

    parser.add_argument('--target', help='domain or url')
    parser.add_argument('--output', help='output file data.json')

    args = parser.parse_args()

    if args.target is None or args.output is None:
        parser.error('You need write two args: --target и --output')

    target: str = args.target
    output: str = args.output

    PATH_TO_OUTPUT_DIR: Final[pathlib.Path] = pathlib.Path(__file__).parent
    output_json = PATH_TO_OUTPUT_DIR / output

    geoip = Geoip(target)
    data = geoip.search()
    with open(output_json, "w") as jf:
        json.dump(data, jf, indent=4)
