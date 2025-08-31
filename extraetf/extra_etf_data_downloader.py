import requests
import json
import time
import os
from typing import List

def download_etf_data(isin_list: List[str], output_dir: str = "etf_data", delay: float = 1.0):
    """
    Scarica i dati degli ETF da ExtraETF per una lista di ISIN.

    Args:
        isin_list: Lista degli ISIN da processare
        output_dir: Directory dove salvare i file JSON (default: "etf_data")
        delay: Pausa in secondi tra una richiesta e l'altra (default: 1.0)
    """

    # Crea la directory di output se non esiste
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Creata directory: {output_dir}")

    base_url = "https://extraetf.com/api-v2/detail/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'it-IT,it;q=0.6',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }

    # Cookie fondamentale per la localizzazione italiana
    cookies = {
        'extraetf_locale': 'it'
    }

    successful_downloads = 0
    failed_downloads = 0

    print(f"Inizio download per {len(isin_list)} ISIN...")

    for i, isin in enumerate(isin_list, 1):
        try:
            # Costruisce l'URL per la richiesta
            url = f"{base_url}?isin={isin}&extraetf_locale=it"

            print(f"[{i}/{len(isin_list)}] Scaricando dati per ISIN: {isin}")
            print(f"URL: {url}")  # Debug: mostra l'URL completo

            # Crea una sessione per mantenere i cookies
            session = requests.Session()
            session.headers.update(headers)
            session.cookies.update(cookies)

            # Effettua la richiesta HTTP
            response = session.get(url, timeout=30)
            response.raise_for_status()  # Solleva un'eccezione per status code di errore

            print(f"Status Code: {response.status_code}")  # Debug

            # Controlla se la risposta contiene dati JSON validi
            json_data = response.json()

            # Salva il file JSON
            filename = f"{isin}.json"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

            print(f"✓ Salvato: {filepath}")
            successful_downloads += 1

        except requests.exceptions.RequestException as e:
            print(f"✗ Errore di rete per ISIN {isin}: {e}")
            failed_downloads += 1

        except json.JSONDecodeError as e:
            print(f"✗ Errore nel parsing JSON per ISIN {isin}: {e}")
            failed_downloads += 1

        except Exception as e:
            print(f"✗ Errore generico per ISIN {isin}: {e}")
            failed_downloads += 1

        # Pausa tra le richieste per essere rispettosi verso il server
        if i < len(isin_list):  # Non aspettare dopo l'ultima richiesta
            time.sleep(delay)

    # Riepilogo finale
    print(f"\n=== RIEPILOGO ===")
    print(f"Download completati con successo: {successful_downloads}")
    print(f"Download falliti: {failed_downloads}")
    print(f"File salvati in: {os.path.abspath(output_dir)}")

# Esempio di utilizzo
if __name__ == "__main__":
    # Lista di esempio di ISIN - sostituisci con i tuoi ISIN
    isin_list = [
        "FR0013416716",
        "IE000OEF25S1",
        "IE00B579F325",
        "IE00BK5BQT80",
        "IE00B6R52259",
        "IE000XZSV718",
        "IE00B5L8K969",
        "IE00BSPLC413",
        "IE00BKM4GZ66",
        "IE0006WW1TQ4",
        "IE00B8GKDB10",
        "IE00BP3QZ825",
        "DE000A0F5UH1",
        "LU0290358497",
        "LU2233156582",
        "IE00B3YLTY66",
        "IE00BDBRDM35",
        "LU1650491282",
        "IE00BZ56SW52",
        "LU1109943388",
        "IE00BF4G6Y48",
        "IE000U9J8HX9",
        "LU0292096186",
        "IE00BJ0KDR00",
        "IE00BH04GL39",
        "XS2940466316",
        "IE00BL25JL35",
        "IE00BM67HK77"
    ]

    # Tutti
    #    trading_currency_id (EURO, DOLLAR, ETC)

    # asset_class_name: Azioni
    #     asset_allocation_exposure_list (azioni, obbligazioni, altro)
    #     country_stocks_exposure_list (italia%, usa%, etc)
    #     country_convertible_exposure_list (vuoto ma forse presente?)
    #     currency_allocations (es. EUR 70%, USD 20%, ecc)
    #     region_stock_exposure_list (es. nord america, europa, ecc)
    #     region_convertible_exposure_list (vuoto ma forse puo essere presente?)
    #     global_bond_exposure_list (es. monetario%)
    #     global_stock_exposure_list (materiali base%, consumo ciclico%, immobiliare%, ecc)
    #     items (lista azioni incompleta!)

    # asset_class_name: Obbligazioni
    #     asset_allocation_exposure_list (azioni, obbligazioni, altro)
    #     country_bond_exposure_list (italia%, usa%, etc)
    #     country_convertible_exposure_list (italia%, usa%, etc)
    #     currency_allocations (es. EUR 70%, USD 20%, ecc)
    #     global_bond_exposure_list (tipi di bond es. governativi, corporate, high yield, ecc)
    #     region_bond_exposure_list (europe%, africa%, etc )
    #     region_convertible_exposure_list (europe%, africa%, etc )
    #     items (lista azioni incompleta!)

    # asset_class_name: Materie prime
    #       "guide_commodity": {
    #         "name": "Oro",
    #         "slug": "gold"
    #       },
    #       - "currency": "USD",
    #        - "fund_currency_id": "USD",
    #        - dentro chiave "items":
    #           "commodity_type_name": "Oro"
    #           "commodity_class_name": "Metalli preziosi",
    #        - "currency_allocations": [] (solo oro, in USD credo??)
    #     items (1 elemento solo, l'oro)

    # asset_class_name: Mercato monetario
    #   - "asset_allocation_exposure_list": "altro"
    #   - dentro chiave "items"
    #       "breakdown_type": "derivatives",
    #       "name": "TRS Solactive €STR +8.5 Daily TR EUR",
    #   - "currency": "EUR"
    #   - "fund_currency_id": "EUR"
    #   - "net_assets_currency": "EUR",
    #   - "currency_allocations" [] (sconosciuta.. in euro credo??)
    #     items (1 elemento solo, es. XEON)

    # asset_class_name: Criptovalute
    #    - "asset_allocation_exposure_list": "altro"
    #    - dentro chiave "items"
    #             "breakdown_type": "derivatives",
    #             "name": "Bitcoin",
    #    - "currency_allocations" [] (solo btc, in USD credo??)
    #    - "crypto_currency_name": "Bitcoin",
    #    - "fund_currency_id": "USD"
    #    - "currency": "USD",
    #    - "net_assets_currency": null
    #     items (1 elemento solo, es. Bitcoin)

    # Avvia il download
    # Puoi modificare output_dir e delay secondo le tue esigenze
    download_etf_data(
        isin_list=isin_list,
        output_dir="data",
        delay=2.0  # 2 secondi di pausa tra le richieste
    )
