import logging
from . import fetch_freight, fetch_duties, fetch_reference_transactions

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Main function to run all data processing scripts.
    """
    logging.info("Starting data pipeline processing...")
    
    # Process freight data
    fetch_freight.process_freight_data()
    
    # Process duties data
    fetch_duties.process_duties_data()
    
    # Process reference transactions data
    fetch_reference_transactions.process_reference_transactions_data()
    
    logging.info("Data pipeline processing complete.")

if __name__ == '__main__':
    main()