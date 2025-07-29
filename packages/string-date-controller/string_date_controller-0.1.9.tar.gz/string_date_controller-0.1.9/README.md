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
