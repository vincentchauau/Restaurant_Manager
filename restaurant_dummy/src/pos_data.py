"""
POS (Point of Sale) data management
"""

import random
from datetime import datetime, timedelta, time
from utils import log_message


class POSManager:
    def __init__(self, db, config):
        self.db = db
        self.config = config
        self.menu_items = self._load_menu_items()
    
    def _load_menu_items(self):
        """Sample menu items for demonstration"""
        return [
            {'name': 'Burger Deluxe', 'category': 'Main', 'price': 18.50},
            {'name': 'Chicken Caesar Salad', 'category': 'Salad', 'price': 16.00},
            {'name': 'Fish & Chips', 'category': 'Main', 'price': 22.00},
            {'name': 'Margherita Pizza', 'category': 'Pizza', 'price': 20.00},
            {'name': 'Beef Steak', 'category': 'Main', 'price': 35.00},
            {'name': 'Pasta Carbonara', 'category': 'Pasta', 'price': 19.50},
            {'name': 'Greek Salad', 'category': 'Salad', 'price': 14.50},
            {'name': 'Cappuccino', 'category': 'Beverage', 'price': 4.50},
            {'name': 'Latte', 'category': 'Beverage', 'price': 4.80},
            {'name': 'Fresh Orange Juice', 'category': 'Beverage', 'price': 6.50},
            {'name': 'House Wine (Glass)', 'category': 'Alcohol', 'price': 9.50},
            {'name': 'Beer (Pint)', 'category': 'Alcohol', 'price': 7.50},
            {'name': 'Chocolate Cake', 'category': 'Dessert', 'price': 8.50},
            {'name': 'Ice Cream Sundae', 'category': 'Dessert', 'price': 7.00},
        ]
    
    def process_date(self, target_date):
        """Generate sample POS data for a specific date"""
        log_message(f"Processing POS data for {target_date}")
        
        # Generate realistic number of transactions
        if target_date.weekday() < 5:  # Weekday
            num_transactions = random.randint(80, 120)
        else:  # Weekend
            num_transactions = random.randint(120, 180)
        
        transactions_inserted = 0
        
        for _ in range(num_transactions):
            try:
                transaction = self._generate_transaction(target_date)
                sale_id = self.db.insert_pos_sale(transaction)
                if sale_id:
                    transactions_inserted += 1
            except Exception as e:
                log_message(f"Error inserting transaction: {e}")
        
        log_message(f"Inserted {transactions_inserted} POS transactions for {target_date}")
        return transactions_inserted
    
    def _generate_transaction(self, sale_date):
        """Generate a realistic POS transaction"""
        # Random time during business hours (9 AM to 11 PM)
        hour = random.randint(9, 22)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        sale_time = time(hour, minute, second)
        
        # Random menu item
        item = random.choice(self.menu_items)
        quantity = random.choices([1, 2, 3], weights=[80, 15, 5])[0]  # Most orders are single items
        
        # Random employee (using simple IDs)
        employee_id = f"EMP{random.randint(1, 8):03d}"  # 8 employees
        
        # Calculate totals
        unit_price = item['price']
        total_amount = unit_price * quantity
        
        return {
            'sale_date': sale_date,
            'sale_time': sale_time,
            'item_name': item['name'],
            'item_category': item['category'],
            'quantity': quantity,
            'unit_price': unit_price,
            'total_amount': total_amount,
            'employee_id': employee_id
        }
    
    def get_daily_summary(self, date):
        """Get summary of POS sales for a specific date"""
        sales = self.db.get_daily_sales(date)
        
        if not sales:
            return {
                'date': date.isoformat(),
                'total_transactions': 0,
                'total_revenue': 0,
                'items_sold': 0,
                'top_items': [],
                'hourly_breakdown': {}
            }
        
        total_transactions = len(sales)
        total_revenue = sum(sale['total_amount'] for sale in sales)
        items_sold = sum(sale['quantity'] for sale in sales)
        
        # Top selling items
        item_counts = {}
        for sale in sales:
            item_name = sale['item_name']
            item_counts[item_name] = item_counts.get(item_name, 0) + sale['quantity']
        
        top_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Hourly breakdown
        hourly_breakdown = {}
        for sale in sales:
            hour = datetime.strptime(sale['sale_time'], '%H:%M:%S').hour
            if hour not in hourly_breakdown:
                hourly_breakdown[hour] = {'transactions': 0, 'revenue': 0}
            hourly_breakdown[hour]['transactions'] += 1
            hourly_breakdown[hour]['revenue'] += sale['total_amount']
        
        return {
            'date': date.isoformat(),
            'total_transactions': total_transactions,
            'total_revenue': float(total_revenue),
            'items_sold': items_sold,
            'avg_transaction': float(total_revenue / total_transactions) if total_transactions > 0 else 0,
            'top_items': [{'item': item, 'quantity': qty} for item, qty in top_items],
            'hourly_breakdown': {str(hour): data for hour, data in hourly_breakdown.items()}
        }
    
    def import_pos_data(self, data_list):
        """Import POS data from external source"""
        imported_count = 0
        
        for record in data_list:
            try:
                # Validate required fields
                required_fields = ['sale_date', 'sale_time', 'item_name', 'quantity', 'unit_price']
                if not all(field in record for field in required_fields):
                    log_message(f"Skipping record - missing required fields: {record}")
                    continue
                
                # Calculate total if not provided
                if 'total_amount' not in record:
                    record['total_amount'] = record['quantity'] * record['unit_price']
                
                sale_id = self.db.insert_pos_sale(record)
                if sale_id:
                    imported_count += 1
                
            except Exception as e:
                log_message(f"Error importing POS record: {e}")
        
        log_message(f"Imported {imported_count} POS records")
        return imported_count