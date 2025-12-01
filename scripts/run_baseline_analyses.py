import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.nlp_parser import parse_user_input
from core.analysis_engine import run_analysis

def run_baseline_analyses():
    """
    Runs a series of baseline analyses and stores the results in a JSON file.
    """
    baseline_inputs = [
        # Existing baselines
        "새우깡 5,000봉지 미국에 4달러에 팔거야",
        "초코파이 10,000박스 미국에 2달러씩 팔 거야",
        "Korean cookies to Germany",
        "신라면 20,000개 미국으로 수출",
        "김치 1,000kg 유럽(독일)에 수출",

        # New baselines for pricing calibration
        "KR→US shrimp chips",
        "KR→US ramen",
        "KR→EU cookies"
    ]

    baseline_results = []

    for user_input in baseline_inputs:
        try:
            parsed_input = parse_user_input(user_input)
            analysis_result = run_analysis(parsed_input)
            baseline_results.append({
                'input': user_input,
                'cost_scenarios': analysis_result.get('cost_scenarios'),
                'risk_scores': analysis_result.get('risk_scores'),
                'used_fallbacks': analysis_result.get('data_quality', {}).get('used_fallbacks')
            })
        except Exception as e:
            baseline_results.append({
                'input': user_input,
                'error': str(e)
            })

    with open('tests/baseline_results.json', 'w') as f:
        json.dump(baseline_results, f, indent=4)

    print("Baseline analyses completed successfully.")

if __name__ == '__main__':
    run_baseline_analyses()