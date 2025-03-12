from src.aigeodb import DatabaseManager


def print_section(title: str):
    print(f"\n{title}")
    print("=" * len(title))


def main():
    # Initialize the database manager
    db = DatabaseManager()

    # Example 1: Get statistics
    print_section("Database Statistics")
    stats = db.get_statistics()
    for entity, count in stats.items():
        print(f"{entity.capitalize()}: {count:,}")

    # Example 2: Search methods
    print_section("Search Examples")

    print("\nSearching cities 'Moscow':")
    cities = db.search_cities("Moscow", limit=5)
    for city in cities:
        print(f"City: {city.name}, {city.state_code}, {city.country_code}")
        print(f"  Location: ({city.latitude}, {city.longitude})")
        print(f"  IDs: city_id={city.id}, state_id={city.state_id}, country_id={city.country_id}")

    print("\nSearching countries 'united':")
    countries = db.search_countries("united", limit=5)
    for country in countries:
        print(f"Country: {country.name} ({country.iso2}, {country.iso3})")
        print(f"  Capital: {country.capital}")
        print(f"  Region: {country.region}, Subregion: {country.subregion}")

    # Example 3: Get by ID methods
    print_section("Get by ID Examples")

    # Get city by ID (New York)
    nyc = db.get_city_by_id(99981)
    if nyc:
        print(f"\nCity by ID (99981):")
        print(f"Name: {nyc.name}, {nyc.state_code}, {nyc.country_code}")
        print(f"Location: ({nyc.latitude}, {nyc.longitude})")

    # Get country by ID (USA)
    usa = db.get_country_by_id(233)
    if usa:
        print(f"\nCountry by ID (233):")
        print(f"Name: {usa.name} ({usa.iso2}, {usa.iso3})")
        print(f"Capital: {usa.capital}")
        print(f"Currency: {usa.currency} ({usa.currency_symbol})")

    # Example 4: Get country info
    print_section("Country Info Example")
    us_info = db.get_country_info("US")
    if us_info:
        print("\nDetailed info for US:")
        for key, value in us_info.items():
            print(f"{key}: {value}")

    # Example 5: Get cities by country
    print_section("Cities and States by Country")
    print("\nFirst 5 cities in Japan:")
    japan_cities = db.get_cities_by_country("JP")
    for city in japan_cities[:5]:
        print(f"{city.name}, {city.state_code} ({city.latitude}, {city.longitude})")

    print("\nStates/Provinces in Canada:")
    canada_states = db.get_states_by_country("CA")
    for state in canada_states:
        print(f"{state.name} ({state.iso2 or 'no ISO code'})")
        print(f"  Type: {state.type or 'unspecified'}, Level: {state.level or 'unspecified'}")

    # Example 6: Get nearby cities
    print_section("Nearby Cities Example")
    print("\nCities within 50km of Tokyo (35.6762, 139.6503):")
    nearby = db.get_nearby_cities(35.6762, 139.6503, radius_km=50, limit=5)
    for city in nearby:
        print(f"{city.name}, {city.state_code} ({city.latitude}, {city.longitude})")

    # Example 7: Get all methods
    print_section("Get All Examples")

    print("\nFirst 5 countries:")
    all_countries = db.get_all_countries()
    for country in list(all_countries)[:5]:
        print(f"{country.name} ({country.iso2})")

    print("\nFirst 5 cities:")
    all_cities = db.get_all_cities()
    for city in list(all_cities)[:5]:
        print(f"{city.name}, {city.state_code}, {city.country_code}")


if __name__ == "__main__":
    main()
