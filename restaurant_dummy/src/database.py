"""
Database management for Restaurant Dummy
"""

import sqlite3
import os
from datetime import datetime, timedelta
from utils import log_message


class Database:
    def __init__(self, config):
        self.db_path = config['path']
        self.ensure_db_directory()
    
    def ensure_db_directory(self):
        """Ensure the database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def setup_tables(self):
        """Create database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # POS Sales table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pos_sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_date DATE NOT NULL,
                    sale_time TIME NOT NULL,
                    item_name TEXT NOT NULL,
                    item_category TEXT,
                    quantity INTEGER NOT NULL DEFAULT 1,
                    unit_price DECIMAL(10,2) NOT NULL,
                    total_amount DECIMAL(10,2) NOT NULL,
                    employee_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Roster/Timesheet table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roster_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id TEXT NOT NULL,
                    employee_name TEXT NOT NULL,
                    shift_date DATE NOT NULL,
                    start_time TIME NOT NULL,
                    end_time TIME NOT NULL,
                    worked_hours DECIMAL(5,2) NOT NULL,
                    hourly_rate DECIMAL(8,2),
                    total_cost DECIMAL(10,2),
                    position TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Employee master data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    employee_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    position TEXT,
                    hourly_rate DECIMAL(8,2),
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            log_message("Database tables created successfully")
    
    def insert_pos_sale(self, sale_data):
        """Insert a POS sale record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pos_sales (sale_date, sale_time, item_name, item_category, 
                                     quantity, unit_price, total_amount, employee_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sale_data['sale_date'],
                sale_data['sale_time'],
                sale_data['item_name'],
                sale_data.get('item_category'),
                sale_data['quantity'],
                sale_data['unit_price'],
                sale_data['total_amount'],
                sale_data.get('employee_id')
            ))
            conn.commit()
            return cursor.lastrowid
    
    def insert_roster_record(self, roster_data):
        """Insert a roster record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO roster_data (employee_id, employee_name, shift_date, 
                                       start_time, end_time, worked_hours, hourly_rate, 
                                       total_cost, position)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                roster_data['employee_id'],
                roster_data['employee_name'],
                roster_data['shift_date'],
                roster_data['start_time'],
                roster_data['end_time'],
                roster_data['worked_hours'],
                roster_data.get('hourly_rate'),
                roster_data.get('total_cost'),
                roster_data.get('position')
            ))
            conn.commit()
            return cursor.lastrowid
    
    def insert_employee(self, employee_data):
        """Insert or update employee record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO employees (employee_id, name, position, hourly_rate, active)
                VALUES (?, ?, ?, ?, ?)
            """, (
                employee_data['employee_id'],
                employee_data['name'],
                employee_data.get('position'),
                employee_data.get('hourly_rate'),
                employee_data.get('active', True)
            ))
            conn.commit()
    
    def get_sales_summary(self, days=7):
        """Get sales summary for the last N days"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(total_amount) as total_revenue,
                    AVG(total_amount) as avg_transaction,
                    COUNT(DISTINCT sale_date) as active_days,
                    COUNT(DISTINCT employee_id) as active_employees
                FROM pos_sales 
                WHERE sale_date BETWEEN ? AND ?
            """, (start_date, end_date))
            
            result = cursor.fetchone()
            return {
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'total_transactions': result[0] or 0,
                'total_revenue': float(result[1] or 0),
                'avg_transaction': float(result[2] or 0),
                'active_days': result[3] or 0,
                'active_employees': result[4] or 0
            }
    
    def get_roster_summary(self, days=7):
        """Get roster summary for the last N days"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_shifts,
                    SUM(worked_hours) as total_hours,
                    AVG(worked_hours) as avg_hours_per_shift,
                    SUM(total_cost) as total_labor_cost,
                    COUNT(DISTINCT employee_id) as active_employees
                FROM roster_data 
                WHERE shift_date BETWEEN ? AND ?
            """, (start_date, end_date))
            
            result = cursor.fetchone()
            return {
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'total_shifts': result[0] or 0,
                'total_hours': float(result[1] or 0),
                'avg_hours_per_shift': float(result[2] or 0),
                'total_labor_cost': float(result[3] or 0),
                'active_employees': result[4] or 0
            }
    
    def get_daily_sales(self, date):
        """Get sales for a specific date"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM pos_sales 
                WHERE sale_date = ?
                ORDER BY sale_time
            """, (date,))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_daily_roster(self, date):
        """Get roster for a specific date"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM roster_data 
                WHERE shift_date = ?
                ORDER BY start_time
            """, (date,))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]