import pandas as pd
from openbb import obb

etf = "SSAC"

# esempio ETF USA (funziona): SPY
holdings = obb.etf.holdings(etf)

# estrai i risultati
data = holdings.results  # può essere lista o DataFrame

# se è una lista, trasformala in DataFrame
if isinstance(data, list):
    df = pd.DataFrame(data)
else:
    df = data

file_name = f"{etf}_holdings"
file_name_csv = f"{file_name}.csv"
file_name_xlsx = f"{file_name}.xlsx"

# salva su file
df.to_csv(f"{file_name_csv}", index=False)
df.to_excel(f"{file_name_xlsx}", index=False)

print(f"✅ Salvati file: {file_name_csv} e {file_name_xlsx}")
