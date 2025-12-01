import os

# Get the absolute path of the project's root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define the paths for the raw and processed data directories
RAW_DATA_DIR = os.path.join(ROOT_DIR, 'data', 'raw')
PROCESSED_DATA_DIR = os.path.join(ROOT_DIR, 'data', 'processed')

# Define the file paths for the raw data files
FREIGHT_RATES_FILE = os.path.join(RAW_DATA_DIR, 'freight_rates.csv')
DUTIES_FILE = os.path.join(RAW_DATA_DIR, 'duties.csv')
REFERENCE_TRANSACTIONS_FILE = os.path.join(RAW_DATA_DIR, 'reference_transactions.csv')

# Define the file paths for the processed data files
PROCESSED_FREIGHT_RATES_FILE = os.path.join(PROCESSED_DATA_DIR, 'freight_rates.csv')
PROCESSED_DUTIES_FILE = os.path.join(PROCESSED_DATA_DIR, 'duties.csv')
PROCESSED_REFERENCE_TRANSACTIONS_FILE = os.path.join(PROCESSED_DATA_DIR, 'reference_transactions.csv')