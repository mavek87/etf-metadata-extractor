import pycountry
import pycountry_convert as pc
from typing import Optional, Dict

class GeoUtils:
    """
    Classe di utilità per la gestione di codici ISO di paesi
    e la conversione in nomi di paesi e continenti (in italiano).
    """

    # Mappa da continenti inglesi -> categorie italiane personalizzate
    CONTINENT_MAP_IT: Dict[str, str] = {
        "Europe": "Europa",
        "Asia": "Asia",
        "North America": "Nord America",
        "South America": "America Latina",
        "Africa": "Africa",
        "Oceania": "Pacifico",
        "Antarctica": "Antartide"
    }

    @classmethod
    def get_country_name(cls, code: str) -> Optional[str]:
        """
        Restituisce il nome di un paese dato il suo codice ISO alpha-2.
        Esempio: 'IT' -> 'Italy'
        """
        try:
            country = pycountry.countries.get(alpha_2=code.upper())
            return country.name if country else None
        except AttributeError:
            return None

    @classmethod
    def get_continent_name(cls, country_code: str) -> Optional[str]:
        """
        Restituisce il nome del continente in italiano
        dato il codice ISO alpha-2 del paese.
        Esempio: 'IT' -> 'Europa'
        """
        try:
            code = country_code.upper()
            continent_code = pc.country_alpha2_to_continent_code(code)
            continent_name = pc.convert_continent_code_to_continent_name(continent_code)
            return cls.CONTINENT_MAP_IT.get(continent_name, continent_name)
        except Exception:
            return None

    @classmethod
    def get_country_and_continent(cls, code: str) -> Dict[str, Optional[str]]:
        """
        Restituisce un dizionario con nome del paese e continente.
        Esempio: 'IT' -> {'country': 'Italy', 'continent': 'Europa'}
        """
        return {
            "country": cls.get_country_name(code),
            "continent": cls.get_continent_name(code)
        }