#!/usr/bin/env python3.5
# coding=UTF-8

import pygeoip
import os
import sys
import argparse


class Geoip:
    def __init__(self, target):
        self.target = target
        self.gip = pygeoip.GeoIP('ip_map_position/GeoLiteCity.dat', pygeoip.MEMORY_CACHE)
        self.search()

    def search(self):
        addr = self.target
        rec = self.gip.record_by_addr(addr)
        for key, val in rec.items():
            print("%s: %s" % (key, val))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Geo localizate IP addresses')
    parser.add_argument('--target', action="store", dest="target", required=True)
    given_args = parser.parse_args()
    target = given_args.target
    geoip = Geoip(target)
    geoip.search()
