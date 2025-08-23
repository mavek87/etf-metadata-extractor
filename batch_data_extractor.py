import os
import subprocess

from file_utils import find_csv_files

# Nome dello script principale
MAIN_SCRIPT = "ishares_data_extractor.py"

# Cartella di input (stessa che usi nello script principale)
INPUT_FOLDER = os.path.join("input")

def main():
    if not os.path.exists(INPUT_FOLDER):
        print(f"❌ La cartella {INPUT_FOLDER} non esiste.")
        return

    csv_files = find_csv_files(INPUT_FOLDER)

    if not csv_files:
        print("⚠️ Nessun file CSV trovato nella cartella input.")
        return

    print(f"🔍 Trovati {len(csv_files)} file CSV da processare.")

    for csv_file in csv_files:
        # Prefisso senza estensione (ISIN)
        isin_prefix = os.path.splitext(csv_file)[0]

        print(f"\n➡️  Processando {csv_file} (ISIN: {isin_prefix})...")
        try:
            # Richiama lo script principale passando l’ISIN come argomento
            subprocess.run(
                ["python", MAIN_SCRIPT, isin_prefix],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Errore durante l'elaborazione di {csv_file}: {e}")


if __name__ == "__main__":
    main()
