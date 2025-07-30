transform_date_dashed_to_nondashed = lambda date_str: date_str.replace('-', '')
transform_date_nondashed_to_dashed = lambda date_str: f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

map_date_dashed_to_nondashed = transform_date_dashed_to_nondashed
map_date_nondashed_to_dashed = transform_date_nondashed_to_dashed