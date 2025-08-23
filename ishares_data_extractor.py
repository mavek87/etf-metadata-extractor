import json
import os
import sys
import traceback
from datetime import datetime

import pandas as pd

from file_utils import create_output_folder

if len(sys.argv) < 2:
    raise ValueError("❌ You have to specify the name of the CSV file as argument")

etf_isin_prefix = sys.argv[1]

print("Reading the csv...")

date_and_time_format = "%Y-%m-%d %H:%M:%S"
etf_8_encoding = "utf-8-sig"
csv_extension = ".csv"
json_extension = ".json"
# country = "_it"
country = ""

# input_csv_file_name_prefix = "etf_data"
# input_csv_file_name_prefix = "EIMI_holdings"
# input_csv_file_name_and_country_prefix = input_csv_file_name_prefix + country
# input_csv_file_name = input_csv_file_name_and_country_prefix + csv_extension
input_folder = create_output_folder("input", "")
print(f"Input folder: {input_folder}")
input_csv_file_name = os.path.join(input_folder, etf_isin_prefix + csv_extension)
print(f"Input csv file name: {input_csv_file_name}")

output_folder = create_output_folder("output", etf_isin_prefix)
print(f"Output folder: {output_folder}")
output_clean_csv_file_name = os.path.join(output_folder, etf_isin_prefix + "_clean" + csv_extension)
print(f"Output clean CSV file: {output_clean_csv_file_name}")
output_json_file_sectors = os.path.join(output_folder, "sectors" + json_extension)
print(f"Output json file sectors: {output_json_file_sectors}")
output_json_file_countries = os.path.join(output_folder, "countries" + json_extension)
print(f"Output json file countries: {output_json_file_countries}")
output_json_file_summary = os.path.join(output_folder, "summary" + json_extension)
print(f"Output json file summary: {output_json_file_summary}")

try:
    df = pd.read_csv(input_csv_file_name, skiprows=2, encoding=etf_8_encoding)

    print(f"✅ Successfully read {input_csv_file_name}!")
    print(f"Dimensions: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    if len(df.columns) == 1:
        print("⚠️  Just 1 column found, trying with other separators...")

        df = pd.read_csv(input_csv_file_name, skiprows=1, encoding=etf_8_encoding, sep=';')
        if len(df.columns) == 1:
            df = pd.read_csv(input_csv_file_name, skiprows=1, encoding=etf_8_encoding, sep=',', quotechar='"')

    print(f"Final dimensions: {df.shape}")
    print(f"Final columns: {list(df.columns)}")

    # Removing extra spaces from column names
    df.columns = df.columns.str.strip()

    print("\nFirst 3 rows:")
    print(df.head(3).to_string())

    weight_col = None
    sector_col = None
    location_col = None

    for col in df.columns:
        if 'weight' in col.lower() or 'ponderazione' in col.lower() and '%' in col:
            weight_col = col
            print(f"✅ Weight colum: '{col}'")
        elif 'sector' in col.lower() or 'settore' in col.lower():
            sector_col = col
            print(f"✅ Sector column: '{col}'")
        elif 'location' in col.lower() or 'area' in col.lower():
            location_col = col
            print(f"✅ Location column: '{col}'")

    if not all([weight_col, sector_col, location_col]):
        print("❌ Not all the columns were found")
        print("Available columns:")
        for i, col in enumerate(df.columns):
            print(f"  {i}: '{col}'")
        exit()

    print(f"\nColumn analysis '{weight_col}':")
    print(f"Unique values (first 10): {df[weight_col].unique()[:10]}")
    print(f"Null values: {df[weight_col].isna().sum()}")
    print(f"Empty values: {(df[weight_col] == '').sum()}")

    print("\nCleaning the weight column...")
    df[weight_col] = df[weight_col].astype(str)
    df[weight_col] = df[weight_col].str.strip()
    df[weight_col] = df[weight_col].str.replace(',', '.')  # Italian decimals -> english
    df[weight_col] = df[weight_col].str.replace('%', '')  # Remove % if present

    # Filter only the rows with valid numeric values
    numeric_pattern = r'^[0-9]+\.?[0-9]*$'
    valid_mask = df[weight_col].str.match(numeric_pattern, na=False)

    print(f"Rows with valid weight: {valid_mask.sum()}/{len(df)}")

    invalid_values = df[~valid_mask][weight_col].unique()[:10]
    print(f"Invalid values (examples): {invalid_values}")

    if valid_mask.sum() == 0:
        print("❌ No valid values found!")
        print("First 5 errors in the weight column:")
        for i in range(min(5, len(df))):
            print(f"  Row {i}: '{df[weight_col].iloc[i]}'")
        exit()

    # Create DataFrame with only valid rows
    df_valid = df[valid_mask].copy()
    df_valid[weight_col] = df_valid[weight_col].astype(float)

    print(f"\n{'=' * 60}")
    print("📊 DATA ANALYSIS")
    print(f"Valid rows: {len(df_valid)}")
    print(f"Weight sum: {df_valid[weight_col].sum():.2f}%")

    print("\n🏢 TOP 15 SECTORS:")
    sectors = df_valid.groupby(sector_col)[weight_col].sum().sort_values(ascending=False)
    sectors = sectors[sectors > 0]

    for i, (sector, perc) in enumerate(sectors.head(15).items(), 1):
        print(f"{i:2d}. {sector:25s}: {perc:6.2f}%")

    print("\n🌍 TOP 15 LOCATIONS:")
    locations = df_valid.groupby(location_col)[weight_col].sum().sort_values(ascending=False)
    locations = locations[locations > 0]

    for i, (location, perc) in enumerate(locations.head(15).items(), 1):
        print(f"{i:2d}. {location:25s}: {perc:6.2f}%")

    print("\n📈 STATS:")
    print(f"Total number of sectors: {len(sectors)}")
    print(f"Total number of locations: {len(locations)}")
    print(f"Top 6 sectors percentage: {sectors.head(6).sum():.2f}%")
    print(f"Top 6 locations percentage: {locations.head(6).sum():.2f}%")

    print("\n💾 FILES EXPORT:")
    sectors.to_json(output_json_file_sectors, orient="index", indent=2)
    locations.to_json(output_json_file_countries, orient="index", indent=2)
    df_valid.to_csv(output_clean_csv_file_name, index=False)

    print(f"✅ {output_json_file_sectors}        - {len(sectors)} sectors")
    print(f"✅ {output_json_file_countries}         - {len(locations)} locations ")
    print(f"✅ {output_clean_csv_file_name}     - {len(df_valid)} clean rows")

    current_date = datetime.now().strftime(date_and_time_format)

    summary = {
        "ISIN": etf_isin_prefix,
        "data": current_date,
        "total_rows": len(df),
        "valid_rows": len(df_valid),
        "weight_sum": float(df_valid[weight_col].sum()),
        "num_sectors": len(sectors),
        "num_locations": len(locations),
        "top_10_sectors": dict(sectors.head(10)),
        "top_10_locations": dict(locations.head(10))
    }

    with open(output_json_file_summary, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"✅ {output_json_file_summary}      - Analysis summary")

except Exception as e:
    print(f"❌ Error: {e}")

    traceback.print_exc()
