# AigeoDB

A Python package for working with world cities, countries, regions database. This package provides easy access to a comprehensive database of world locations.

## About

Developed by [Unrealos Inc.](https://unrealos.com/) - We create innovative SaaS and PaaS solutions powered by AI for business. Our expertise includes:
- AI-powered business solutions
- SaaS platforms
- PaaS infrastructure
- Custom enterprise software

## Features

- Easy-to-use interface for querying geographical data
- Built-in database downloader and updater
- Support for searching cities, countries, and regions
- Geolocation features (nearby cities search)
- SQLAlchemy models for all database entities
- Django integration with custom model fields

## Installation

```bash
pip install aigeodb
```

## Core Usage

### Basic Example

```python
from aigeodb import DatabaseManager

# Initialize the database manager
db = DatabaseManager()

# Search for cities
cities = db.search_cities("Moscow", limit=5)
for city in cities:
    print(f"{city.name}, {city.country_code}")

# Get country information
country = db.get_country_info("US")
print(country.name, country.iso2)

# Find nearby cities
nearby = db.get_nearby_cities(40.7128, -74.0060, radius_km=100)
for city in nearby:
    print(f"{city.name}, {city.state_code}")
```

### API Reference

```python
# DatabaseManager methods
db = DatabaseManager()

# Search cities by name
cities = db.search_cities("Moscow", limit=5)

# Get country information
country = db.get_country_info("US")

# Find nearby cities (simple usage)
cities = db.get_nearby_cities(
    latitude=40.7128, 
    longitude=-74.0060,
    radius_km=100,
    limit=10
)
for city in cities:
    print(f"{city.name}, {city.state_code}")

# Find nearby cities with distances
cities_with_distances = db.get_nearby_cities(
    latitude=40.7128,
    longitude=-74.0060,
    radius_km=100,
    limit=10,
    with_distance=True
)
for city, distance in cities_with_distances:
    print(f"{city.name}: {distance:.1f}km")

# Get cities by country
cities = db.get_cities_by_country("US")

# Get states/regions by country
states = db.get_states_by_country("US")

# Get database statistics
stats = db.get_statistics()
```

### Database Content

The package includes:
- Countries (250 records)
- Regions (6 records)
- Subregions (22 records)
- States/Regions/Municipalities (5,038 records)
- Cities/Towns/Districts (151,072 records)

## Django Integration

If you're using Django, AigeoDB provides custom model fields with autocomplete support.

### Setup

1. Add to INSTALLED_APPS:
```python
INSTALLED_APPS = [
    ...
    'aigeodb.django',
]
```

2. Add URLs:
```python
from django.urls import path, include

urlpatterns = [
    ...
    path('', include('aigeodb.django.urls')),  # URLs already include 'aigeodb/' prefix
]
```

### Using Fields

```python
from django.db import models
from aigeodb.django.fields import CityField, CountryField

class Location(models.Model):
    # Required fields
    city = CityField()
    country = CountryField()
    
    # Optional fields
    optional_city = CityField(null=True, blank=True)
    optional_country = CountryField(null=True, blank=True)
```

### Admin Integration

```python
from django.contrib import admin

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('get_city_name', 'get_country_name', 'get_optional_city_name')
    search_fields = ('city', 'country', 'optional_city', 'optional_country')
    
    def get_city_name(self, obj):
        city_data = obj.city.get_data()
        return f"{city_data['name']}, {city_data['country_code']}"
    
    def get_country_name(self, obj):
        country_data = obj.country.get_data()
        return country_data['name']
        
    def get_optional_city_name(self, obj):
        if obj.optional_city:
            city_data = obj.optional_city.get_data()
            return f"{city_data['name']}, {city_data['country_code']}"
        return '-'
    
    get_city_name.short_description = 'City'
    get_country_name.short_description = 'Country'
    get_optional_city_name.short_description = 'Optional City'
```

## License

MIT License - see the LICENSE file for details.

## Credits

- Data source: [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database)
- Developed by [Unrealos Inc.](https://unrealos.com/)
