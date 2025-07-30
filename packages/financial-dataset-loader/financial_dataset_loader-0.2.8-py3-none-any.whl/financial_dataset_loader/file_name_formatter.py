from string_date_controller import get_first_date_of_month, get_last_date_of_month

def format_regex_for_snapshot(menu_code, fund_code, date_ref=None):
    if date_ref:
        date_ref = date_ref.replace('-', '')
        regex = f'menu{menu_code}-code{fund_code}-at{date_ref}'
    else:
        regex = f'menu{menu_code}-code{fund_code}-at'
    return regex

def format_regex_for_timeseries(menu_code, fund_code):
    regex = f'menu{menu_code}-code{fund_code}'
    return regex

def format_regex_for_period(menu_code, fund_code, start_date=None, end_date=None, date_ref=None):
    if date_ref and start_date==None and end_date==None:
        start_date = get_first_date_of_month(date_ref)
        end_date = get_last_date_of_month(date_ref)
    regex = f'menu{menu_code}-code{fund_code}-between{start_date.replace("-", "")}-and{end_date.replace("-", "")}'
    return regex

def format_regex_for_bbg_price(ticker_bbg):
    regex = f'dataset-bbg-{ticker_bbg}-PX_LAST'
    return regex

def format_regex_for_market(market_name, date_ref=None):
    if date_ref:
        date_ref = date_ref.replace('-', '')
        regex = f'dataset-bbg-{market_name}_market-at{date_ref}'
    else:
        regex = f'dataset-bbg-{market_name}_market-'
    return regex

def format_regex_for_index_market(ticker_bbg_index, date_ref=None):
    if date_ref:
        date_ref = date_ref.replace('-', '')
        regex = f'dataset-bbg-{ticker_bbg_index}-market-at{date_ref}'
    else:
        regex = f'dataset-bbg-{ticker_bbg_index}-market-'
    return regex
