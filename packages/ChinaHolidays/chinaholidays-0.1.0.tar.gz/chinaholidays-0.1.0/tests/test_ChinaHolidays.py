import unittest
from datetime import datetime
from src.ChinaHolidays import (
    get_all_holidays,
    filter_holidays,
    date_range
)

class TestChinaHolidays(unittest.TestCase):
    def test_get_all_holidays(self):
        holidays = get_all_holidays(True, 2025)
        self.assertEqual(len(holidays), 117)

    def test_filter_holidays(self):
        workdays = filter_holidays(datetime(2025, 5, 29), datetime(2025, 6, 3))
        self.assertEqual(len(workdays), 3)

    def test_date_range(self):
        dates = date_range(datetime(2025, 5, 29), datetime(2025, 6, 3))
        self.assertEqual(len(dates), 6)

    def test_date_range_param_error(self):
        with self.assertRaises(ValueError):
            date_range(datetime(2025, 6, 3), datetime(2025, 5, 29))
    
    def test_get_all_holidays_param_error(self):
        with self.assertRaises(ValueError):
            get_all_holidays(year=2023)
        
        with self.assertRaises(ValueError):
            get_all_holidays(year=3000)