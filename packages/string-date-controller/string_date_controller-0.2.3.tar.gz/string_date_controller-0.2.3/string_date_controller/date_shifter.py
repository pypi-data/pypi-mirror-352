from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from shining_pebbles import get_today, get_yesterday

def get_today_dashed():
    return get_today('%Y-%m-%d')

def get_today_nondashed():
    return get_today('%Y%m%d')

def get_yesterday_dashed():
    return get_yesterday('%Y-%m-%d')

def get_yesterday_nondashed():
    return get_yesterday('%Y%m%d')

def get_first_date_of_month(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return f"{date_obj.year}-{str(date_obj.month).zfill(2)}-01"

def get_last_date_of_month(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    if date_obj.month == 12:
        next_month = date(date_obj.year + 1, 1, 1)
    else:
        next_month = date(date_obj.year, date_obj.month + 1, 1)
    last_date = next_month - timedelta(days=1)    
    return f"{last_date.year}-{str(last_date.month).zfill(2)}-{str(last_date.day).zfill(2)}"

def get_last_date_of_previous_month(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')    
    first_date_of_current_month = date(date_obj.year, date_obj.month, 1)    
    last_date_of_previous_month = first_date_of_current_month - timedelta(days=1)    
    return f"{last_date_of_previous_month.year}-{str(last_date_of_previous_month.month).zfill(2)}-{str(last_date_of_previous_month.day).zfill(2)}"

def get_first_date_of_year(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return f"{date_obj.year}-01-01"

def get_last_date_of_year(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return f"{date_obj.year}-12-31"

def get_date_n_years_ago(date_str, n):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    past_date = date_obj - relativedelta(years=n)
    return f"{past_date.year}-{str(past_date.month).zfill(2)}-{str(past_date.day).zfill(2)}"

def get_date_n_months_ago(date_str, n):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')   
    past_date = date_obj - relativedelta(months=n)   
    return f"{past_date.year}-{str(past_date.month).zfill(2)}-{str(past_date.day).zfill(2)}"

def get_date_n_days_ago(date_str, n):
   date_obj = datetime.strptime(date_str, '%Y-%m-%d')   
   past_date = date_obj - timedelta(days=n)   
   return f"{past_date.year}-{str(past_date.month).zfill(2)}-{str(past_date.day).zfill(2)}"

def get_date_n_years_after(date_str, n):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    future_date = date_obj + relativedelta(years=n)
    return f"{future_date.year}-{str(future_date.month).zfill(2)}-{str(future_date.day).zfill(2)}"

def get_date_n_days_after(date_str, n):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')   
    future_date = date_obj + timedelta(days=n)   
    return f"{future_date.year}-{str(future_date.month).zfill(2)}-{str(future_date.day).zfill(2)}"

def get_date_n_months_after(date_str, n):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')   
    future_date = date_obj + relativedelta(months=n)   
    return f"{future_date.year}-{str(future_date.month).zfill(2)}-{str(future_date.day).zfill(2)}"

def get_n_months_ago_last_date(date_ref: str, n: int) -> str:
    return get_last_date_of_month(get_date_n_months_ago(date_ref, n))

def get_n_years_ago_last_date(date_ref: str, n: int) -> str:
    return get_last_date_of_month(get_date_n_years_ago(date_ref, n))

def get_year_first_date_simple(date_ref: str) -> str:
    return date_ref.split('-')[0] + '-01-01'
