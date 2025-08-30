import requests
import yfinance as yf

# Crea una sessione con User-Agent "da browser"
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36"
})

# ticker = "AAPL"
ticker = "SSAC.L"
stock = yf.Ticker(ticker, session=session)

info = stock.info
# shares = stock.shares
# print(f"aaaaaaAA: {shares}")

print(info.get("longName"))
print(stock.history(period="1mo").tail())

for k, v in info.items():
    print(k, ":", v)

# import requests
# import yfinance as yf
#
# # Creo la sessione con User-Agent
# session = requests.Session()
# session.headers.update({
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36"
# })
#
# # Patch globale: sostituisco la sessione di yfinance
# yf.shared._requests = session
#
# ticker = "AAPL"
# stock = yf.Ticker(ticker)
#
# print(stock.info.get("longName"))