import requests
import os
from pathlib import Path
import time
from urllib.parse import urlparse

def download_etf_files(isin_list, download_folder="etf_downloads", delay=1):
    """
    Scarica i file Excel/CSV degli ETF Xtrackers per una lista di ISIN

    Args:
        isin_list (list): Lista di codici ISIN
        download_folder (str): Cartella di destinazione per i download
        delay (float): Pausa tra i download in secondi (per evitare rate limiting)
    """

    # URL base template
    base_url = "https://etf.dws.com/etfdata/export/GBR/ENG/excel/product/constituent/{isin}/"

    # Crea la cartella di download se non esiste
    Path(download_folder).mkdir(exist_ok=True)

    # Configura headers per simulare un browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,text/csv,*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    successful_downloads = []
    failed_downloads = []

    print(f"Inizio download per {len(isin_list)} ETF...")
    print(f"Cartella di destinazione: {os.path.abspath(download_folder)}")
    print("-" * 50)

    for i, isin in enumerate(isin_list, 1):
        # Costruisci l'URL sostituendo l'ISIN
        url = base_url.format(isin=isin)

        print(f"[{i}/{len(isin_list)}] Downloading {isin}...")
        print(f"URL: {url}")

        try:
            # Effettua la richiesta
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()  # Solleva eccezione per status HTTP di errore

            # Determina l'estensione del file dal Content-Type o usa xlsx come default
            content_type = response.headers.get('content-type', '').lower()
            if 'csv' in content_type:
                extension = 'csv'
            elif 'excel' in content_type or 'spreadsheet' in content_type:
                extension = 'xlsx'
            else:
                # Fallback: prova a determinare dall'header Content-Disposition
                content_disposition = response.headers.get('content-disposition', '')
                if '.csv' in content_disposition.lower():
                    extension = 'csv'
                else:
                    extension = 'xlsx'  # Default

            # Nome del file
            filename = f"{isin}.{extension}"
            filepath = os.path.join(download_folder, filename)

            # Salva il file
            with open(filepath, 'wb') as f:
                f.write(response.content)

            file_size = len(response.content)
            print(f"✓ Salvato: {filename} ({file_size:,} bytes)")
            successful_downloads.append(isin)

        except requests.exceptions.RequestException as e:
            print(f"✗ Errore nel download di {isin}: {e}")
            failed_downloads.append((isin, str(e)))

        except Exception as e:
            print(f"✗ Errore generico per {isin}: {e}")
            failed_downloads.append((isin, str(e)))

        # Pausa tra i download per evitare rate limiting
        if i < len(isin_list):  # Non fare pausa dopo l'ultimo download
            print(f"Pausa di {delay} secondi...")
            time.sleep(delay)

        print("-" * 30)

    # Riepilogo finale
    print("\n" + "=" * 50)
    print("RIEPILOGO DOWNLOAD")
    print("=" * 50)
    print(f"Download completati con successo: {len(successful_downloads)}")
    print(f"Download falliti: {len(failed_downloads)}")

    if successful_downloads:
        print(f"\n✓ ISIN scaricati con successo:")
        for isin in successful_downloads:
            print(f"  - {isin}")

    if failed_downloads:
        print(f"\n✗ ISIN con errori:")
        for isin, error in failed_downloads:
            print(f"  - {isin}: {error}")

    return successful_downloads, failed_downloads

# Esempio di utilizzo
if __name__ == "__main__":
    # Lista degli ISIN da scaricare
    isin_list = [
        "IE0006WW1TQ4",
        "LU0290358497",
        "LU0292096186",
        "IE00BJ0KDR00",
        "IE00BL25JL35",
        "IE00BM67HK77"
    ]

    # Avvia il download
    successful, failed = download_etf_files(
        isin_list=isin_list,
        download_folder="input/xtrackers",
        delay=2  # 2 secondi di pausa tra i download
    )

    print(f"\nScript completato. File salvati in: {os.path.abspath('etf_downloads')}")