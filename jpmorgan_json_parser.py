import json
from pprint import pprint  # per stampe più leggibili

with open("jpmorgan_example.json", "r", encoding="utf-8") as f:
    data = json.load(f)

fund_data = data["fundData"]

# --- Parsing settori ---
sectors = [
    {
        "name": item["name"],
        "value": item["value"],
        "secondaryValue": item["secondaryValue"],
        "tertiaryValue": item["tertiaryValue"]
    }
    for item in fund_data["emeaSectorBreakdown"]["data"]
]

# --- Parsing regioni ---
regions = [
    {
        "name": item["name"],
        "value": item["value"],
        "secondaryValue": item["secondaryValue"],
        "tertiaryValue": item["tertiaryValue"]
    }
    for item in fund_data["emeaRegionalBreakdown"]["data"]
]

# --- Parsing holdings ---
holdings = [
    {
        "securityDescription": item["securityDescription"],
        "ticker": item["securityTicker"],
        "isin": item["securityIsin"],
        "country": item["country"],
        "marketValue": item["marketValue"],
        "marketValuePercent": item["marketValuePercent"]
    }
    for item in fund_data["dailyHoldingsAll"]["data"]
]

# --- Stampa ---
print("\n\n\n\n\n📊 SETTORI")
pprint(sectors)

print("\n\n\n\n\n🌍 REGIONI")
pprint(regions)

print("\n\n\n\n\n💼 HOLDINGS")
pprint(holdings)