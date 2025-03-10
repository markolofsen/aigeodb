# AigeoDB

A Python package for working with world cities, countries, regions database. This package provides easy access to a comprehensive database of world locations including cities, countries, regions, subregions, and states.

## Features

- Easy-to-use interface for querying geographical data
- Built-in database downloader and updater
- Support for searching cities, countries, and regions
- Geolocation features (nearby cities search)
- SQLAlchemy models for all database entities

## Installation

```bash
pip install aigeodb
```

## Quick Start

```python
from aigeodb import DatabaseManager

# Initialize the database manager
db = DatabaseManager()

# Search for cities
cities = db.search_cities("Moscow", limit=5)
for city in cities:
    print(f"{city.name}, {city.country_code}")

# Get country information
country_info = db.get_country_info("US")
print(country_info)

# Find nearby cities
nearby = db.get_nearby_cities(40.7128, -74.0060, radius_km=100)
for city in nearby:
    print(f"{city.name}, {city.state_code}")
```

## Database Structure

The package includes the following data:
- Countries (250 records)
- Regions (6 records)
- Subregions (22 records)
- States/Regions/Municipalities (5,038 records)
- Cities/Towns/Districts (151,072 records)

## Updating Database

To update the database to the latest version:

```python
from aigeodb import DatabaseDownloader

downloader = DatabaseDownloader()
downloader.update_databases()
```

## API Reference

### DatabaseManager

Main class for interacting with the database:

```python
# Initialize
db = DatabaseManager()

# Available methods
db.search_cities(term, limit=10)
db.get_country_info(country_code)
db.get_nearby_cities(latitude, longitude, radius_km=100)
db.get_cities_by_country(country_code)
db.get_states_by_country(country_code)
db.get_statistics()
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

This package uses data from [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database) repository.
