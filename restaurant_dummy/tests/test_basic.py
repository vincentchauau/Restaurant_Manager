"""
Basic tests for Restaurant Dummy
"""

import unittest
import os
import sys
import tempfile
import shutil
from datetime import datetime, date, time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import Database
from pos_data import POSManager
from roster_data import RosterManager
from utils import parse_date, parse_time, validate_employee_id, safe_float


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'path': os.path.join(self.temp_dir, 'test.db')
        }
        self.db = Database(self.config)
        self.db.setup_tables()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_table_creation(self):
        """Test that tables are created successfully"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['pos_sales', 'roster_data', 'employees']
            for table in expected_tables:
                self.assertIn(table, tables)
    
    def test_insert_pos_sale(self):
        """Test POS sale insertion"""
        sale_data = {
            'sale_date': date(2024, 1, 15),
            'sale_time': time(12, 30),
            'item_name': 'Test Burger',
            'item_category': 'Main',
            'quantity': 1,
            'unit_price': 15.50,
            'total_amount': 15.50,
            'employee_id': 'EMP001'
        }
        
        sale_id = self.db.insert_pos_sale(sale_data)
        self.assertIsNotNone(sale_id)
        self.assertGreater(sale_id, 0)
    
    def test_insert_roster_record(self):
        """Test roster record insertion"""
        roster_data = {
            'employee_id': 'EMP001',
            'employee_name': 'Test Employee',
            'shift_date': date(2024, 1, 15),
            'start_time': time(9, 0),
            'end_time': time(17, 0),
            'worked_hours': 8.0,
            'hourly_rate': 25.00,
            'total_cost': 200.00,
            'position': 'Server'
        }
        
        roster_id = self.db.insert_roster_record(roster_data)
        self.assertIsNotNone(roster_id)
        self.assertGreater(roster_id, 0)
    
    def test_sales_summary(self):
        """Test sales summary calculation"""
        # Insert test data
        sale_data = {
            'sale_date': date.today(),
            'sale_time': time(12, 30),
            'item_name': 'Test Item',
            'quantity': 2,
            'unit_price': 10.00,
            'total_amount': 20.00
        }
        self.db.insert_pos_sale(sale_data)
        
        summary = self.db.get_sales_summary(days=1)
        self.assertEqual(summary['total_transactions'], 1)
        self.assertEqual(summary['total_revenue'], 20.00)


class TestPOSManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'database': {'path': os.path.join(self.temp_dir, 'test.db')},
            'restaurant': {'name': 'Test Restaurant'}
        }
        self.db = Database(self.config['database'])
        self.db.setup_tables()
        self.pos_manager = POSManager(self.db, self.config)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_menu_items_loaded(self):
        """Test that menu items are loaded"""
        self.assertGreater(len(self.pos_manager.menu_items), 0)
        
        # Check structure of first item
        first_item = self.pos_manager.menu_items[0]
        self.assertIn('name', first_item)
        self.assertIn('category', first_item)
        self.assertIn('price', first_item)
    
    def test_generate_transaction(self):
        """Test transaction generation"""
        test_date = date(2024, 1, 15)
        transaction = self.pos_manager._generate_transaction(test_date)
        
        self.assertEqual(transaction['sale_date'], test_date)
        self.assertIn('sale_time', transaction)
        self.assertIn('item_name', transaction)
        self.assertGreater(transaction['quantity'], 0)
        self.assertGreater(transaction['unit_price'], 0)
        self.assertEqual(
            transaction['total_amount'],
            transaction['quantity'] * transaction['unit_price']
        )


class TestRosterManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'database': {'path': os.path.join(self.temp_dir, 'test.db')},
            'restaurant': {'name': 'Test Restaurant'}
        }
        self.db = Database(self.config['database'])
        self.db.setup_tables()
        self.roster_manager = RosterManager(self.db, self.config)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_employees_loaded(self):
        """Test that employees are loaded"""
        self.assertGreater(len(self.roster_manager.employees), 0)
        
        # Check structure of first employee
        first_emp = self.roster_manager.employees[0]
        self.assertIn('id', first_emp)
        self.assertIn('name', first_emp)
        self.assertIn('position', first_emp)
        self.assertIn('hourly_rate', first_emp)
    
    def test_calculate_worked_hours(self):
        """Test worked hours calculation"""
        start_time = time(9, 0, 0)
        end_time = time(17, 30, 0)
        
        hours = self.roster_manager.calculate_worked_hours(start_time, end_time)
        self.assertEqual(hours, 8.5)
    
    def test_calculate_worked_hours_with_breaks(self):
        """Test worked hours calculation with meal breaks"""
        start_time = time(9, 0, 0)
        end_time = time(17, 30, 0)
        meal_breaks = [{'duration': 30}]  # 30 minutes
        
        hours = self.roster_manager.calculate_worked_hours(start_time, end_time, meal_breaks)
        self.assertEqual(hours, 8.0)  # 8.5 - 0.5 = 8.0


class TestUtils(unittest.TestCase):
    def test_parse_date(self):
        """Test date parsing"""
        self.assertEqual(parse_date('2024-01-15'), date(2024, 1, 15))
        self.assertEqual(parse_date('15/01/2024'), date(2024, 1, 15))
        self.assertEqual(parse_date('01/15/2024'), date(2024, 1, 15))
    
    def test_parse_time(self):
        """Test time parsing"""
        self.assertEqual(parse_time('14:30:00'), time(14, 30, 0))
        self.assertEqual(parse_time('14:30'), time(14, 30, 0))
        self.assertEqual(parse_time('2:30 PM'), time(14, 30, 0))
    
    def test_validate_employee_id(self):
        """Test employee ID validation"""
        self.assertTrue(validate_employee_id('EMP001'))
        self.assertTrue(validate_employee_id('EMP999'))
        self.assertFalse(validate_employee_id('EMP1'))
        self.assertFalse(validate_employee_id('E001'))
        self.assertFalse(validate_employee_id(''))
        self.assertFalse(validate_employee_id(None))
    
    def test_safe_float(self):
        """Test safe float conversion"""
        self.assertEqual(safe_float('15.50'), 15.50)
        self.assertEqual(safe_float('invalid', 0.0), 0.0)
        self.assertEqual(safe_float(None, -1.0), -1.0)
        self.assertEqual(safe_float(25), 25.0)


if __name__ == '__main__':
    unittest.main()