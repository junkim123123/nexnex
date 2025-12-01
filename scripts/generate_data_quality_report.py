import pandas as pd
import json

def generate_data_quality_report():
    """
    Analyzes the CSV datasets and generates a data quality report.
    """
    report = {}

    # Analyze freight_rates.csv
    try:
        df_freight = pd.read_csv('data/raw/freight_rates.csv')
        report['freight_rates'] = {
            'row_count': len(df_freight),
            'distinct_combinations': len(df_freight.groupby(['origin', 'destination'])),
            'numeric_stats': {
                'rate_per_kg': df_freight['rate_per_kg'].describe().to_dict(),
            },
            'coverage_score': min(100, len(df_freight) // 10)
        }
    except FileNotFoundError:
        report['freight_rates'] = {'error': 'File not found'}

    # Analyze duty_rates.csv
    try:
        df_duty = pd.read_csv('data/raw/duties.csv')
        report['duty_rates'] = {
            'row_count': len(df_duty),
            'distinct_hs_codes': len(df_duty['hs_code'].unique()),
            'numeric_stats': {
                'duty_rate_percent': df_duty['duty_rate_percent'].describe().to_dict(),
            },
            'coverage_score': min(100, len(df_duty) // 5)
        }
    except FileNotFoundError:
        report['duty_rates'] = {'error': 'File not found'}

    # Analyze extra_costs.csv
    try:
        df_extra = pd.read_csv('data/raw/extra_costs.csv')
        report['extra_costs'] = {
            'row_count': len(df_extra),
            'numeric_stats': {
                'terminal_handling': df_extra['terminal_handling'].describe().to_dict(),
                'customs_clearance': df_extra['customs_clearance'].describe().to_dict(),
            },
            'coverage_score': min(100, len(df_extra) // 2)
        }
    except FileNotFoundError:
        report['extra_costs'] = {'error': 'File not found'}

    # Analyze reference_transactions.csv
    try:
        df_ref = pd.read_csv('data/raw/reference_transactions.csv')
        report['reference_transactions'] = {
            'row_count': len(df_ref),
            'numeric_stats': {},
            'coverage_score': min(100, len(df_ref) // 20)
        }
    except FileNotFoundError:
        report['reference_transactions'] = {'error': 'File not found'}

    with open('data/data_quality_report.json', 'w') as f:
        json.dump(report, f, indent=4)

    print("Data quality report generated successfully.")

if __name__ == '__main__':
    generate_data_quality_report()