# Restaurant Dummy - Simplified Restaurant Data Management

A simplified version of the fonda-datagator project for basic restaurant data operations.

## Structure

```
restaurant_dummy/
├── README.md
├── requirements.txt
├── config/
│   └── restaurant_config.json
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── pos_data.py
│   ├── roster_data.py
│   └── utils.py
├── data/
│   └── sample/
└── tests/
    └── test_basic.py
```

## Features

- Simple POS data management
- Basic roster/timesheet handling  
- SQLite database for local development
- JSON configuration
- Basic reporting

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure settings in `config/restaurant_config.json`

3. Run the application:
   ```bash
   python src/main.py
   ```

## Usage

- Process POS sales data
- Manage employee rosters
- Generate basic reports
- Export data to CSV/JSON