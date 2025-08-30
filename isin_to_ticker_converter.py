import requests

url = "https://query2.finance.yahoo.com/v1/finance/search"
# params = {"q": "US1667641005", "quotesCount": 1, "newsCount": 0}

# Nvidia
# params = {"q": "US67066G1040", "quotesCount": 1, "newsCount": 0}

# VWCE
# params = {"q": "IE00BK5BQT80", "quotesCount": 1, "newsCount": 0}

# AMAZON
# params = {"q": "US0231351067", "quotesCount": 1, "newsCount": 0}

# ISAC
params = {"q": "IE00B6R52259", "quotesCount": 1, "newsCount": 0}

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36"}

r = requests.get(url, params=params, headers=headers)
print("Status:", r.status_code)
print("Text:", r.text)

if r.status_code == 200:
    data = r.json()
    if data.get("quotes"):
        print("Ticker:", data["quotes"][0]["symbol"])
        print("Name:", data["quotes"][0]["longname"])
    else:
        print("Nessun risultato per questo ISIN")
else:
    print("Errore HTTP:", r.status_code)
