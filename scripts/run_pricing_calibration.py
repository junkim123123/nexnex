import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.run_baseline_analyses import run_baseline_analyses

def run_pricing_calibration():
    """
    Runs baseline analyses, detects implausible results, and appends a report to CALIBRATION_NOTES.md.
    """
    # Step 1: Run baseline analyses to generate the latest results
    run_baseline_analyses()

    # Step 2: Load the results
    try:
        with open('tests/baseline_results.json', 'r') as f:
            results = json.load(f)
    except FileNotFoundError:
        print("Error: baseline_results.json not found. Run run_baseline_analyses.py first.")
        return

    # Step 3: Detect implausible cases
    implausible_cases = []
    for result in results:
        if 'error' in result:
            implausible_cases.append({
                'input': result['input'],
                'reason': f"Analysis failed with error: {result['error']}"
            })
            continue

        cost_scenarios = result.get('cost_scenarios', {})
        base_cost = cost_scenarios.get('base')

        # This part is a bit tricky since profitability is not in the baseline results.
        # We'll have to infer it or decide to add it. For now, let's check for very high risk.
        risk_scores = result.get('risk_scores', {})
        price_risk = risk_scores.get('price_risk')

        if price_risk and price_risk > 80:
             implausible_cases.append({
                'input': result['input'],
                'reason': f"High price risk detected: {price_risk:.1f}/100"
            })


    # Step 4: Append report to CALIBRATION_NOTES.md
    if not implausible_cases:
        print("No implausible cases detected.")
        return

    report = f"\n## Pricing Calibration Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    report += "The following baseline scenarios produced potentially implausible results:\n\n"
    for case in implausible_cases:
        report += f"- **Input:** `{case['input']}`\n"
        report += f"  - **Reason:** {case['reason']}\n"

    try:
        with open('docs/CALIBRATION_NOTES.md', 'a') as f:
            f.write(report)
        print(f"Successfully appended calibration report to docs/CALIBRATION_NOTES.md")
    except FileNotFoundError:
        print("Error: docs/CALIBRATION_NOTES.md not found.")

if __name__ == '__main__':
    run_pricing_calibration()