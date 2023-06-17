# -*- coding: utf-8 -*-
"""
© 2012 - 2021 Xample SA

Author: Candas Kuran
Date: 13.06.23
"""
import tempfile
from typing import List, Union

import xlrd
from bs4 import BeautifulSoup
import requests
import sqlite3
import os
from urllib.parse import urljoin



class Obstacle(object):
    """
    Container class (incomplete) to be used for temporary obstacle storage.
    """
    def __init__(self, name: str = None , type: str = None, lat: float = None, lon: float = None, elevation: float = None, height: float = None):
        self._name = name
        self._type = type
        self._lat = lat
        self._lon = lon
        self._elevation = elevation
        self._height = height
        super().__init__()

    @property
    def lat(self):
        return self._lat

    @lat.setter
    def lat(self, value):
        if type(value) == float:
            self._lat = value
        else:
            raise ValueError("La latitude doit être un float")
    
    @property
    def lon(self):
        return self._lon

    @lon.setter
    def lon(self, value):
        if type(value) == float:
            self._lon = value
        else:
            raise ValueError("La longitude doit être un float")
        
    @property
    def elevation(self):
        return self._elevation
    
    @elevation.setter
    def elevation(self, value):
        if type(value) == float:
            self._elevation = value
        else:
            raise ValueError("L'elevation doit etre un float")
        
    
    @property
    def height(self):
        return self._height
    
    @height.setter
    def height(self, value):
        if type(value) == float:
            self._height = value
        else:
            raise ValueError("height doit etre un float")



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
    # file_name = None
    url = "https://download.airnavigation.aero/python/obstacles/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    target_href = "VFR_Obstacles_2023_05_18_CRC_68F19134.xls"

    liens = soup.find_all('a')

    for lien in liens:
        href = lien.get('href')

        if href is None:
            continue

        if not (href.startswith('VFR_Obstacles') and href.endswith('.xls')):
            continue

        file_url = urljoin(url, href)
        file_response = requests.get(file_url)

        temp_dir = tempfile.mkdtemp()
        file_name = os.path.join(temp_dir, os.path.basename(href))

        with open(file_name, 'wb') as file:
            file.write(file_response.content)

        print(f"la fichier a ete telecharcge!, file name: {file_name}")
        return file_name
    
    raise Exception("Aucun fichier correspondant n'a pas été trouvé")



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
    if coord is None or coord[0] == "-":
        return None

    valeur = coord[-1]
    if valeur not in ['N','S','E','W']:
        return None

    decimal_degrees = None
    try:
        if valeur in ['N', 'S'] and len(coord) >= 7:
            degrees = float(coord[0:2])
            minutes = float(coord[2:4])
            seconds = float(coord[4:-1])
        elif valeur in ['E', 'W'] and len(coord) >= 8:
            degrees = float(coord[0:3])
            minutes = float(coord[3:5])
            seconds = float(coord[5:-1])
        else:
            return None

        decimal_degrees = degrees + minutes / 60 + seconds / 3600

        if valeur in ["S", "W"]:
            decimal_degrees *= -1
    except ValueError:
        return None

    return decimal_degrees

     
    


def get_items(path: str) -> List[Obstacle]:
    """
    Extract some Obstacles from the provided local path
    :param path: input path to the local copy of the file.
    """
    workbook = xlrd.open_workbook(path)
    sheet = workbook.sheet_by_name("All")

    column_names = sheet.row_values(0)
    obstacles_list = []
    for row_index in range(1, sheet.nrows):
        row_values = sheet.row_values(row_index)
        #pour séparer les valeurs lat et lon
        coord = row_values[2].split("\n")
        lat = parse_coord(coord[0])
        lon = parse_coord(coord[1])
        # convertion FT => M
        elevation = float(row_values[3].split(" ")[0]) * 0.3048
        height = float(row_values[4].split(" ")[0]) * 0.3048
        obstacle = Obstacle(name=row_values[0], type=row_values[1].split("\n")[0], lat=lat, lon=lon, elevation=elevation, height=height)
        obstacles_list.append(obstacle)
    return obstacles_list
    


def create_table(conn):
    """Create the table structure given the SQlite connection"""
    
    conn = sqlite3.connect("uk_obstacles.db")
    cursor = conn.cursor()

    create_table_query = ("""
        CREATE TABLE IF NOT EXISTS obstacles (
            name TEXT,
            type TEXT,
            lat REAL,
            lon REAL,
            elevation REAL,
            height REAL
        )
    """)
    
    cursor.execute(create_table_query)


    conn.commit()
 

    print(f"La base de donnees a été creer!")

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
        
    temp_dir = tempfile.mkdtemp()

    db_path = os.path.join(temp_dir, file_name)
    
    conn = sqlite3.connect(db_path)

    create_table(conn)
    
    cursor = conn.cursor()


    items_tube = [(item.name, item.type, item.lat, item.lon, item.elevation, item.height)for item in items]
    cursor.executemany("""
            INSERT INTO obstacles (name, type, lat, lon, elevation, height)
            VALUES (?, ?, ?, ?, ?, ?)
            """, items_tube)

    conn.commit()
    

    return db_path






