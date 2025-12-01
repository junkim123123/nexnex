import pandas as pd
import os
from datetime import date

# This script generates a synthetic dataset of product pricing information.
# It is designed to be re-runnable; it will overwrite the existing file with a fresh dataset.
# This approach is suitable for the current phase, as the data is entirely synthetic and
# based on internal heuristics. In a future implementation where data might be manually
# edited or augmented from external sources, a merge/update strategy would be more appropriate.

def get_project_root():
    """Gets the project root directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def generate_product_pricing_data():
    """
    Generates a DataFrame with synthetic product pricing data based on heuristics.
    """
    today = date.today().strftime("%Y-%m-%d")

    data = [
        # KR -> US Snacks
        ("KR snack - shrimp chips", "South Korea", "United States", 0.25, 0.45, 0.80, 1.20, 1.50, 2.50, 8.5, 5000, "bags in carton", "high-margin impulse snack", today),
        ("KR ramen", "South Korea", "United States", 0.50, 0.80, 1.20, 1.80, 2.00, 3.50, 6.0, 10000, "cups in box", "medium-margin staple", today),
        ("KR cookies", "South Korea", "United States", 0.80, 1.20, 1.80, 2.50, 3.00, 4.50, 8.5, 3000, "boxes in carton", "high-margin gift item", today),
        ("KR spicy snacks", "South Korea", "United States", 0.40, 0.60, 1.00, 1.50, 1.99, 2.99, 8.5, 5000, "bags in carton", "high-margin niche", today),

        # KR -> EU Snacks
        ("KR cookies", "South Korea", "Germany", 0.85, 1.25, 2.00, 2.80, 3.50, 5.00, 19.0, 3000, "boxes in carton", "high-margin gift item", today),
        ("KR snacks", "South Korea", "France", 0.50, 0.75, 1.50, 2.20, 2.50, 4.00, 20.0, 4000, "bags in carton", "medium-margin snack", today),
        ("KR ramen", "South Korea", "Netherlands", 0.55, 0.85, 1.30, 2.00, 2.20, 3.80, 21.0, 8000, "cups in box", "medium-margin staple", today),

        # KR -> JP Snacks
        ("KR convenience snacks", "South Korea", "Japan", 0.30, 0.50, 0.70, 1.10, 1.20, 1.80, 10.0, 10000, "bags in carton", "thin-margin high-volume", today),

        # CN -> US Electronics & Goods
        ("CN electronics - low value", "China", "United States", 2.50, 5.00, 7.00, 12.00, 15.00, 25.00, 9.0, 1000, "bubble wrap in box", "medium-margin electronics", today),
        ("CN toys", "China", "United States", 1.50, 4.00, 5.00, 10.00, 9.99, 19.99, 9.0, 2000, "polybag in carton", "high-margin seasonal", today),
        ("CN generic household goods", "China", "United States", 0.80, 2.00, 2.50, 5.00, 4.99, 9.99, 8.0, 3000, "items in master carton", "thin-margin commodity", today),
    ]

    columns = [
        "product_category",
        "origin_country",
        "destination_market",
        "typical_fob_low_usd",
        "typical_fob_high_usd",
        "typical_wholesale_price_low_usd",
        "typical_wholesale_price_high_usd",
        "typical_retail_price_low_usd",
        "typical_retail_price_high_usd",
        "vat_or_sales_tax_percent",
        "typical_moq_units",
        "packaging_type",
        "margin_hint",
        "last_updated"
    ]

    return pd.DataFrame(data, columns=columns)

def main():
    """
    Main function to generate and save the product pricing data.
    """
    project_root = get_project_root()
    output_dir = os.path.join(project_root, 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'product_pricing.csv')

    print("Generating synthetic product pricing data...")
    df = generate_product_pricing_data()
    
    print(f"Saving data to {output_path}...")
    df.to_csv(output_path, index=False)
    
    print("Successfully generated and saved product_pricing.csv.")
    print(f"\nTotal rows generated: {len(df)}")
    print("\nData preview:")
    print(df.head())

if __name__ == "__main__":
    main()