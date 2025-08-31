import pytest

from geo_utils import GeoUtils

class TestGeoUtils:
    @pytest.mark.parametrize("code,expected", [
        ("IT", "Italy"),
        ("us", "United States"),
        ("BR", "Brazil"),
        ("xx", None),  # codice non valido
        ("", None),  # stringa vuota
    ])
    def test_get_country_name(self, code, expected):
        assert GeoUtils.get_country_name(code) == expected

    @pytest.mark.parametrize("code,expected", [
        ("IT", "Europa"),
        ("US", "Nord America"),
        ("BR", "America Latina"),
        ("AU", "Pacifico"),
        ("ZZ", None),  # codice non valido
        ("", None),  # stringa vuota
    ])
    def test_get_continent_name(self, code, expected):
        assert GeoUtils.get_continent_name(code) == expected

    def test_get_country_and_continent(self):
        result = GeoUtils.get_country_and_continent("IT")
        assert result == {"country": "Italy", "continent": "Europa"}

        result = GeoUtils.get_country_and_continent("xx")
        assert result == {"country": None, "continent": None}

    def test_invalid_continent_exception_handling(self):
        # Simula un errore interno forzando un input strano (esempio: None)
        assert GeoUtils.get_continent_name(None) is None
