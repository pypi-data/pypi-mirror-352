from itertools import count, takewhile
import logging
from string_date_controller.date_shifter import (
    get_n_months_ago_last_date, 
    get_n_years_ago_last_date, 
    get_date_n_months_ago, 
    get_date_n_years_ago,
    get_first_date_of_year
)
from string_date_controller.date_determinator import is_month_end, is_n_month_ago_in_dates, is_n_year_ago_in_dates

logging.basicConfig(format='%(message)s', level=logging.INFO)
logger = logging.getLogger()

def get_historical_timeseries_dates(date_ref, dates, period_type, is_valid_fn, get_date_fn_regular, get_date_fn_month_end, option_verbose=False):
    """Generic function for getting historical dates"""
    if is_month_end(date_ref):
        get_date_fn = get_date_fn_month_end
    else:
        get_date_fn = get_date_fn_regular
    
    is_valid = lambda n: is_valid_fn(n, dates, date_ref, option_verbose)
    create_date_dict = lambda n: {f'{n}{period_type}': get_date_fn(date_ref, n)}
    valid_periods = takewhile(is_valid, count(1))
    return list(map(create_date_dict, valid_periods))

def get_historical_month_dates(date_ref, dates, option_verbose=False):
    return get_historical_timeseries_dates(
        date_ref, 
        dates, 
        '-month',
        is_n_month_ago_in_dates,
        get_date_n_months_ago,
        get_n_months_ago_last_date,
        option_verbose
    )

def get_historical_year_dates(date_ref, dates, option_verbose=False):
    return get_historical_timeseries_dates(
        date_ref, 
        dates, 
        '-year',
        is_n_year_ago_in_dates,
        get_date_n_years_ago,
        get_n_years_ago_last_date,
        option_verbose
    )

def get_ytd_date(date_ref, dates):
    """Get year-to-date starting date"""
    first_date_of_year = get_first_date_of_year(date_ref)
    if first_date_of_year in dates:
        return {'ytd': first_date_of_year}
    else:
        return {'ytd': dates[0]}

def get_inception_date(dates):
    return {'date_inception': dates[0]}

def get_all_historical_dates(date_ref, dates, option_verbose=False):
    return {
        **get_historical_month_dates(date_ref, dates, option_verbose),
        **get_historical_year_dates(date_ref, dates, option_verbose),
        **get_ytd_date(date_ref, dates),
        **get_inception_date(dates)
    }