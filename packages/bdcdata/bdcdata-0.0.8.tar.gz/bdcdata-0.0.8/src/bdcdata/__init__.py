#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Feb 10 2025.

@author: npappin-wsu
@license: MIT

Updated on Feb 11 2025.
"""

import logging
import os
from dotenv import load_dotenv # type: ignore

load_dotenv()

apiKey = os.getenv("BDC_API_KEY")
username = os.getenv("BDC_USERNAME")

# print(apiKey)

# Configure logging
logging.basicConfig(
    filename="bdc.log", filemode="a", format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# print(logger)

from .helpers import get_session

session = get_session(apiKey, username)

from .helpers import get_metadata, bdcCache

metadata = get_metadata()

from .bdc import *
