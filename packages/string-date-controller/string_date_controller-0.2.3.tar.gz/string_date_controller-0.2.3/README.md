# String Date Controller

A Python module for string date manipulation and formatting operations.

## Features

- Date shifting: Easily shift dates forward or backward
- Date formatting: Convert dates between different formats
- Date cropping: Crop dates to specific time periods
- Date generation: Generate date sequences and ranges
- Date extraction: Extract dates from file names and folders
- Historical dates collection: Dynamically collect reference dates for timeseries analysis

## Version History

### v0.2.3 (2025-06-04)
- Added yearly_dates_collector module for YTD date pair operations
- Implemented functions to get YTD date pairs based on reference date or specific year
- Optimized get_year_first_date_simple function for better performance
- Added support for retrieving all existing years from date list

### v0.2.2 (2025-06-04)
- Added get_last_date_of_year function to date_shifter module
- Enhanced date manipulation capabilities for year-end operations

### v0.2.1 (2025-06-03)
- Added monthly date pairs collection for time series analysis
- Implemented functions to get month-end dates and their previous month-end dates
- Added support for nested dictionary structure for year/month organization
- Included month name mapping constants

### v0.2.0 (2025-06-02)
- Major refactoring of historical dates collection functionality
- Improved logging configuration for better application integration
- Added functional approach using reduce for combining historical dates
- Enhanced month filtering to focus on 1, 3, 6 month periods
- Renamed functions for better clarity and consistency

### v0.1.10 (2025-06-02)
- Fixed parameter order in historical date functions
- Enhanced readability of output keys (YTD, Since Inception)
- Fixed function call parameter alignment

### v0.1.9 (2025-06-02)
- Improved API flexibility by making date_ref parameter optional with default value
- Standardized parameter order across historical date collection functions

### v0.1.8 (2025-06-02)
- Added historical dates collection functionality for timeseries analysis
- Implemented functions to dynamically collect monthly, yearly, YTD, and inception dates

### v0.1.6 (2025-04-23)
- Fixed dependency version format in requirements.txt

### v0.1.5 (2025-04-23)
- Fixed package deployment issues

### v0.1.4 (2025-04-23)
- Added file folder date extraction functionality
- Improved type handling in date generation functions
- Fixed bugs in date range generation
- Standardized naming conventions (using 'nondashed' consistently)

## Installation

```bash
pip install string-date-controller
```

## Usage

```python
from string_date_controller import date_shifter, date_formatter, date_cropper

# Example usage will be added soon
```

## Requirements

- Python >= 3.11
- shining_pebbles

## License

MIT License

## Author

**June Young Park**  
AI Management Development Team Lead & Quant Strategist at LIFE Asset Management

LIFE Asset Management is a hedge fund management firm that integrates value investing and engagement strategies with quantitative approaches and financial technology, headquartered in Seoul, South Korea.

## Contact

- Email: juneyoungpaak@gmail.com
- Location: TWO IFC, Yeouido, Seoul
