from shining_pebbles import open_df_in_file_folder_by_regex
from .path_director import FILE_FOLDER
from .file_name_formatter import format_regex_for_snapshot, format_regex_for_timeseries, format_regex_for_period, format_regex_for_bbg_price, format_regex_for_market

def load_menu2160_local(fund_code):
    regex = format_regex_for_timeseries(menu_code='2160', fund_code=fund_code)
    df = open_df_in_file_folder_by_regex(file_folder=FILE_FOLDER['2160'], regex=regex)
    return df

def load_menu2160_snapshot_local(date_ref=None):
    regex = format_regex_for_snapshot(menu_code='2160', fund_code='000000', date_ref=date_ref)
    df = open_df_in_file_folder_by_regex(file_folder=FILE_FOLDER['2160-snapshot'], regex=regex)
    return df

def load_menu2205_local(fund_code, date_ref=None):
    regex = format_regex_for_snapshot(menu_code='2205', fund_code=fund_code, date_ref=date_ref)
    df = open_df_in_file_folder_by_regex(file_folder=FILE_FOLDER['2205'], regex=regex)
    return df

def load_menu2205_snapshot_local(date_ref=None):
    regex = format_regex_for_snapshot(menu_code='2205', fund_code='000000', date_ref=date_ref)
    df = open_df_in_file_folder_by_regex(file_folder=FILE_FOLDER['2205-snapshot'], regex=regex)
    return df

def load_menu2206_local(date_ref=None):
    regex = format_regex_for_snapshot(menu_code='2206', fund_code='000000', date_ref=date_ref)
    df = open_df_in_file_folder_by_regex(file_folder=FILE_FOLDER['2206'], regex=regex)
    return df
    
def load_menu8186_snapshot_local(date_ref=None):
    regex = format_regex_for_snapshot(menu_code='8186', fund_code='000000', date_ref=date_ref)
    df = open_df_in_file_folder_by_regex(file_folder=FILE_FOLDER['8186-snapshot'], regex=regex)
    return df

def load_menu4165_local(fund_code, date_ref):
    regex = format_regex_for_period(menu_code='4165', fund_code=fund_code, date_ref=date_ref)
    df = open_df_in_file_folder_by_regex(file_folder=FILE_FOLDER['4165'], regex=regex)
    return df

def load_menu4165_snapshot_local(fund_code, date_ref=None):
    regex = format_regex_for_snapshot(menu_code='4165', fund_code=fund_code, date_ref=date_ref)
    df = open_df_in_file_folder_by_regex(file_folder=FILE_FOLDER['4165'], regex=regex)
    return df

def load_index_local(ticker_bbg_index):
    regex = format_regex_for_bbg_price(ticker_bbg=ticker_bbg_index)
    df = open_df_in_file_folder_by_regex(file_folder=FILE_FOLDER['index'], regex=regex)
    return df

def load_currency_local(ticker_bbg_currency):
    regex = format_regex_for_bbg_price(ticker_bbg=ticker_bbg_currency)
    df = open_df_in_file_folder_by_regex(file_folder=FILE_FOLDER['currency'], regex=regex)
    return df

def load_market_local(market_name, date_ref=None):
    regex = format_regex_for_market(market_name=market_name, date_ref=date_ref)
    df = open_df_in_file_folder_by_regex(file_folder=FILE_FOLDER['market'], regex=regex)
    return df

def load_menu_local(menu_code, fund_code, date_ref=None):
    regex = format_regex_for_snapshot(menu_code=menu_code, fund_code=fund_code, date_ref=date_ref)
    df = open_df_in_file_folder_by_regex(file_folder=FILE_FOLDER[menu_code], regex=regex)
    return df

def load_menu_snapshot_local(menu_code, date_ref=None):
    regex = format_regex_for_snapshot(menu_code=menu_code, fund_code='000000', date_ref=date_ref)
    df = open_df_in_file_folder_by_regex(file_folder=FILE_FOLDER[menu_code], regex=regex)
    return df


