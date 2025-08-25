import os
import sys
import traceback
import json
from datetime import datetime

import pandas as pd

from file_utils import create_output_folder

if len(sys.argv) < 2:
    raise ValueError("❌ You have to specify the name of the XLSX file as argument")

etf_isin_prefix = sys.argv[1]

print("Reading the xlsx...")

date_and_time_format = "%Y-%m-%d %H:%M:%S"
xlsx_extension = ".xlsx"
json_extension = ".json"

input_folder = create_output_folder("input/xtrackers", "")
print(f"Input folder: {input_folder}")
input_xlsx_file_name = os.path.join(input_folder, etf_isin_prefix + xlsx_extension)
print(f"Input xlsx file name: {input_xlsx_file_name}")

output_folder = create_output_folder("output/xtrackers", etf_isin_prefix)
print(f"Output folder: {output_folder}")
output_clean_csv_file_name = os.path.join(output_folder, etf_isin_prefix + "_clean.csv")
print(f"Output clean CSV file: {output_clean_csv_file_name}")
output_json_file_sectors = os.path.join(output_folder, "sectors" + json_extension)
print(f"Output json file sectors: {output_json_file_sectors}")
output_json_file_countries = os.path.join(output_folder, "countries" + json_extension)
print(f"Output json file countries: {output_json_file_countries}")
output_json_file_summary = os.path.join(output_folder, "summary" + json_extension)
print(f"Output json file summary: {output_json_file_summary}")

try:
    # Lettura del file XLSX
    df = pd.read_excel(input_xlsx_file_name, skiprows=3)

    print(f"✅ Successfully read {input_xlsx_file_name}!")
    print(f"Dimensions: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    # Rimozione di spazi superflui nei nomi delle colonne
    df.columns = df.columns.str.strip()

    print("\nFirst 3 rows:")
    print(df.head(3).to_string())

    # Identificazione delle colonne necessarie
    weight_col = "Weighting"
    sector_col = "Industry Classification"
    country_col = "Country"

    if not all([weight_col in df.columns, sector_col in df.columns, country_col in df.columns]):
        print("❌ Not all key columns are present in the dataset")
        print("Available columns:")
        for i, col in enumerate(df.columns):
            print(f"  {i}: '{col}'")
        exit()

    # Pulizia della colonna dei pesi
    print(f"\nCleaning the '{weight_col}' column...")
    df[weight_col] = df[weight_col].astype(str)
    df[weight_col] = df[weight_col].str.replace(',', '.')  # Decimal point adjustment
    df[weight_col] = df[weight_col].str.replace('%', '')  # Remove percentage symbol
    df[weight_col] = pd.to_numeric(df[weight_col], errors='coerce')

    # Filtrare solo le righe valide
    df_valid = df.dropna(subset=[weight_col])

    print(f"\n{'=' * 60}")
    print("📊 DATA ANALYSIS")
    print(f"Valid rows: {len(df_valid)}")
    print(f"Weight sum: {df_valid[weight_col].sum():.2f}%")

    # Analisi per settore
    print("\n🏢 TOP 15 SECTORS:")
    sectors = df_valid.groupby(sector_col)[weight_col].sum().sort_values(ascending=False)
    sectors = sectors[sectors > 0]

    for i, (sector, perc) in enumerate(sectors.head(15).items(), 1):
        print(f"{i:2d}. {sector:30s}: {perc:6.2f}%")

    # Analisi per nazione
    print("\n🌍 TOP 15 COUNTRIES:")
    countries = df_valid.groupby(country_col)[weight_col].sum().sort_values(ascending=False)
    countries = countries[countries > 0]

    for i, (country, perc) in enumerate(countries.head(15).items(), 1):
        print(f"{i:2d}. {country:30s}: {perc:6.2f}%")

    # Esportazione dei dati
    print("\n💾 EXPORTING FILES...")
    sectors.to_json(output_json_file_sectors, orient="index", indent=2)
    countries.to_json(output_json_file_countries, orient="index", indent=2)
    df_valid.to_csv(output_clean_csv_file_name, index=False)

    print(f"✅ {output_json_file_sectors}        - {len(sectors)} sectors")
    print(f"✅ {output_json_file_countries}         - {len(countries)} countries ")
    print(f"✅ {output_clean_csv_file_name}     - {len(df_valid)} clean rows")

    # Creazione di un file di riepilogo
    current_date = datetime.now().strftime(date_and_time_format)

    summary = {
        "ISIN": etf_isin_prefix,
        "data": current_date,
        "total_rows": len(df),
        "valid_rows": len(df_valid),
        "weight_sum": float(df_valid[weight_col].sum()),
        "num_sectors": len(sectors),
        "num_countries": len(countries),
        "top_10_sectors": dict(sectors.head(10)),
        "top_10_countries": dict(countries.head(10))
    }

    with open(output_json_file_summary, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"✅ {output_json_file_summary}      - Analysis summary")

except Exception as e:
    print(f"❌ Error: {e}")

    traceback.print_exc()