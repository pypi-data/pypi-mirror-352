from typing import List, Tuple, Dict
from string_date_controller import get_first_date_of_year, get_last_date_of_year

def get_ytd_date_pair_of_date_ref(dates: List[str], date_ref: str=None) -> Tuple[str, str]:
    date_ytd = get_first_date_of_year(date_ref)
    if date_ytd not in dates:
        date_ytd = dates[0]
    date_year_end = get_last_date_of_year(date_ref)
    if date_year_end not in dates:
        date_year_end = dates[-1]
    return date_ytd, date_year_end

def get_ytd_date_pair_of_year(dates: List[str], year: str=None) -> Tuple[str, str]:
    date_ytd = f"{year}-01-01"
    date_year_end = f"{year}-12-31"
    if date_ytd not in dates:
        date_ytd = dates[0]
    if date_year_end not in dates:
        date_year_end = dates[-1]
    return date_ytd, date_year_end

def get_all_exising_years(dates: List[str]) -> List[str]:
    return sorted(list(set(map(lambda date: date.split('-')[0], dates))))

def get_all_data_ytd_date_pairs(dates: List[str]) -> List[Dict[str, Tuple[str, str]]]:
    existing_years = get_all_exising_years(dates)
    return list(map(lambda year: {f'{year}': get_ytd_date_pair_of_year(dates, year)}, existing_years))

