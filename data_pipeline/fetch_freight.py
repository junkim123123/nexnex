import os
import pandas as pd
import logging
from . import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_freight_data():
    """
    Reads raw freight data, normalizes it, and saves it to the processed data directory.
    """
    try:
        # Create the processed data directory if it doesn't exist
        os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)

        # Read the raw freight data from the CSV file
        df = pd.read_csv(config.FREIGHT_RATES_FILE)

        # Basic data normalization (this can be expanded later)
        df['rate_per_kg'] = pd.to_numeric(df['rate_per_kg'], errors='coerce')
        df['rate_per_cbm'] = pd.to_numeric(df['rate_per_cbm'], errors='coerce')
        df['rate_per_container'] = pd.to_numeric(df['rate_per_container'], errors='coerce')
        df['transit_days'] = pd.to_numeric(df['transit_days'], errors='coerce')

        # Save the processed data to a new CSV file
        df.to_csv(config.PROCESSED_FREIGHT_RATES_FILE, index=False)
        logging.info("Successfully processed freight data.")

    except FileNotFoundError:
        logging.error(f"Raw freight data file not found at: {config.FREIGHT_RATES_FILE}")
    except Exception as e:
        logging.error(f"An error occurred while processing freight data: {e}")

if __name__ == '__main__':
    process_freight_data()