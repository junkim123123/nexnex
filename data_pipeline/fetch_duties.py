import os
import pandas as pd
import logging
from . import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_duties_data():
    """
    Reads raw duties data, normalizes it, and saves it to the processed data directory.
    """
    try:
        # Create the processed data directory if it doesn't exist
        os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)

        # Read the raw duties data from the CSV file
        df = pd.read_csv(config.DUTIES_FILE)

        # Basic data normalization
        df['duty_rate_percent'] = df['duty_rate_percent'].astype(float)

        # Save the processed data to a new CSV file
        df.to_csv(config.PROCESSED_DUTIES_FILE, index=False)
        logging.info("Successfully processed duties data.")

    except FileNotFoundError:
        logging.error(f"Raw duties data file not found at: {config.DUTIES_FILE}")
    except Exception as e:
        logging.error(f"An error occurred while processing duties data: {e}")

if __name__ == '__main__':
    process_duties_data()