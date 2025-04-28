import unittest
from unittest.mock import patch, MagicMock
import sqlite3
import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import fetch_all_launches, format_countdown

#simple db tests -- mock db? 
class TestFetchAllLaunches(unittest.TestCase):
    
    @patch('sqlite3.connect')
    def test_fetch_all_launches(self, mock_connect):
        
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        
        mock_cursor.fetchall.return_value = [
            (1, 101, "Starlink",  "url1", "2025-12-01T10:00:00Z", "Falcon 9", "SpaceX"),
            (2, 102, "Flight Test",  "url2", "2025-12-02T12:00:00Z", "Starship", "Spacex")
        ]
        
        launches = fetch_all_launches()
        
        self.assertEqual(len(launches), 2)
        self.assertEqual(launches[0][2], "Starlink")
        self.assertEqual(launches[1][5], "Starship")

# time format test -- using regex, also tests for overdue times
class TestFormatCountdown(unittest.TestCase):
    
    def test_format_countdown(self):
        future = (datetime.datetime.now() + datetime.timedelta(days=1)).replace(microsecond=0).isoformat() + "Z"  
        countdown = format_countdown(future)
        self.assertRegex(countdown, r'\d{2}:\d{2}:\d{2}:\d{2}') 
        
        past = (datetime.datetime.now() - datetime.timedelta(days=1)).replace(microsecond=0).isoformat() + "Z" 
        countdown = format_countdown(past)
        self.assertEqual(countdown, "Launched")
        
        invalid = "00:09021, []'"
        countdown = format_countdown(invalid)
        self.assertEqual(countdown, "Unknown")  


if __name__ == '__main__':
    unittest.main()
