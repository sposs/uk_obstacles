# -*- coding: utf-8 -*-
"""
© 2012 - 2021 Xample SA

Author: Candas Kuran
Date: 13.06.23
"""
import tempfile
import re
from typing import List, Union

import xlrd
from bs4 import BeautifulSoup


class Obstacle(object):
    """
    Container class (incomplete) to be used for temporary obstacle storage.
    """
    def __init__(self):
        super().__init__()


def is_xls(href: str) -> bool:
    """
    Helper util for BeautifulSoup
    """
    if "VFR_Obstacles" in href and "xls" in href:
        return True
    else:
        return False


def download_file() -> str:
    """
    Download a file to a temporary directory
    :return: path to file
    """
    url = "https://download.airnavigation.aero/python/obstacles/"
    return


def parse_coord(coord: str) -> Union[float, None]:
    """
    Helper method to populate the Obstacle objects.
    The data file contains coordinates in a 'bad' format. Our DB needs to have numbers (floats).
    latitudes and longitudes are stored using this pattern : "DDMMSS.SS[NS]" for lat and "DDDMMSS.SS[EW]" for lon.
    North leads to positive latitudes, East is also positive for longitudes
    South is negative, and so is West.
    :param coord: a coordinate as string
    :return: float or None
    """
    return


def get_items(path: str) -> List[Obstacle]:
    """
    Extract some Obstacles from the provided local path
    :param path: input path to the local copy of the file.
    """
    return


def create_table(conn):
    """Create the table structure given the SQlite connection"""
    return


def save_objects(items: List[Obstacle], file_name: str) -> str:
    """
    Given a list of Obstacles, we store the data inside a SQlite file. The file to be created inside a temp directory
    1. create the temp directory
    2. create a connection to the file in the directory
    3. Create the table structure
    4. Populate the table
    5. Return the full path
    :param items: list of Obstacles
    :param file_name: output filename
    :return: the full path to the created output file
    """
    return



