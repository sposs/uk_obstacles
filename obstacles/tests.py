# -*- coding: utf-8 -*-
"""
© 2012 - 2021 Xample SA

Author: stephane
Date: 13.06.23
"""
import os
import sqlite3
from unittest import TestCase

from obstacles.utils import download_file, get_items, parse_coord, save_objects, Obstacle

test_data = os.path.join(os.path.dirname(__file__), "data")


class UKObstaclesTest(TestCase):
    obstacle = None
    obstacles = []

    @classmethod
    def setUpClass(cls) -> None:
        cls.obstacle = Obstacle()
        cls.obstacle.name = "UK29308256F"
        cls.obstacle.type = "ROTATING CRANE, INDUSTRIAL"
        cls.obstacle.lat = 52.48527777777778
        cls.obstacle.lon = -1.9183333333333332
        cls.obstacle.elevation = 254.2032
        cls.obstacle.height = 123.1392
        cls.obstacles = [cls.obstacle]

    def test_download(self):
        path = download_file()
        self.assertIsInstance(path, str)
        self.assertTrue(os.path.exists(path))
        self.assertEqual(os.path.basename(path), "VFR_Obstacles_2023_05_18_CRC_68F19134.xls")
        self.assertEqual(os.stat(path).st_size, 2260992)

    def test_utils(self):
        coords = {  "522907.00N": 52.48527777777778,
                    "0015506.00W": -1.9183333333333332,
                    "532855.00N": 53.481944444444444,
                    "532855N": 53.481944444444444,
                    "532222.28N": 53.37285555555555,
                    "0002811.05E": 0.46973611111111113,
                    "532222N": 53.37277777777778,               
                    "5464343N": None,  
                    "-432532.43E": None,
                    "toto": None
                  }
        for coord, val in coords.items():
            with self.subTest("Parsing %s" % coord):
                res = parse_coord(coord)
                self.assertEqual(res, val)

    def test_read(self):
        items = get_items(os.path.join(test_data, "VFR_Obstacles.xls"))
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 9458)
        first_item = items[0]
        self.assertTrue(hasattr(first_item, "name"))
        self.assertTrue(hasattr(first_item, "lat"))
        self.assertTrue(hasattr(first_item, "lon"))
        self.assertTrue(hasattr(first_item, "type"))
        self.assertTrue(hasattr(first_item, "elevation"))
        self.assertEqual(first_item.name, "UK29308256F")
        self.assertEqual(first_item.lat, 52.48527777777778)
        self.assertEqual(first_item.lon, -1.9183333333333332)
        self.assertEqual(first_item.type, "ROTATING CRANE, INDUSTRIAL")
        self.assertEqual(first_item.elevation, 254.2032)  # meters
        self.assertEqual(first_item.height, 123.1392)  # meters

    def test_store_in_sqlite(self):
        file_name = "uk_obstacles.db"
        os.unlink(os.path.join("temp", "uk_obstacles.db"))
        res = save_objects(self.obstacles, file_name)
        self.assertTrue(os.path.exists(res))
        table_to_use = "obstacles"
        with sqlite3.connect(res) as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM %s;" % table_to_use)
            row = c.fetchone()
            self.assertEqual(row[0], 1)
            c.execute("SELECT name FROM %s;" % table_to_use)
            row = c.fetchone()
            self.assertEqual(row[0], "UK29308256F")
            c.execute("SELECT lat FROM %s;" % table_to_use)
            row = c.fetchone()
            self.assertEqual(row[0], 52.48527777777778)
