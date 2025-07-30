from shining_pebbles import scan_files_including_regex
from .date_formatter import transform_date_nondashed_to_dashed

def get_final_date_of_timeseries(df):
    return df.index.dropna()[-1]

def get_initial_date_of_timeseries(df):
    return df.index.dropna()[0]

def get_initial_and_final_date_of_timeseries(df):
    dates = df.index.dropna()
    return (dates[0], dates[-1])

def extract_date_ref_from_file_name(file_name, option_dashed=True, labels=('-at', '-')):
    start_label, end_label = labels
    date_ref = file_name.split(start_label)[-1].split(end_label)[0]
    if option_dashed:
        date_ref = transform_date_nondashed_to_dashed(date_ref)
    return date_ref

def extract_dates_ref_from_file_folder(file_folder, option_dashed=True, labels=('-at', '-')):
    file_names = scan_files_including_regex(file_folder, regex=labels[0])
    return [extract_date_ref_from_file_name(file_name, option_dashed, labels) for file_name in file_names]
