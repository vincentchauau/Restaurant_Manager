"""
Utility functions for Restaurant Dummy
"""

import logging
import os
from datetime import datetime, timedelta
import json


def setup_logging(enable_logging=True):
    """Setup logging configuration"""
    if enable_logging:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        logging.disable(logging.CRITICAL)


def log_message(message):
    """Log a message with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")
    logging.info(message)


def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:.2f}"


def format_hours(hours):
    """Format hours with 2 decimal places"""
    return f"{hours:.2f}h"


def parse_date(date_string):
    """Parse date string in various formats"""
    formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y%m%d']
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt).date()
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_string}")


def parse_time(time_string):
    """Parse time string in various formats"""
    formats = ['%H:%M:%S', '%H:%M', '%I:%M:%S %p', '%I:%M %p']
    
    for fmt in formats:
        try:
            return datetime.strptime(time_string, fmt).time()
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse time: {time_string}")


def get_date_range(start_date, end_date):
    """Generate list of dates between start and end dates"""
    current_date = start_date
    dates = []
    
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    
    return dates


def validate_employee_id(employee_id):
    """Validate employee ID format"""
    if not employee_id:
        return False
    
    # Simple validation - should start with EMP and have 3 digits
    if employee_id.startswith('EMP') and len(employee_id) == 6:
        try:
            int(employee_id[3:])  # Check if last 3 characters are digits
            return True
        except ValueError:
            pass
    
    return False


def safe_float(value, default=0.0):
    """Safely convert value to float"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0):
    """Safely convert value to int"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def load_json_file(file_path):
    """Load JSON data from file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        log_message(f"Error loading JSON file {file_path}: {e}")
        return None


def save_json_file(data, file_path):
    """Save data to JSON file"""
    try:
        # Ensure directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        log_message(f"Error saving JSON file {file_path}: {e}")
        return False


def generate_report_filename(report_type, restaurant_name=None):
    """Generate standardized report filename"""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    if restaurant_name:
        clean_name = restaurant_name.lower().replace(' ', '-').replace('&', 'and')
        return f"{clean_name}-{report_type}-{timestamp}.json"
    else:
        return f"{report_type}-{timestamp}.json"


def calculate_percentage(part, total):
    """Calculate percentage with safe division"""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)


def get_business_hours():
    """Get standard business hours"""
    return {
        'open_time': '09:00',
        'close_time': '23:00',
        'timezone': 'Australia/Melbourne'
    }


def is_business_hours(check_time):
    """Check if time is within business hours"""
    business_hours = get_business_hours()
    open_time = datetime.strptime(business_hours['open_time'], '%H:%M').time()
    close_time = datetime.strptime(business_hours['close_time'], '%H:%M').time()
    
    return open_time <= check_time <= close_time


class DataValidator:
    """Data validation utilities"""
    
    @staticmethod
    def validate_pos_record(record):
        """Validate POS record structure"""
        required_fields = ['sale_date', 'sale_time', 'item_name', 'quantity', 'unit_price']
        errors = []
        
        for field in required_fields:
            if field not in record or record[field] is None:
                errors.append(f"Missing required field: {field}")
        
        if 'quantity' in record and record['quantity'] <= 0:
            errors.append("Quantity must be positive")
        
        if 'unit_price' in record and record['unit_price'] < 0:
            errors.append("Unit price cannot be negative")
        
        return errors
    
    @staticmethod
    def validate_roster_record(record):
        """Validate roster record structure"""
        required_fields = ['employee_id', 'employee_name', 'shift_date', 'start_time', 'end_time']
        errors = []
        
        for field in required_fields:
            if field not in record or record[field] is None:
                errors.append(f"Missing required field: {field}")
        
        if 'worked_hours' in record and record['worked_hours'] < 0:
            errors.append("Worked hours cannot be negative")
        
        if 'hourly_rate' in record and record['hourly_rate'] < 0:
            errors.append("Hourly rate cannot be negative")
        
        return errors


def create_sample_data_files(output_dir):
    """Create sample data files for testing"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Sample POS data
    pos_data = [
        {
            'sale_date': '2024-01-15',
            'sale_time': '12:30:00',
            'item_name': 'Burger Deluxe',
            'item_category': 'Main',
            'quantity': 1,
            'unit_price': 18.50,
            'total_amount': 18.50,
            'employee_id': 'EMP001'
        },
        {
            'sale_date': '2024-01-15',
            'sale_time': '12:35:00',
            'item_name': 'Cappuccino',
            'item_category': 'Beverage',
            'quantity': 2,
            'unit_price': 4.50,
            'total_amount': 9.00,
            'employee_id': 'EMP003'
        }
    ]
    
    # Sample roster data
    roster_data = [
        {
            'employee_id': 'EMP001',
            'employee_name': 'Alice Johnson',
            'shift_date': '2024-01-15',
            'start_time': '09:00:00',
            'end_time': '17:00:00',
            'worked_hours': 8.0,
            'hourly_rate': 28.50,
            'total_cost': 228.00,
            'position': 'Manager'
        },
        {
            'employee_id': 'EMP003',
            'employee_name': 'Carol Davis',
            'shift_date': '2024-01-15',
            'start_time': '11:00:00',
            'end_time': '19:00:00',
            'worked_hours': 7.5,
            'hourly_rate': 22.50,
            'total_cost': 168.75,
            'position': 'Server'
        }
    ]
    
    # Save sample files
    save_json_file(pos_data, os.path.join(output_dir, 'sample_pos_data.json'))
    save_json_file(roster_data, os.path.join(output_dir, 'sample_roster_data.json'))
    
    log_message(f"Created sample data files in {output_dir}")