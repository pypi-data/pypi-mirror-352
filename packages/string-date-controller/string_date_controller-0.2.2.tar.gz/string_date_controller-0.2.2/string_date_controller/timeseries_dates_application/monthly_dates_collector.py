from string_date_controller.date_determinator import is_month_end
from string_date_controller.date_shifter import (
    get_last_date_of_month, 
    get_date_n_months_ago
)
from collections import defaultdict

def get_month_end_dates(dates):
    dates_month_end = list(filter(is_month_end, dates))
    return dates_month_end

def adjust_first_and_last_date(dates, min_date, max_date):
    first_date = max(dates[0], min_date)
    last_date = min(dates[-1], max_date)
    return [first_date] + dates[1:-1] + [last_date]

def get_prev_month_end_dates_with_adjustment(dates):
    month_end_dates = get_month_end_dates(dates)
    dates = adjust_first_and_last_date(
        list(map(
            lambda date: get_last_date_of_month(get_date_n_months_ago(date, 1)), 
            month_end_dates
        )),
        dates[0],
        dates[-1]
    )
    return dates

def get_monthly_date_pairs(dates):
    first_date = dates[0]
    last_date = dates[-1]
    month_end_dates = get_month_end_dates(dates)
    prev_month_end_dates = adjust_first_and_last_date(
        list(map(
            lambda date: get_last_date_of_month(get_date_n_months_ago(date, 1)), 
            month_end_dates
        )),
        first_date,
        last_date
    )
    date_pairs = list(zip(prev_month_end_dates, month_end_dates))
    if last_date not in month_end_dates:
        date_pairs.append((month_end_dates[-1], last_date))
    return date_pairs

def create_nested_dict(date_pairs):
    dct = defaultdict(dict)
    for date_pair in date_pairs:
        year, month, _ = date_pair[-1].split('-')
        dct[year][month] = date_pair
    return dict(dct)

def get_all_data_monthly_date_pairs(dates):
    date_pairs = get_monthly_date_pairs(dates)
    return create_nested_dict(date_pairs)
