from functools import reduce
from itertools import count, takewhile
import operator
import logging
from string_date_controller.date_shifter import (
    get_n_months_ago_last_date, 
    get_n_years_ago_last_date, 
    get_date_n_months_ago, 
    get_date_n_years_ago,
    get_first_date_of_year
)
from string_date_controller.date_determinator import is_month_end, is_n_month_ago_in_dates, is_n_year_ago_in_dates

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

def get_data_historical_timeseries_dates(dates, period_type, is_valid_fn, get_date_fn_regular, get_date_fn_month_end, date_ref=None, option_verbose=False):
    date_ref = date_ref if date_ref else dates[-1]
    """Generic function for getting historical dates"""
    if is_month_end(date_ref):
        get_date_fn = get_date_fn_month_end
    else:
        get_date_fn = get_date_fn_regular
    
    is_valid = lambda n: is_valid_fn(n, dates, date_ref, option_verbose)
    create_date_dict = lambda n: {f'{n}{period_type}': get_date_fn(date_ref, n)}
    valid_periods = takewhile(is_valid, count(1))
    return list(map(create_date_dict, valid_periods))

def get_data_historical_month_dates(dates, date_ref=None, option_verbose=False):
    """Get historical month dates - only 1, 3, 6 months"""
    VALID_MONTHS = [1, 3, 6]
    all_months = get_data_historical_timeseries_dates(
        dates, '-month', is_n_month_ago_in_dates,
        get_date_n_months_ago, get_n_months_ago_last_date,
        date_ref, option_verbose
    )
    
    # 1, 3, 6개월만 필터링
    return [month for month in all_months if any(f'{n}-month' in month for n in VALID_MONTHS)]

def get_data_historical_year_dates(dates, date_ref=None, option_verbose=False):
    return get_data_historical_timeseries_dates(
        dates, 
        '-year',
        is_n_year_ago_in_dates,
        get_date_n_years_ago,
        get_n_years_ago_last_date,
        date_ref,
        option_verbose
    )

def get_data_ytd_date(dates, date_ref=None):
    """Get year-to-date starting date"""
    date_ref = date_ref if date_ref else dates[-1]
    first_date_of_year = get_first_date_of_year(date_ref)
    if first_date_of_year in dates:
        return {'YTD': first_date_of_year}
    else:
        return {'YTD': str(dates[0])}

def get_data_inception_date(dates):
    return {'Since Inception': str(dates[0])}


def get_all_data_historical_dates(dates, date_ref=None, option_verbose=False):
    """Functional approach using reduce"""
    month_list = get_data_historical_month_dates(dates, date_ref, option_verbose)
    year_list = get_data_historical_year_dates(dates, date_ref, option_verbose)
    ytd_dict = [get_data_ytd_date(dates, date_ref)]
    inception_dict = [get_data_inception_date(dates)]
    return reduce(operator.or_, month_list + year_list + ytd_dict + inception_dict, {})
