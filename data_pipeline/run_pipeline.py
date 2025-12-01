import argparse
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_pipeline.fetch_all import fetch_all_data
from scripts.generate_data_quality_report import generate_data_quality_report
from scripts.run_baseline_analyses import run_baseline_analyses
from scripts.run_pricing_calibration import run_pricing_calibration

def run_pipeline(with_pricing_calibration: bool = False):
    """
    Runs the main data pipeline, which includes fetching data, generating a data quality report,
    and running baseline analyses.
    """
    # Step 1: Fetch all data
    fetch_all_data()

    # Step 2: Generate data quality report
    generate_data_quality_report()

    # Step 3: Run baseline analyses
    run_baseline_analyses()

    # Step 4: Optionally run pricing calibration
    if with_pricing_calibration:
        print("Running pricing calibration...")
        run_pricing_calibration()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the NexSupply data pipeline.")
    parser.add_argument(
        '--with-pricing-calibration',
        action='store_true',
        help='If set, runs the pricing calibration routine.'
    )
    args = parser.parse_args()

    run_pipeline(with_pricing_calibration=args.with_pricing_calibration)