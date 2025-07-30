#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Feb 10 2025.

@author: npappin-wsu
@license: MIT

Updated on Feb 11 2025.
"""

from . import logger
import json, pathlib

from requests_ratelimiter import LimiterSession # type: ignore


def get_session(apiKey, username, cache=False):
    session = LimiterSession(max_retries=3, per_minute=10)
    session.headers.update({"User-Agent": "python-bdc"})
    session.headers.update({"hash_value": apiKey})
    session.headers.update({"username": username})
    logger.debug(session.headers)
    logger.info("Session created.")
    return session


def get_metadata():
    from . import session

    logger.info("Collecting metadata...")
    r = session.get("https://broadbandmap.fcc.gov/api/public/map/listAsOfDates")
    logger.debug(r.json())
    parsed = json.loads(r.text)
    logger.info(parsed)
    logger.debug(parsed["data"])
    logger.info("Metadata collected.")
    types = set([item["data_type"] for item in parsed["data"]])
    metadata = {}
    for t in types:
        if t not in metadata.keys():
            metadata[t] = list()
        for item in parsed["data"]:
            if item["data_type"] == t:
                logger.debug(f"Data type: {t}")
                logger.debug(item)
                metadata[t].append(item["as_of_date"])
    return metadata

class bdcCache:
    def check(filename):
        if pathlib.Path('cache', f'{filename}.zip').exists():
            return True
        else:
            return False
        
    def save(filename, data):
        if not pathlib.Path('cache').exists():
            pathlib.Path('cache').mkdir(parents=True, exist_ok=True)
        with open(pathlib.Path('cache', f'{filename}.zip'), 'wb')as f:
            f.write(data)
        pass
    
    def get(filename):
        with open(pathlib.Path('cache', f'{filename}.zip'), 'rb') as f:
            return f.read()

# Detect if parameter is empty. This is a placeholder for future implementation.
# This function should be implemented to check if a parameter is empty or not.
def isEmpty(item):
    # TODO: Implement is empty detection.
    return False