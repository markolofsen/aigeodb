import pytest

from aigeodb import DatabaseManager


@pytest.fixture
def db():
    return DatabaseManager()


def test_database_connection(db):
    """Test that database connection works"""
    stats = db.get_statistics()
    assert isinstance(stats, dict)
    assert "countries" in stats
    assert stats["countries"] > 0


def test_search_cities(db):
    """Test city search functionality"""
    cities = db.search_cities("Moscow", limit=1)
    assert len(cities) > 0
    assert cities[0].name == "Moscow"


def test_get_country_info(db):
    """Test country info retrieval"""
    country = db.get_country_info("US")
    assert country is not None
    assert country["name"] == "United States"
    assert country["iso2"] == "US"


def test_nearby_cities(db):
    """Test nearby cities search"""
    # New York coordinates
    cities = db.get_nearby_cities(40.7128, -74.0060, radius_km=100, limit=5)
    assert len(cities) > 0


if __name__ == "__main__":
    pytest.main()
    