from .dataset_loader_s3 import *
from .dataset_loader_local import *
from .dataset_loader_config import DEFAULT_OPTION_DATA_SOURCE

DEFAULT_OPTION_DATA_SOURCE = 's3'

def load_menu2160(fund_code, option_data_source=DEFAULT_OPTION_DATA_SOURCE):
    mapping_option = {
        's3': load_menu2160_s3,
        'local': load_menu2160_local
    }
    return mapping_option[option_data_source](fund_code)

def load_menu2160_snapshot(date_ref=None, option_data_source=DEFAULT_OPTION_DATA_SOURCE):
    mapping_option = {
        's3': load_menu2160_snapshot_s3,
        'local': load_menu2160_snapshot_local
    }
    return mapping_option[option_data_source](date_ref)

def load_menu2205(fund_code, date_ref=None, option_data_source=DEFAULT_OPTION_DATA_SOURCE):
    mapping_option = {
        's3': load_menu2205_s3,
        'local': load_menu2205_local
    }
    return mapping_option[option_data_source](fund_code, date_ref)

def load_menu2205_snapshot(date_ref=None, option_data_source=DEFAULT_OPTION_DATA_SOURCE):
    mapping_option = {
        's3': load_menu2205_snapshot_s3,
        'local': load_menu2205_snapshot_local
    }
    return mapping_option[option_data_source](date_ref)

def load_menu2206(date_ref=None, option_data_source=DEFAULT_OPTION_DATA_SOURCE):
    mapping_option = {
        's3': load_menu2206_s3,
        'local': load_menu2206_local
    }
    return mapping_option[option_data_source](date_ref)

def load_menu8186_snapshot(date_ref=None, option_data_source=DEFAULT_OPTION_DATA_SOURCE):
    mapping_option = {
        's3': load_menu8186_snapshot_s3,
        'local': load_menu8186_snapshot_local
    }
    return mapping_option[option_data_source](date_ref)

def load_menu4165(fund_code, date_ref, option_data_source=DEFAULT_OPTION_DATA_SOURCE):
    mapping_option = {
        's3': load_menu4165_s3,
        'local': load_menu4165_local
    }
    return mapping_option[option_data_source](fund_code, date_ref)

def load_menu4165_snapshot(fund_code, date_ref=None, option_data_source=DEFAULT_OPTION_DATA_SOURCE):
    mapping_option = {
        's3': load_menu4165_snapshot_s3,
        'local': load_menu4165_snapshot_local
    }
    return mapping_option[option_data_source](fund_code, date_ref)

def load_index(ticker_bbg_index, option_data_source=DEFAULT_OPTION_DATA_SOURCE):
    mapping_option = {
        's3': load_index_s3,
        'local': load_index_local
    }
    return mapping_option[option_data_source](ticker_bbg_index)

def load_currency(ticker_bbg_currency, option_data_source=DEFAULT_OPTION_DATA_SOURCE):
    mapping_option = {
        's3': load_currency_s3,
        'local': load_currency_local
    }
    return mapping_option[option_data_source](ticker_bbg_currency)

def load_market(market_name, date_ref=None, option_data_source=DEFAULT_OPTION_DATA_SOURCE):
    mapping_option = {
        's3': load_market_s3,
        'local': load_market_local
    }
    return mapping_option[option_data_source](market_name, date_ref)

def load_menu(menu_code, fund_code, date_ref=None, option_data_source=DEFAULT_OPTION_DATA_SOURCE):
    mapping_option = {
        's3': load_menu_s3,
        'local': load_menu_local
    }
    return mapping_option[option_data_source](menu_code, fund_code, date_ref)

def load_menu_snapshot(menu_code, date_ref=None, option_data_source=DEFAULT_OPTION_DATA_SOURCE):
    mapping_option = {
        's3': load_menu_snapshot_s3,
        'local': load_menu_snapshot_local
    }
    return mapping_option[option_data_source](menu_code, date_ref)
