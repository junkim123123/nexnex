# Data Quality Report

This report provides a summary of the data quality for the CSV datasets used in the NexSupply AI project.

## Freight Rates

- **Row Count:** 12
- **Distinct Origin/Destination Combinations:** 8
- **Coverage Score:** 1

### Numeric Stats

| Column | Mean | Std Dev | Min | Max |
|---|---|---|---|---|
| rate_per_kg | 4.8 | 1.1 | 3.0 | 6.0 |
| rate_per_cbm | 105.8 | 13.1 | 80.0 | 120.0 |
| rate_per_container | 1700.0 | 141.4 | 1600.0 | 1800.0 |

## Duty Rates

- **Row Count:** 13
- **Distinct HS Codes:** 6
- **Coverage Score:** 2

### Numeric Stats

| Column | Mean | Std Dev | Min | Max |
|---|---|---|---|---|
| duty_rate_percent | 5.8 | 4.5 | 0.0 | 10.0 |
| section_301_rate_percent | 10.5 | 11.1 | 0.0 | 25.0 |

## Extra Costs

- **Row Count:** 5
- **Coverage Score:** 2

### Numeric Stats

| Column | Mean | Std Dev | Min | Max |
|---|---|---|---|---|
| terminal_handling | 0.11 | 0.02 | 0.1 | 0.15 |
| customs_clearance | 0.07 | 0.02 | 0.05 | 0.10 |
| inland_transport | 0.16 | 0.02 | 0.15 | 0.20 |
| inspection_qc | 0.38 | 0.16 | 0.20 | 0.60 |
| certification | 0.50 | 0.22 | 0.30 | 0.80 |

## Reference Transactions

- **Row Count:** 20
- **Coverage Score:** 1

### Numeric Stats

| Column | Mean | Std Dev | Min | Max |
|---|---|---|---|---|
| fob_price_per_unit | 0.5 | 0.4 | 0.2 | 1.3 |
| landed_cost_per_unit | 0.8 | 0.6 | 0.4 | 2.3 |
| volume | 24450 | 14078 | 8000 | 70000 |

## Product Pricing

- **Row Count:** 11
- **Coverage:** Covers key product categories for KR→US, KR→EU, KR→JP, and CN→US routes.
- **Areas for Improvement:** The dataset is still small and relies on heuristics. More granular data for different product sub-categories and routes is needed to reduce fallbacks further.

## Summary

The CSV datasets have been expanded with synthetic data to improve coverage and reduce reliance on fallbacks. The following is a summary of the changes:

- **freight_rates.csv:** Now has 12 rows covering key shipping lanes between KR, US, EU, JP, and CN.
- **duty_rates.csv:** Now has 13 rows with duty rates for common product categories.
- **extra_costs.csv:** Now has 5 rows with cost breakdowns for different product types.
- **reference_transactions.csv:** Now has 20 rows of sample transactions for various products and routes.
- **product_pricing.csv:** A new dataset with 11 rows providing pricing hints for key product categories and routes. This is a major step towards reducing reliance on generic heuristics for price estimation.

While the coverage scores have improved, the system may still rely on fallbacks for less common scenarios. The KR → US snack import baseline analysis now uses fewer fallbacks and appears more economically plausible.