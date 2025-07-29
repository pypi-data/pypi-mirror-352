### functional_programming
from datetime import datetime, timedelta
from typing import Union, List
from functools import partial

def parse_date_format(date_str: str) -> tuple[str, bool]:
   """Determine the format of date string"""
   return ('%Y-%m-%d', True) if '-' in date_str else ('%Y%m%d', False)

def validate_dates(start: datetime, end: datetime) -> None:
   """Validate date range"""
   if start > end:
       raise ValueError("Start date must be earlier than or equal to end date")

def convert_date_string_to_datetime(date_input: Union[str, int], date_format: str) -> datetime:
   """Convert input to datetime object"""
   return datetime.strptime(str(date_input), date_format)

map_date_string_to_datetime = convert_date_string_to_datetime

def generate_date_range(start_date: Union[str, int, datetime], end_date: Union[str, int, datetime]) -> List[datetime]:
   """Generate list of datetime objects between two dates
   
   Args:
       start_date: Start date as string, int, or datetime object
       end_date: End date as string, int, or datetime object
       
   Returns:
       List of datetime objects between start and end dates
   """
   # Convert to datetime if not already
   if not isinstance(start_date, datetime):
       start_date = convert_date_string_to_datetime(str(start_date), '%Y-%m-%d')
   if not isinstance(end_date, datetime):
       end_date = convert_date_string_to_datetime(str(end_date), '%Y-%m-%d')
       
   return [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

def convert_datetime_to_date_string(date: datetime, option_dashed: bool) -> str:
   """Convert datetime object to string in specified format"""
   return date.strftime('%Y-%m-%d' if option_dashed else '%Y%m%d')

map_datetime_to_date_string = convert_datetime_to_date_string

def get_all_dates_between_dates(start_date: Union[str, int], end_date: Union[str, int]) -> List[str]:
   """
   Return list of all dates between two dates
   
   Args:
       start_date: Start date (YYYY-MM-DD or YYYYMMDD format)
       end_date: End date (same format as start_date)
   
   Returns:
       List[str]: List of dates from start_date to end_date
   
   Raises:
       ValueError: Invalid date format or start_date later than end_date
   """
   try:
       # 1. Parse date format
       date_format, option_dashed = parse_date_format(str(start_date))
       
       # 2. Convert to datetime objects
       to_datetime = partial(convert_date_string_to_datetime, date_format=date_format)
       start_date_datetime = to_datetime(start_date)
       end_date_datetime = to_datetime(end_date)
       
       # 3. Validate dates
       validate_dates(start_date_datetime, end_date_datetime)
       
       # 4. Generate and format date range
       to_string = partial(convert_datetime_to_date_string, option_dashed=option_dashed)
       
       return list(map(to_string, generate_date_range(start_date_datetime, end_date_datetime)))
       
   except ValueError as e:
       raise ValueError(f"Invalid date format or invalid date range: {str(e)}")