#!/usr/bin/env python3
"""
Main application entry point for Restaurant Dummy
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from database import Database
from pos_data import POSManager
from roster_data import RosterManager
from utils import setup_logging, log_message


def load_config():
    """Load configuration from JSON file"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'restaurant_config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description='Restaurant Dummy - Simple Restaurant Data Management')
    parser.add_argument('--action', choices=['pos', 'roster', 'report', 'setup'], 
                       default='setup', help='Action to perform')
    parser.add_argument('--date', help='Date for data operations (YYYY-MM-DD)')
    parser.add_argument('--days', type=int, default=7, help='Number of days to process')
    parser.add_argument('--output', help='Output file path for reports')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    setup_logging(config['settings']['enable_logging'])
    
    # Initialize database
    db = Database(config['database'])
    
    log_message("🍴 Restaurant Dummy started")
    log_message(f"Restaurant: {config['restaurant']['name']}")
    log_message(f"Action: {args.action}")
    
    try:
        if args.action == 'setup':
            setup_database(db, config)
        elif args.action == 'pos':
            process_pos_data(db, config, args)
        elif args.action == 'roster':
            process_roster_data(db, config, args)
        elif args.action == 'report':
            generate_report(db, config, args)
        
        log_message("✅ Operation completed successfully")
        
    except Exception as e:
        log_message(f"❌ Error: {e}")
        return 1
    
    return 0


def setup_database(db, config):
    """Initialize database tables"""
    log_message("Setting up database...")
    db.setup_tables()
    log_message("Database setup complete")


def process_pos_data(db, config, args):
    """Process POS sales data"""
    log_message("Processing POS data...")
    pos_manager = POSManager(db, config)
    
    if args.date:
        target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        pos_manager.process_date(target_date)
    else:
        # Process last N days
        for i in range(args.days):
            target_date = datetime.now().date() - timedelta(days=i)
            pos_manager.process_date(target_date)


def process_roster_data(db, config, args):
    """Process roster/timesheet data"""
    log_message("Processing roster data...")
    roster_manager = RosterManager(db, config)
    
    if args.date:
        target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        roster_manager.process_date(target_date)
    else:
        # Process last N days
        for i in range(args.days):
            target_date = datetime.now().date() - timedelta(days=i)
            roster_manager.process_date(target_date)


def generate_report(db, config, args):
    """Generate reports"""
    log_message("Generating reports...")
    
    # Simple sales report
    sales_data = db.get_sales_summary(args.days)
    roster_data = db.get_roster_summary(args.days)
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'restaurant': config['restaurant']['name'],
        'period_days': args.days,
        'sales_summary': sales_data,
        'roster_summary': roster_data
    }
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        log_message(f"Report saved to {args.output}")
    else:
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    exit(main())