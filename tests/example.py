from src.aigeodb import DatabaseManager


def main():
    # Initialize the database manager
    db = DatabaseManager()

    # Example 1: Get statistics
    print("\nDatabase Statistics:")
    print("===================")
    stats = db.get_statistics()
    for entity, count in stats.items():
        print(f"{entity.capitalize()}: {count:,}")

    # Example 2: Search cities
    print("\nSearching for 'Moscow':")
    print("======================")
    cities = db.search_cities("Moscow", limit=5)
    for city in cities:
        print(f"{city.name}, {city.country_code} ({city.latitude}, {city.longitude})")

    # Example 3: Get country info
    print("\nCountry Info for US:")
    print("===================")
    us_info = db.get_country_info("US")
    if us_info:
        for key, value in us_info.items():
            print(f"{key}: {value}")

    # Example 4: Get nearby cities (near New York)
    print("\nCities near New York:")
    print("====================")
    nearby = db.get_nearby_cities(40.7128, -74.0060, radius_km=100, limit=5)
    for city in nearby:
        print(f"{city.name}, {city.state_code} ({city.latitude}, {city.longitude})")

    # Example 5: Get all states in a country
    print("\nStates in Canada:")
    print("================")
    canada_states = db.get_states_by_country("CA")
    for state in canada_states:
        print(f"{state.name} ({state.iso2})")


if __name__ == "__main__":
    main()
