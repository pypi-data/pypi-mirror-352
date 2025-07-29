from datetime import datetime
import calendar
import logging
from .date_shifter import (
    get_n_months_ago_last_date, 
    get_n_years_ago_last_date, 
    get_date_n_months_ago, 
    get_date_n_years_ago
)


logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def is_month_end(date_ref):
    """Check if given date is the last day of the month"""
    if isinstance(date_ref, str):
        target_date = datetime.strptime(date_ref, '%Y-%m-%d').date()
    elif isinstance(date_ref, datetime):
        target_date = date_ref.date()
    else:
        target_date = date_ref
    last_day_of_month = calendar.monthrange(target_date.year, target_date.month)[1]
    return target_date.day == last_day_of_month

def is_n_month_ago_in_dates(n, dates, date_ref=None, option_verbose=False):
    date_ref = date_ref if date_ref else dates[-1]
    if is_month_end(date_ref):
        date_n_month_ago = get_n_months_ago_last_date(date_ref, n)
    else:
        date_n_month_ago = get_date_n_months_ago(date_ref, n)
    
    if option_verbose:
        logger.info(date_n_month_ago)
    return date_n_month_ago in dates

def is_n_year_ago_in_dates(n, dates, date_ref=None, option_verbose=False):
    date_ref = date_ref if date_ref else dates[-1]
    if is_month_end(date_ref):
        date_n_year_ago = get_n_years_ago_last_date(date_ref, n)
    else:
        date_n_year_ago = get_date_n_years_ago(date_ref, n)
    
    if option_verbose:
        logger.info(date_n_year_ago)
    return date_n_year_ago in dates