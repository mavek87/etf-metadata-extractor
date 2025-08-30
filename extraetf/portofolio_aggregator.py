import json
import os
from collections import defaultdict
from typing import Dict

import pandas as pd


class PortfolioAggregator:
    def __init__(self, data_dir: str = "./data"):
        """
        Inizializza l'aggregatore di portafoglio.

        Args:
            data_dir: Directory contenente i file JSON degli ETF
        """
        self.data_dir = data_dir
        self.etf_data = {}

    def load_etf_data(self) -> None:
        """Carica tutti i file JSON dalla directory data."""
        if not os.path.exists(self.data_dir):
            raise FileNotFoundError(f"Directory {self.data_dir} non trovata")

        json_files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]

        if not json_files:
            raise FileNotFoundError(f"Nessun file JSON trovato in {self.data_dir}")

        print(f"Caricamento di {len(json_files)} file ETF...")

        for filename in json_files:
            isin = filename.replace('.json', '')
            filepath = os.path.join(self.data_dir, filename)

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Estrai i dati del portfolio breakdown
                if 'results' in data and len(data['results']) > 0:
                    portfolio_data = data['results'][0].get('portfolio_breakdown', {})
                    self.etf_data[isin] = portfolio_data
                    print(f"✓ Caricato {isin}")
                else:
                    print(f"⚠ Dati mancanti per {isin}")

            except Exception as e:
                print(f"✗ Errore nel caricamento di {filename}: {e}")

    def aggregate_portfolio(self, portfolio_weights: Dict[str, float]) -> Dict:
        """
        Aggrega i dati del portafoglio in base alle percentuali.

        Args:
            portfolio_weights: Dict con ISIN come chiave e percentuale come valore
            Esempio: {"IE00BZ56SW52": 30.0, "IE00B4L5Y983": 55.0, "IE00B3XXRP09": 15.0}

        Returns:
            Dict con i dati aggregati
        """
        # Verifica che le percentuali sommino a 100
        total_weight = sum(portfolio_weights.values())
        if abs(total_weight - 100.0) > 0.01:
            print(f"⚠ Attenzione: le percentuali sommano a {total_weight}% invece di 100%")

        # Converti percentuali in decimali
        weights = {isin: weight / 100.0 for isin, weight in portfolio_weights.items()}

        # Inizializza le strutture per l'aggregazione
        aggregated_data = {
            'esposizione_settoriale': defaultdict(float),
            'esposizione_geografica': defaultdict(float),
            'holdings': defaultdict(float),
            'valute': defaultdict(float)
        }

        print("\n=== AGGREGAZIONE DATI ===")

        for isin, weight in weights.items():
            if isin not in self.etf_data:
                print(f"⚠ Dati non trovati per ISIN {isin}")
                continue

            etf_data = self.etf_data[isin]
            print(f"Processando {isin} (peso: {weight * 100:.1f}%)")

            # 1. ESPOSIZIONE SETTORIALE
            sector_data = etf_data.get('global_stock_exposure_list', [])
            for sector in sector_data:
                sector_name = sector.get('name', 'Sconosciuto')
                sector_value = sector.get('value', 0)
                aggregated_data['esposizione_settoriale'][sector_name] += sector_value * weight

            # 2. ESPOSIZIONE GEOGRAFICA
            country_data = etf_data.get('country_stocks_exposure_list', [])
            for country in country_data:
                country_name = country.get('name', 'Sconosciuto')
                country_value = country.get('value', 0)
                aggregated_data['esposizione_geografica'][country_name] += country_value * weight

            # 3. HOLDINGS (singole azioni)
            holdings_data = etf_data.get('items', [])
            for holding in holdings_data:
                holding_name = holding.get('name', 'Sconosciuto')
                holding_isin = holding.get('isin', '')
                holding_weight = holding.get('weight', 0)

                # Usa ISIN + Nome per identificare univocamente
                holding_key = f"{holding_name} ({holding_isin})" if holding_isin else holding_name
                aggregated_data['holdings'][holding_key] += holding_weight * weight

            # 4. VALUTE
            currency_data = etf_data.get('currency_allocations', [])
            for currency in currency_data:
                currency_name = currency.get('name', 'Sconosciuta')
                currency_value = currency.get('value', 0)
                aggregated_data['valute'][currency_name] += currency_value * weight

        # Converti defaultdict in dict normali e ordina per valore
        result = {}
        for category, data in aggregated_data.items():
            sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
            result[category] = sorted_data

        return result

    import json
import os
from typing import Dict, List
from collections import defaultdict
import pandas as pd

