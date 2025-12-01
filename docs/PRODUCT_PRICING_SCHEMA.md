# Product Pricing Data Schema

This document defines the schema for the `data/product_pricing.csv` file. This file provides the analysis engine with realistic pricing, margin, and tax data for various product categories to improve the accuracy of cost and profitability estimates.

## 1. Purpose

The primary purpose of this dataset is to:
- **Provide realistic price ranges:** When users do not provide specific FOB, wholesale, or retail prices, the engine can use the ranges from this dataset as a plausible baseline.
- **Act as a sanity check:** If a user provides prices that are far outside the typical ranges for a given product, the system can flag it as a potential risk or error.
- **Improve margin analysis:** By providing hints about typical margins and sales taxes, the engine can generate more accurate profitability forecasts.
- **Reduce reliance on generic fallbacks:** This data layer allows the system to make more specific, data-driven assumptions instead of relying on broad, hard-coded heuristics.

## 2. Schema Definition

**File Location:** `data/product_pricing.csv`

| Column Name | Type | Description | Example Value | How it's used by the analysis engine |
|---|---|---|---|---|
| `product_category` | String | A specific, queryable product category identifier. This is the primary key for matching against a user's query. | `KR snack - shrimp chips` | Used to find the most relevant pricing data for the user's specified product. |
| `origin_country` | String | The country where the product is manufactured/shipped from. Must be a normalized name (e.g., "South Korea"). | `South Korea` | Part of the composite key to find the correct pricing row. |
| `destination_market` | String | The target market/country for the product. Must be a normalized name (e.g., "United States"). | `United States` | Part of the composite key to find the correct pricing row. |
| `typical_fob_low_usd` | Float | The low end of the typical Free On Board (FOB) price per unit, in USD. | `0.25` | Used to estimate a baseline FOB price if the user doesn't provide one. |
| `typical_fob_high_usd` | Float | The high end of the typical FOB price per unit, in USD. | `0.45` | Used to estimate a baseline FOB price and for sanity-checking user input. |
| `typical_wholesale_price_low_usd` | Float | The low end of the typical wholesale price per unit in the destination market, in USD. | `0.80` | Helps in estimating the wholesale price range for margin calculations. |
| `typical_wholesale_price_high_usd` | Float | The high end of the typical wholesale price per unit in the destination market, in USD. | `1.20` | Helps in estimating the wholesale price range for margin calculations. |
| `typical_retail_price_low_usd` | Float | The low end of the typical retail price per unit in the destination market, in USD. | `1.50` | Used to estimate a baseline retail price if the user doesn't provide one. |
| `typical_retail_price_high_usd` | Float | The high end of the typical retail price per unit in the destination market, in USD. | `2.50` | Used to estimate a baseline retail price and for sanity-checking user input. |
| `vat_or_sales_tax_percent` | Float | An approximate VAT or sales tax percentage in the destination market for this product category. | `8.5` | Applied during the final profitability calculation to estimate net margin. |
| `typical_moq_units` | Integer | The typical Minimum Order Quantity (MOQ) for this type of product. | `5000` | Can be used to inform the user about typical order sizes or to adjust risk scores. |
| `packaging_type` | String | A brief description of the common packaging format. | `bags in carton` | Informational data that can be used in future analysis or reports. |
| `margin_hint` | String | A qualitative hint about the product's margin profile. | `high-margin impulse snack` | Used by the risk engine to assess the viability of the user's stated prices. |
| `last_updated` | String | The date when the data for this row was last updated, in YYYY-MM-DD format. | `2025-12-01` | For data maintenance and to track the freshness of the data. |

## 3. How the Analysis Engine Uses This Data

1.  **Data Loading:** The `core.data_access` module will contain a function, `get_product_pricing_hint()`, which loads `product_pricing.csv` into a pandas DataFrame and searches for the best match.
2.  **Matching Logic:** The engine will attempt to find a row that matches the `product_category`, `origin_country`, and `destination_market` from the user's `ShipmentSpec`. If an exact match is not found, it may fall back to a partial match (e.g., on `product_category` and `origin_country` only).
3.  **Price Estimation (Fallback):** If the user's query does not specify an FOB or retail price, the engine will use the `typical_fob_low_usd`/`high` and `typical_retail_price_low_usd`/`high` values from the matched row to populate these fields in the `AnalysisResult`.
4.  **Price Validation (Sanity Check):** If the user *does* specify prices, the engine will compare them against the ranges in the matched row. If the user's price is significantly outside the typical range (e.g., 50% higher or lower), a warning will be added to the `AnalysisResult` and the `price_risk` score will be increased.
5.  **Margin Calculation:** The `vat_or_sales_tax_percent` will be used to calculate the post-tax profit margin, making the final "Verdict" more realistic.
6.  **Risk Scoring:** The `margin_hint` and the comparison of user-provided data against the dataset will influence the overall risk score, particularly the financial and market risk components.

This data layer is a critical step in moving from purely heuristic-based analysis to a more data-informed model, significantly improving the quality and reliability of the generated reports.