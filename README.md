
# Idea progetto

L'obbiettivo del progetto è quello di estrarre i dati ufficiali dei principali ETF mondiali.
Nello specifico i dati che si vogliono estrarre per ciascun etf sono:

- Lista delle holdings e relative percentuali (es. Apple 2.5%, Microsoft 1.8% etc)
- Percentuali di settore (es. Tech 20%, Finance 15% etc)
- Percentuali di paese (es. USA 50%, UK 10% etc)
- Percentuali valuta (es. USD 60%, EUR 20% etc) (Non è detto che sia sempre possibile, alcuni emittenti non forniscono questo dato nei loro report. Non ricordo se SPDR o Vanguard)

Altri dati come ticker, TER, data di lancio, non sono al momento prioritari in quanto esistono già altre liste che li riportano. 
Al momento tutto sarà basato sugli ISIN degli ETF e l'obbiettivo sarà, dato un ISIN quello di fornire i dati elencati precedentemente.

Avendo a disposizione un db con tutti i dati precisi e ufficiali si potranno anche fornire delle API a pagamento visto che non sembra che in giro esistano servizi simili (o almeno non gratuiti).

# Problematiche

- Ciascun emittente di ETF ha un proprio sito web e una propria modalità di presentazione dei dati
- Alcuni emittenti forniscono i dati in formato csv, altri in formato xlsx
- Alcuni emittenti forniscono i dati in un unico file (lista delle holdings con possibilità di ottenere paesi e settori tramite aggregazioni) altri in file separati
- Alcuni emittenti forniscono i dati in modo statico, altri in modo dinamico (javascript) (Vanguard)

# Preferenze ottenimento dati

## Metodo 1: Tramite API ufficiali (se esistono)
- Se esistono API ufficiali, queste rappresentano il canale preferenziale.

## Metodo 2: Tramite download di file (csv/xlsx) ufficiali
### Opzione 2.1: Download automatizzato
- Automatizzazione del download (se possibile).
### Opzione 2.2: Download manuale
- Procedura manuale in caso non sia possibile automatizzare.

## Metodo 3: Tramite scraping
### Opzione 3.1: Scraping di siti ufficiali
- Raccogliere i dati direttamente dal sito ufficiale.
### Opzione 3.2: Scraping di siti di terze parti
- Ad esempio, justetf.com (solo se il sito ufficiale non è disponibile).

# Task del progetto

1. ottenere i dati ufficiali per ciascun etf (file csv/xlsx o scraping)
2. estrarre i dati rilevanti in seguito di eventuali elaborazioni (aggregazioni, calcoli etc)
3. normalizzare i dati in modo uniforme nonostante le differenze di formato tra i vari emittenti
4. memorizzare i dati in un database in modo normalizzato
5. fornire reportistica e analisi sui dati raccolti (funzione aggiuntiva che può essere fatta in un secondo momento una volta che il db è popolato)

# Componenti del progetto

1. Script di scraping per ciascun emittente (es. ishares.py, vanguard.py, spdr.py etc)
2. Script di automatizzazione dello scraping iterando per ciascun emittente e per ciascun prodotto di ciascun emittente (se possibile, altrimenti qualcosa va fatto manualmente)
3. Test di validazione dei dati raccolti
4. Script di normalizzazione dei dati raccolti
5. Script di salvataggio dei dati nel database
6. Scheduler per eseguire tutto il processo di scraping periodicamente (es. ogni giorno/settimana)

## Dependency installation:

```bash
pip install -r requirements.txt
```

https://www.ishares.com/uk/professional/en/products/264659/?referrer=tickerSearch
https://www.ishares.com/us/products/etf-investments#/?productView=etf&pageNumber=1&sortColumn=totalNetAssets&sortDirection=desc&dataView=keyFacts

## Scraping rules

To collect correct data, it is important to use official csv files provided by the ETF providers. Below are the rules for each provider.

## Extra-ETF useful data

https://extraetf.com/api-v2/detail/?isin=IE00BZ56SW52&extraetf_locale=it
https://extraetf.com/api-v2/detail/?isin=IE00BZ56SW52&extraetf_locale=en

using the ISIN is possible to find all the info about an ETF on extra-etf. The data are not always updated but it could be useful if it's not possibile to find them on the official website of the ETF provider.

