#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Feb 10 2025.

@author: npappin-wsu
@license: MIT

Updated on May 14 2025.
"""

from . import logger, session, metadata, bdcCache
import pandas as pd
import json, zipfile, io
from pprint import pprint
from .helpers import isEmpty

# from . import config


class availability:
    """
    A class to retrieve broadband availability data for specified states, technologies, and release dates.
    """

    def fixed(
        states: int | str | list = "53",
        technology: int | str | list = "50",
        release: str | list = "2024-06-30",
        cache: bool = False,
    ) -> pd.DataFrame:
        """
        Retrieves broadband availability data for specified states, technologies, and release dates.

        Args:
            states (int | str | list, optional): State FIPS code(s) to filter by.
                Can be a single value, a list of values, or "all" to include all states. Defaults to "53".
            technology (int | str | list, optional): Technology code(s) to filter by.
                Can be a single value, a list of values, "all" to include all technologies,
                "fixed" for fixed technologies, or "mobile" for mobile technologies. Defaults to "50".
            release (str | list, optional): Release date(s) to filter by. Can be a single value or a list of values. Defaults to "2024-06-30".
            cache (bool, optional): Whether to use caching for downloaded files. Defaults to False.

        Raises:
            Exception: If one or more parameters are empty.
            Exception: If availability data retrieval fails for a specific release.
            Exception: If availability data retrieval fails for a specific state, technology, or release.

        Returns:
            pd.DataFrame: A DataFrame containing the filtered broadband availability data.
        """
        logger.info("Collecting availability...")
        logger.debug(f"State: {states}")
        logger.debug(f"Technology: {technology}")
        logger.debug(f"Release: {release}")

        # TODO: Add empty detection here
        if isEmpty(states) or isEmpty(technology) or isEmpty(release):
            raise Exception("One or more parameters are empty.")

        # Normalization code
        if type(states) is not list:
            states = [states]
        if type(technology) is not list:
            technology = [technology]
        if type(release) is not list:
            release = [release]
        technology = [str(t) for t in technology]
        states = [str(s) for s in states]

        # Retrieve availability data
        availability = dict()
        for r in release:
            response = session.get(
                f"https://broadbandmap.fcc.gov/api/public/map/downloads/listAvailabilityData/{r}"
            )
            if response.status_code != 200:
                logger.error(f"Failed to retrieve availability data for {r}.")
                raise Exception(f"Failed to retrieve availability data for {r}.")
            # TODO: adding dtype hints here I think would be helpful.
            availability[r] = pd.DataFrame.from_dict(response.json()["data"])
        if "all" in states:
            states = availability[r].state_fips.drop_duplicates().dropna().tolist()
        if "all" in technology:
            technology = (
                availability[r].technology_code.drop_duplicates().dropna().tolist()
            )
        elif "fixed" in technology:
            technology = (
                availability[r][
                    (
                        (availability[r].subcategory == "Location Coverage")
                        & (availability[r].provider_id.isnull())
                    )
                ]
                .technology_code.drop_duplicates()
                .dropna()
                .tolist()
            )
            technology = [t for t in technology if int(t) < 100]
        elif "mobile" in technology:
            technology = (
                availability[r][
                    (
                        (availability[r].subcategory == "Location Coverage")
                        & (availability[r].provider_id.isnull())
                    )
                ]
                .technology_code.drop_duplicates()
                .dropna()
                .tolist()
            )
            technology = [t for t in technology if int(t) >= 100]

        df = pd.DataFrame()
        columnHints = {
            "frn": str,
            "provider_id": "UInt32",
            "brand_name": str,
            "location_id": "UInt32",
            "technology": "UInt16",
            "max_advertised_download_speed": "UInt32",
            "max_advertised_upload_speed": "UInt32",
            "low_latency": "boolean",
            "business_residental_code": "category",
            "state_usps": "category",
            "block_geoid": str,
            "h3_res8_id": str,
        }

        if len(release) * len(states) * len(technology) > 100:
            logger.warning(
                f"Retrieving {len(release) * len(states) * len(technology)} records. This may take a while... or crash."
            )

        for r in release:
            rlocal = availability[r]
            items = rlocal[
                (rlocal.category == "State")
                & (rlocal.state_fips.isin(states))
                & (rlocal.technology_code.isin(technology))
            ].to_dict("records")
            for item in items:
                logger.debug(
                    f"State: {item['state_name']}({item})), Technology: {item['technology_code']}, Release: {r}"
                )
                # FUCK I DONT LIKE THIS
                if cache and bdcCache.check(item["file_name"]):
                    data = bdcCache.get(item["file_name"])
                    logger.debug("Cache hit!")
                    pass
                else:
                    response = session.get(
                        f"https://broadbandmap.fcc.gov/api/public/map/downloads/downloadFile/availability/{item['file_id']}"
                    )
                    if response.status_code == 200 and cache:
                        bdcCache.save(item["file_name"], response.content)
                    data = response.content
                if response.status_code != 200:
                    logger.error(
                        f"Failed to retrieve availability data for {item['state_name']} and {item['technology_code']} in {r}."
                    )
                    raise Exception(
                        f"Failed to retrieve availability data for {item['state_name']} and {item['technology_code']} in {r}."
                    )
                else:
                    zip = zipfile.ZipFile(io.BytesIO(data))
                    localdf = pd.read_csv(
                        zip.open(zip.filelist[0].filename),
                        dtype=columnHints,
                        dtype_backend="pyarrow",
                    )
                    df = pd.concat([df, localdf], ignore_index=True)
                logger.info(
                    f"df memory size (hinted): {df.memory_usage(deep=True).sum()/1000000} MB"
                )
                logger.info(f"df shape: {df.shape}")
        logger.debug(f"State: {states}, Technology: {technology}, Release: {release}")
        return df


def echo(message):
    logger.info(message)
    print(message)
    pass


def main():
    logger.info("Starting the application...")
    # Your code here


if __name__ == "__main__":
    main()
