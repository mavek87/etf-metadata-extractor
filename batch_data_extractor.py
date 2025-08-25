import json
import os
import subprocess

from file_utils import find_csv_files

# Script specifici per l'estrazione
ISHARES_SCRIPT = "ishares_data_extractor.py"
XTRACKERS_SCRIPT = "xtrackers_data_extractor.py"

# Percorso del file con la lista ISIN
ISIN_LIST_FILE = "isin_list.json"

# Cartelle di input
ISHARES_INPUT_FOLDER = os.path.join("input", "ishares")
XTRACKERS_INPUT_FOLDER = os.path.join("input", "xtrackers")

def load_isin_list():
    """Carica la lista degli ISIN dal file JSON."""
    if not os.path.exists(ISIN_LIST_FILE):
        raise FileNotFoundError(f"❌ Il file {ISIN_LIST_FILE} non esiste.")

    with open(ISIN_LIST_FILE, "r") as f:
        return json.load(f)

def process_files(input_folder, isin_list, script_name):
    """Elabora i file presenti nella cartella di input usando lo script specificato."""
    if not os.path.exists(input_folder):
        print(f"❌ La cartella {input_folder} non esiste.")
        return

    print(f"🔍 Cercando file nella cartella: {input_folder}")
    files_in_folder = {os.path.splitext(f)[0] for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))}
    files_to_process = set(isin_list).intersection(files_in_folder)

    if not files_to_process:
        print(f"⚠️ Nessun file da processare trovato in {input_folder}.")
        return

    print(f"✅ Trovati {len(files_to_process)} file da processare per {script_name}.")

    for isin in files_to_process:
        print(f"\n➡️  Processando {isin} con {script_name}...")
        try:
            subprocess.run(
                ["python", script_name, isin],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Errore durante l'elaborazione di {isin} con {script_name}: {e}")

def main():
    try:
        # Carica la lista degli ISIN
        isin_data = load_isin_list()
        ishares_isin = isin_data.get("ishares", [])
        xtrackers_isin = isin_data.get("xtrackers", [])

        # Processa iShares
        print("\n🧾 Elaborazione dei file iShares...")
        process_files(ISHARES_INPUT_FOLDER, ishares_isin, ISHARES_SCRIPT)

        # Processa Xtrackers
        print("\n🧾 Elaborazione dei file Xtrackers...")
        process_files(XTRACKERS_INPUT_FOLDER, xtrackers_isin, XTRACKERS_SCRIPT)

    except Exception as e:
        print(f"❌ Errore generale: {e}")


if __name__ == "__main__":
    main()