class PortfolioAggregator:
    def __init__(self, data_dir: str = "./data"):
        """
        Inizializza l'aggregatore di portafoglio.

        Args:
            data_dir: Directory contenente i file JSON degli ETF
        """
        self.data_dir = data_dir
        self.etf_data = {}

    def load_etf_data(self) -> None:
        """Carica tutti i file JSON dalla directory data."""
        if not os.path.exists(self.data_dir):
            raise FileNotFoundError(f"Directory {self.data_dir} non trovata")

        json_files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]

        if not json_files:
            raise FileNotFoundError(f"Nessun file JSON trovato in {self.data_dir}")

        print(f"Caricamento di {len(json_files)} file ETF...")

        for filename in json_files:
            isin = filename.replace('.json', '')
            filepath = os.path.join(self.data_dir, filename)

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Estrai i dati del portfolio breakdown
                if 'results' in data and len(data['results']) > 0:
                    portfolio_data = data['results'][0].get('portfolio_breakdown', {})
                    self.etf_data[isin] = portfolio_data
                    print(f"✓ Caricato {isin}")
                else:
                    print(f"⚠ Dati mancanti per {isin}")

            except Exception as e:
                print(f"✗ Errore nel caricamento di {filename}: {e}")

    def aggregate_portfolio(self, portfolio_weights: Dict[str, float]) -> Dict:
        """
        Aggrega i dati del portafoglio in base alle percentuali.

        Args:
            portfolio_weights: Dict con ISIN come chiave e percentuale come valore
            Esempio: {"IE00BZ56SW52": 30.0, "IE00B4L5Y983": 55.0, "IE00B3XXRP09": 15.0}

        Returns:
            Dict con i dati aggregati
        """
        # Verifica che le percentuali sommino a 100
        total_weight = sum(portfolio_weights.values())
        if abs(total_weight - 100.0) > 0.01:
            print(f"⚠ Attenzione: le percentuali sommano a {total_weight}% invece di 100%")

        # Converti percentuali in decimali
        weights = {isin: weight/100.0 for isin, weight in portfolio_weights.items()}

        # Inizializza le strutture per l'aggregazione
        aggregated_data = {
            'esposizione_settoriale': defaultdict(float),
            'esposizione_geografica': defaultdict(float),
            'holdings': defaultdict(float),
            'valute': defaultdict(float)
        }

        print("\n=== AGGREGAZIONE DATI ===")

        for isin, weight in weights.items():
            if isin not in self.etf_data:
                print(f"⚠ Dati non trovati per ISIN {isin}")
                continue

            etf_data = self.etf_data[isin]
            print(f"Processando {isin} (peso: {weight*100:.1f}%)")

            # 1. ESPOSIZIONE SETTORIALE
            sector_data = etf_data.get('global_stock_exposure_list', [])
            for sector in sector_data:
                sector_name = sector.get('name', 'Sconosciuto')
                sector_value = sector.get('value', 0)
                aggregated_data['esposizione_settoriale'][sector_name] += sector_value * weight

            # 2. ESPOSIZIONE GEOGRAFICA
            country_data = etf_data.get('country_stocks_exposure_list', [])
            for country in country_data:
                country_name = country.get('name', 'Sconosciuto')
                country_value = country.get('value', 0)
                aggregated_data['esposizione_geografica'][country_name] += country_value * weight

            # 3. HOLDINGS (singole azioni)
            holdings_data = etf_data.get('items', [])
            for holding in holdings_data:
                holding_name = holding.get('name', 'Sconosciuto')
                holding_isin = holding.get('isin', '')
                holding_weight = holding.get('weight', 0)

                # Usa ISIN + Nome per identificare univocamente
                holding_key = f"{holding_name} ({holding_isin})" if holding_isin else holding_name
                aggregated_data['holdings'][holding_key] += holding_weight * weight

            # 4. VALUTE
            currency_data = etf_data.get('currency_allocations', [])
            for currency in currency_data:
                currency_name = currency.get('name', 'Sconosciuta')
                currency_value = currency.get('value', 0)
                aggregated_data['valute'][currency_name] += currency_value * weight

        # Converti defaultdict in dict normali e ordina per valore
        result = {}
        for category, data in aggregated_data.items():
            sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
            result[category] = sorted_data

        return result

    def print_results(self, aggregated_data: Dict) -> None:
        """Stampa i risultati aggregati in formato leggibile."""
        print("\n" + "="*60)
        print("RISULTATI AGGREGAZIONE PORTAFOGLIO")
        print("="*60)

        # 1. ESPOSIZIONE SETTORIALE
        print("\n🏭 ESPOSIZIONE SETTORIALE:")
        print("-" * 40)
        sector_total = 0
        for sector, percentage in aggregated_data['esposizione_settoriale']:
            print(f"{sector:<30} {percentage:>8.2f}%")
            sector_total += percentage
        print("-" * 40)
        print(f"{'TOTALE':<30} {sector_total:>8.2f}%")

        # 2. ESPOSIZIONE GEOGRAFICA
        print("\n🌍 ESPOSIZIONE GEOGRAFICA:")
        print("-" * 40)
        country_total = 0
        for country, percentage in aggregated_data['esposizione_geografica']:
            print(f"{country:<30} {percentage:>8.2f}%")
            country_total += percentage
        print("-" * 40)
        print(f"{'TOTALE':<30} {country_total:>8.2f}%")

        # 3. TOP HOLDINGS (mostra solo i primi 20)
        print("\n💼 TOP 20 HOLDINGS:")
        print("-" * 60)
        holdings_total = 0
        holdings_shown = 0
        for i, (holding, percentage) in enumerate(aggregated_data['holdings'][:20], 1):
            print(f"{i:2d}. {holding:<45} {percentage:>8.2f}%")
            holdings_total += percentage
            holdings_shown += 1

        # Calcola il totale di TUTTI gli holdings (non solo i top 20)
        all_holdings_total = sum(percentage for _, percentage in aggregated_data['holdings'])

        if len(aggregated_data['holdings']) > 20:
            remaining_total = all_holdings_total - holdings_total
            print(f"\n... e altri {len(aggregated_data['holdings']) - 20} holdings ({remaining_total:.2f}%)")

        print("-" * 60)
        print(f"{'TOTALE (tutti gli holdings)':<47} {all_holdings_total:>8.2f}%")

        # 4. VALUTE
        print("\n💱 ESPOSIZIONE VALUTARIA:")
        print("-" * 40)
        currency_total = 0
        for currency, percentage in aggregated_data['valute']:
            print(f"{currency:<30} {percentage:>8.2f}%")
            currency_total += percentage
        print("-" * 40)
        print(f"{'TOTALE':<30} {currency_total:>8.2f}%")


    def save_to_csv(self, aggregated_data: Dict, output_dir: str = "./portfolio_analysis") -> None:
        """Salva i risultati in file CSV separati."""
        os.makedirs(output_dir, exist_ok=True)

        for category, data in aggregated_data.items():
            df = pd.DataFrame(data, columns=['Nome', 'Percentuale'])
            filename = os.path.join(output_dir, f"{category}.csv")
            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"✓ Salvato: {filename}")


