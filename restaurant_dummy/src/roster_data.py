"""
Roster and timesheet data management
"""

import random
from datetime import datetime, timedelta, time
from utils import log_message


class RosterManager:
    def __init__(self, db, config):
        self.db = db
        self.config = config
        self.employees = self._load_employees()
        self.positions = self._load_positions()
    
    def _load_employees(self):
        """Sample employee data"""
        return [
            {'id': 'EMP001', 'name': 'Alice Johnson', 'position': 'Manager', 'hourly_rate': 28.50},
            {'id': 'EMP002', 'name': 'Bob Smith', 'position': 'Chef', 'hourly_rate': 25.00},
            {'id': 'EMP003', 'name': 'Carol Davis', 'position': 'Server', 'hourly_rate': 22.50},
            {'id': 'EMP004', 'name': 'David Wilson', 'position': 'Server', 'hourly_rate': 22.50},
            {'id': 'EMP005', 'name': 'Emma Brown', 'position': 'Kitchen Hand', 'hourly_rate': 20.00},
            {'id': 'EMP006', 'name': 'Frank Miller', 'position': 'Bartender', 'hourly_rate': 24.00},
            {'id': 'EMP007', 'name': 'Grace Taylor', 'position': 'Server', 'hourly_rate': 22.50},
            {'id': 'EMP008', 'name': 'Henry Lee', 'position': 'Kitchen Hand', 'hourly_rate': 20.00},
        ]
    
    def _load_positions(self):
        """Position configurations"""
        return {
            'Manager': {'min_hours': 7, 'max_hours': 9, 'shifts_per_week': 5},
            'Chef': {'min_hours': 6, 'max_hours': 8, 'shifts_per_week': 5},
            'Server': {'min_hours': 4, 'max_hours': 8, 'shifts_per_week': 4},
            'Kitchen Hand': {'min_hours': 4, 'max_hours': 7, 'shifts_per_week': 4},
            'Bartender': {'min_hours': 5, 'max_hours': 8, 'shifts_per_week': 4},
        }
    
    def setup_employees(self):
        """Initialize employee records in database"""
        for emp in self.employees:
            self.db.insert_employee({
                'employee_id': emp['id'],
                'name': emp['name'],
                'position': emp['position'],
                'hourly_rate': emp['hourly_rate'],
                'active': True
            })
        log_message(f"Setup {len(self.employees)} employee records")
    
    def process_date(self, target_date):
        """Generate sample roster data for a specific date"""
        log_message(f"Processing roster data for {target_date}")
        
        shifts_inserted = 0
        
        # Determine which employees work on this date
        working_employees = self._get_working_employees(target_date)
        
        for emp in working_employees:
            try:
                shift = self._generate_shift(emp, target_date)
                if shift:
                    shift_id = self.db.insert_roster_record(shift)
                    if shift_id:
                        shifts_inserted += 1
            except Exception as e:
                log_message(f"Error inserting shift for {emp['name']}: {e}")
        
        log_message(f"Inserted {shifts_inserted} roster shifts for {target_date}")
        return shifts_inserted
    
    def _get_working_employees(self, date):
        """Determine which employees are scheduled to work on a given date"""
        working = []
        
        for emp in self.employees:
            position_config = self.positions[emp['position']]
            shifts_per_week = position_config['shifts_per_week']
            
            # Simple scheduling logic - some randomness with position-based probability
            if emp['position'] == 'Manager':
                # Manager works most days except random days off
                if random.random() < 0.85:
                    working.append(emp)
            elif date.weekday() < 5:  # Weekday
                # Higher chance for full-time positions
                if emp['position'] in ['Chef', 'Server'] and random.random() < 0.7:
                    working.append(emp)
                elif random.random() < 0.5:
                    working.append(emp)
            else:  # Weekend
                # Different pattern for weekends
                if random.random() < 0.8:
                    working.append(emp)
        
        return working
    
    def _generate_shift(self, employee, shift_date):
        """Generate a realistic shift for an employee"""
        position_config = self.positions[employee['position']]
        
        # Random shift duration within position limits
        min_hours = position_config['min_hours']
        max_hours = position_config['max_hours']
        shift_hours = round(random.uniform(min_hours, max_hours), 2)
        
        # Random start time based on position
        if employee['position'] == 'Manager':
            start_hour = random.randint(8, 11)  # Early start
        elif employee['position'] == 'Chef':
            start_hour = random.randint(9, 12)  # Kitchen prep
        else:
            start_hour = random.randint(10, 15)  # Service staff
        
        start_minute = random.choice([0, 15, 30, 45])  # Quarter-hour increments
        start_time = time(start_hour, start_minute)
        
        # Calculate end time
        start_datetime = datetime.combine(shift_date, start_time)
        end_datetime = start_datetime + timedelta(hours=shift_hours)
        end_time = end_datetime.time()
        
        # Calculate cost
        hourly_rate = employee['hourly_rate']
        total_cost = shift_hours * hourly_rate
        
        return {
            'employee_id': employee['id'],
            'employee_name': employee['name'],
            'shift_date': shift_date,
            'start_time': start_time,
            'end_time': end_time,
            'worked_hours': shift_hours,
            'hourly_rate': hourly_rate,
            'total_cost': total_cost,
            'position': employee['position']
        }
    
    def calculate_worked_hours(self, start_time, end_time, meal_breaks=None):
        """Calculate worked hours accounting for meal breaks"""
        try:
            # Convert times to datetime objects for calculation
            if isinstance(start_time, str):
                start_dt = datetime.strptime(start_time, '%H:%M:%S')
            elif isinstance(start_time, time):
                start_dt = datetime.combine(datetime.today(), start_time)
            else:
                start_dt = start_time
            
            if isinstance(end_time, str):
                end_dt = datetime.strptime(end_time, '%H:%M:%S')
            elif isinstance(end_time, time):
                end_dt = datetime.combine(datetime.today(), end_time)
            else:
                end_dt = end_time
            
            # Handle shifts that cross midnight
            if end_dt < start_dt:
                end_dt += timedelta(days=1)
            
            # Calculate total time
            total_time = end_dt - start_dt
            total_hours = total_time.total_seconds() / 3600
            
            # Subtract meal breaks if provided
            if meal_breaks:
                break_hours = 0
                for break_info in meal_breaks:
                    if 'duration' in break_info:
                        break_hours += break_info['duration'] / 60  # Convert minutes to hours
                
                total_hours -= break_hours
            
            return round(max(0, total_hours), 2)  # Ensure non-negative
            
        except Exception as e:
            log_message(f"Error calculating worked hours: {e}")
            return 0.0
    
    def get_daily_summary(self, date):
        """Get summary of roster for a specific date"""
        shifts = self.db.get_daily_roster(date)
        
        if not shifts:
            return {
                'date': date.isoformat(),
                'total_shifts': 0,
                'total_hours': 0,
                'total_cost': 0,
                'employees_working': 0,
                'position_breakdown': {}
            }
        
        total_shifts = len(shifts)
        total_hours = sum(shift['worked_hours'] for shift in shifts)
        total_cost = sum(shift['total_cost'] or 0 for shift in shifts)
        employees_working = len(set(shift['employee_id'] for shift in shifts))
        
        # Position breakdown
        position_breakdown = {}
        for shift in shifts:
            position = shift['position']
            if position not in position_breakdown:
                position_breakdown[position] = {'shifts': 0, 'hours': 0, 'cost': 0}
            
            position_breakdown[position]['shifts'] += 1
            position_breakdown[position]['hours'] += shift['worked_hours']
            position_breakdown[position]['cost'] += shift['total_cost'] or 0
        
        return {
            'date': date.isoformat(),
            'total_shifts': total_shifts,
            'total_hours': float(total_hours),
            'total_cost': float(total_cost),
            'employees_working': employees_working,
            'avg_hours_per_shift': float(total_hours / total_shifts) if total_shifts > 0 else 0,
            'position_breakdown': position_breakdown
        }
    
    def import_roster_data(self, data_list):
        """Import roster data from external source"""
        imported_count = 0
        
        for record in data_list:
            try:
                # Validate required fields
                required_fields = ['employee_id', 'employee_name', 'shift_date', 'start_time', 'end_time']
                if not all(field in record for field in required_fields):
                    log_message(f"Skipping record - missing required fields: {record}")
                    continue
                
                # Calculate worked hours if not provided
                if 'worked_hours' not in record or not record['worked_hours']:
                    record['worked_hours'] = self.calculate_worked_hours(
                        record['start_time'], 
                        record['end_time'],
                        record.get('meal_breaks')
                    )
                
                # Calculate cost if not provided
                if 'total_cost' not in record and 'hourly_rate' in record:
                    record['total_cost'] = record['worked_hours'] * record['hourly_rate']
                
                shift_id = self.db.insert_roster_record(record)
                if shift_id:
                    imported_count += 1
                
            except Exception as e:
                log_message(f"Error importing roster record: {e}")
        
        log_message(f"Imported {imported_count} roster records")
        return imported_count