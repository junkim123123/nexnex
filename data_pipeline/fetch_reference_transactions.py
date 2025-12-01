import os
import pandas as pd
import logging
from . import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_reference_transactions_data():
    """
    Reads raw reference transactions data, normalizes it, and saves it to the processed data directory.
    """
    try:
        # Create the processed data directory if it doesn't exist
        os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)

        # Read the raw reference transactions data from the CSV file
        df = pd.read_csv(config.REFERENCE_TRANSACTIONS_FILE)

        # Basic data normalization
        df['fob_price_usd'] = df['fob_price_usd'].astype(float)
        df['quantity'] = df['quantity'].astype(int)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])

        # Save the processed data to a new CSV file
        df.to_csv(config.PROCESSED_REFERENCE_TRANSACTIONS_FILE, index=False)
        logging.info("Successfully processed reference transactions data.")

    except FileNotFoundError:
        logging.error(f"Raw reference transactions data file not found at: {config.REFERENCE_TRANSACTIONS_FILE}")
    except Exception as e:
        logging.error(f"An error occurred while processing reference transactions data: {e}")

if __name__ == '__main__':
    process_reference_transactions_data()