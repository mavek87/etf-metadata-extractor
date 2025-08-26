import requests

url = "https://query2.finance.yahoo.com/v1/finance/search"
params = {"q": "US1667641005", "quotesCount": 1, "newsCount": 0}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36"}

r = requests.get(url, params=params, headers=headers)
print("Status:", r.status_code)
print("Text:", r.text[:200])

if r.status_code == 200:
    data = r.json()
    if data.get("quotes"):
        print("Ticker:", data["quotes"][0]["symbol"])
    else:
        print("Nessun risultato per questo ISIN")
else:
    print("Errore HTTP:", r.status_code)
