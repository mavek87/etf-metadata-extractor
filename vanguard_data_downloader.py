import pandas as pd
import requests

url = "https://www.it.vanguard/gpx/graphql"

headers = {
    "content-type": "application/json",
    "origin": "https://www.it.vanguard",
    "referer": "https://www.it.vanguard/",
    "user-agent": "Mozilla/5.0",
    "apollographql-client-name": "gpx",
    "x-consumer-id": "it0"
}

payload = {
    "operationName": "MarketAllocationGqlQuery",
    "variables": {"portIds": ["9679"]},
    "query": """query MarketAllocationGqlQuery($portIds: [String!]!) {
      funds(portIds: $portIds) {
        profile {
          fundFullName
          marketOfDomicile
          __typename
        }
        marketAllocation {
          portId
          date
          countryCode
          countryName
          fundMktPercent
          holdingStatCode
          benchmarkMktPercent
          regionCode
          regionName
          __typename
        }
        __typename
      }
    }"""
}

# Settori

# ```json
# {operationName: "getSectorDiversification", variables: {portIds: ["9679"]},…}
# operationName
# :
# "getSectorDiversification"
# query
# :
# "query getSectorDiversification($portIds: [String!]!) {\n  funds(portIds: $portIds) {\n    profile {\n      primarySectorEquityClassification\n      __typename\n    }\n    sectorDiversification {\n      sectorCode\n      date\n      sectorName\n      fundPercent\n      benchmarkPercent\n      __typename\n    }\n    __typename\n  }\n}\n"
# variables
# :
# {portIds: ["9679"]}
# ```

resp = requests.post(url, headers=headers, json=payload)
data = resp.json()

# estraiamo la tabella marketAllocation
alloc = data["data"]["funds"][0]["marketAllocation"]
df = pd.DataFrame(alloc)

# esporta in CSV e XLSX
df.to_csv("market_allocation.csv", index=False)
df.to_excel("market_allocation.xlsx", index=False)

print("Salvati market_allocation.csv e market_allocation.xlsx")