## Morningstar 

ISIN is not used. this is complicated to use...

Holdings:
https://api-global.morningstar.com/sal-service/v1/etf/portfolio/v2/sector/0P0001RTKE/data?languageId=it&locale=it&clientId=MDC&benchmarkId=prospectus_primary&component=sal-mip-sector-exposure&version=4.69.0

Factors:
https://api-global.morningstar.com/sal-service/v1/etf/factorProfile/0P0001RTKE/data?languageId=it&locale=it&clientId=MDC&benchmarkId=prospectus_primary&component=sal-mip-factor-profile&version=4.69.0

### iShares

- Format: List of ETFs
- Scraping rule: -

### Vanguard

- Format:
- Scraping rule: no rule and js also hide the url to download the csv file

### SPDR

### Amundi

### Xtrackers

- Format: List of ETFs
- Scraping rule: It is possible to build the download URL of the xlxs file from the ETF ISIN. Example:
  - ISIN: IE00BJ0KDQ92
  - URL: https://etf.dws.com/etfdata/export/GBR/ENG/excel/product/constituent/IE00BJ0KDQ92/

### Invesco

https://dng-api.invesco.com/cache/v1/accounts/it_IT/shareclasses/IE000OEF25S1/holdings/index?idType=isin
https://dng-api.invesco.com/cache/v1/accounts/it_IT/shareclasses/IE000OEF25S1/weightedHoldings/fund?idType=isin&breakdown=sector&audienceType=Financial%20Professional&productType=ETF
https://dng-api.invesco.com/cache/v1/accounts/it_IT/shareclasses/IE000OEF25S1/weightedHoldings/fund?idType=isin&breakdown=country&audienceType=Financial%20Professional&productType=ETF

### JPMorgan

- List of all the ETFs: https://am.jpmorgan.com/FundsMarketingHandler/fund-explorer-label?country=it&language=it&version=8.15_1755008531

- All the json data: https://am.jpmorgan.com/FundsMarketingHandler/product-data?cusip=IE00BF4G6Y48&country=it&role=per&language=it&userLoggedIn=false&version=8.15_1755008531
  - key: emeaRegionalBreakdown -> regions
  - key: emeaSectorBreakdown -> sectors
  - key: dailyHoldingsAll -> holdings

- report (probably useless): https://am.jpmorgan.com/FundsMarketingHandler/excel?type=dailyETFHoldings&cusip=IE00BF4G6Y48&country=it&role=per&fundType=N_ETF&locale=it-IT&isUnderlyingHolding=false&isProxyHolding=false

### Fidelity

https://www.fidelity-italia.it/xapi/fund/portfolio/download/fundFullHolding?id=IE00BYXVGZ48&countries=it&country=it&languages=it%2Cen&language=it&channels=ce.private-investor%2Cce.professional-investor&channel=ce.professional-investor&r=1756198976642

sector and regions: at the moment any URL found. They can be found scraping the web page.

### WisdomTree

List of all etfs: https://dataspanapi.wisdomtree.com/pdr/documents/EMT/ETP/EU/EN-GB/EMT-V42/

similar to vanguard but even worst because the url to download the csv file is hidden in js code
sector and regions: at the moment any URL found. They can be found scraping the web page.

List of all holdings for GGRA (probably the ID is internal, they don't use ISIN in the URL):
https://www.wisdomtree.eu/it-it/global/etf-details/modals/all-holdings?id={213E2975-10D2-4521-B1CE-DB445F02AB16}

List holdings structure:
Name, Isin, Country Code, Weight

No sector. But it could be aggregated from the holdings using their ISIN. Otherwise, they can be scraped from the the ETF html page.

### VanEck

similar to vanguard but even worst because the url to download the csv file is hidden in js code
sector and regions: at the moment any URL found. They can be found scraping the web page.

### HSBC

https://www.assetmanagement.hsbc.it/it/api/v1/download/document/ie00b5l01s80/it/it/holdings

no sector. Could be scraped but it's not easy

### Franklin Templeton

similar to vanguard but even worst because the url to download the csv file is hidden in js code

### UBS

### Pimco

### L&G

### BNP

### Ossiam


# alternative site to download sectors and other data

https://global.morningstar.com/it/investimenti/etf/0P0001BJX7/portafoglio