def main():
    """Esempio di utilizzo dello script."""

    # Inizializza l'aggregatore
    aggregator = PortfolioAggregator(data_dir="./data")

    # Carica i dati degli ETF
    aggregator.load_etf_data()

    # DEFINISCI QUI LE PERCENTUALI DEL TUO PORTAFOGLIO
    # Sostituisci con i tuoi ISIN e percentuali
    portfolio_composition = {
        "FR0013416716": 6.11,
        "IE000OEF25S1": 1.63,
        "IE00B579F325": 4.30,
        "IE00BK5BQT80": 7.93,
        "IE00B6R52259": 7.76,
        "IE000XZSV718": 3.31,
        "IE00B5L8K969": 1.51,
        "IE00BSPLC413": 0.26,
        "IE00BKM4GZ66": 0.53,
        "IE0006WW1TQ4": 1.82,
        "IE00B8GKDB10": 2.14,
        "IE00BP3QZ825": 3.62,
        "DE000A0F5UH1": 1.43,
        "LU0290358497": 13.58,
        "LU2233156582": 3.50,
        "IE00B3YLTY66": 7.36,
        "IE00BDBRDM35": 3.46,
        "LU1650491282": 3.44,
        "IE00BZ56SW52": 2.62,
        "LU1109943388": 0.36,
        "IE00BF4G6Y48": 3.34,
        "IE000U9J8HX9": 1.71,
        "LU0292096186": 1.38,
        "IE00BJ0KDR00": 2.23,
        "IE00BH04GL39": 6.75,
        "XS2940466316": 3.32,
        "IE00BL25JL35": 3.28,
        "IE00BM67HK77": 1.32
    }

    # XEON reale LU0290358497 = 7.80%
    # Somma percentuale = 94.22% quindi per 100% aggiungo 5,78% a XEON (100%-94,22%) cosi XEON diventa 7,80% + 5,78% = 13,58%

    print(f"\nComposizione portafoglio:")
    for isin, percentage in portfolio_composition.items():
        print(f"  {isin}: {percentage}%")

    # Aggrega i dati
    aggregated_results = aggregator.aggregate_portfolio(portfolio_composition)

    # Mostra i risultati
    aggregator.print_results(aggregated_results)

    # Salva in CSV (opzionale)
    try:
        aggregator.save_to_csv(aggregated_results)
        print(f"\n✓ File CSV salvati in ./portfolio_analysis/")
    except ImportError:
        print("\n⚠ pandas non disponibile - file CSV non salvati")
    except Exception as e:
        print(f"\n✗ Errore nel salvataggio CSV: {e}")


if __name__ == "__main__":
    main()
