import os

BASE_DIR = 'data'

FILE_FOLDER = {
    '2160': os.path.join(BASE_DIR, 'dataset-menu2160'),
    '2160-snapshot': os.path.join(BASE_DIR, 'dataset-menu2160-snapshot'),
    '2205': os.path.join(BASE_DIR, 'dataset-menu2205'),
    '2205-snapshot': os.path.join(BASE_DIR, 'dataset-menu2205-snapshot'),
    '4165': os.path.join(BASE_DIR, 'dataset-menu4165'),
    '8186-snapshot': os.path.join(BASE_DIR, 'dataset-menu8186-snapshot'),
    '2110': os.path.join(BASE_DIR, 'dataset-menu2110'),
    '3412': os.path.join(BASE_DIR, 'dataset-menu3412'),
    '3421': os.path.join(BASE_DIR, 'dataset-menu3421'),
    '3233': os.path.join(BASE_DIR, 'dataset-menu3233'),
    'fund': os.path.join(BASE_DIR, 'dataset-fund'),
    'market': os.path.join(BASE_DIR, 'dataset-market'),
    'index': os.path.join(BASE_DIR, 'dataset-index'),
    'currency': os.path.join(BASE_DIR, 'dataset-currency'),
    'equity': os.path.join(BASE_DIR, 'dataset-equity'),
}

BUCKET_SYSTEM = 'dataset-system'
BUCKET_BBG = 'dataset-bbg'

BUCKET_PREFIX = {
    '2160': 'dataset-menu2160',
    '2160-snapshot': 'dataset-menu2160-snapshot',
    '2205': 'dataset-menu2205',
    '2205-snapshot': 'dataset-menu2205-snapshot',
    '2206': 'dataset-menu2206',
    '4165': 'dataset-menu4165',
    '8186-snapshot': 'dataset-menu8186-snapshot',
    '2110': 'dataset-menu2110',
    '3412': 'dataset-menu3412',
    '3421': 'dataset-menu3421',
    '3233': 'dataset-menu3233',
    'market': 'dataset-market',
    'index': 'dataset-index',
    'currency': 'dataset-currency',
    'equity': 'dataset-equity',
    'timeseries': 'dataset-timeseries'
}