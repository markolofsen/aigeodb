# AigeoDB

A Python package for working with world cities, countries, regions database. This package provides easy access to a comprehensive database of world locations.

## Features

- Easy-to-use interface for querying geographical data
- Built-in database downloader and updater
- Support for searching cities, countries, and regions
- Geolocation features (nearby cities search)
- SQLite database with Peewee ORM
- Django integration with custom model fields
- Robust date handling and data validation
- Snake case field names with backward compatibility

## Installation

Basic installation:
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
    print(f"Location: ({city.latitude}, {city.longitude})")
    print(f"State: {city.state_code}")

# Get country information
country = db.get_country_info("US")
print(f"{country['name']} ({country['iso2']})")
print(f"Capital: {country['capital']}")
print(f"Currency: {country['currency']} ({country['currency_symbol']})")

# Find nearby cities
cities = db.get_nearby_cities(
    latitude=40.7128,
    longitude=-74.0060,
    radius_km=100,
    limit=10
)
for city in cities:
    print(f"{city.name}, {city.state_code} ({city.latitude}, {city.longitude})")
```

### Data Models

All models use snake_case field names with aliases for backward compatibility:

```python
# City model fields
city = cities[0]
print(f"ID: {city.id}")
print(f"Name: {city.name}")
print(f"State ID: {city.state_id}")  # aliased as 'state' in database
print(f"State Code: {city.state_code}")
print(f"Country ID: {city.country_id}")  # aliased as 'country' in database
print(f"Country Code: {city.country_code}")
print(f"Location: ({city.latitude}, {city.longitude})")
print(f"Created: {city.created_at}")
print(f"Updated: {city.updated_at}")
print(f"Active: {city.flag}")
print(f"Wiki Data: {city.wiki_data_id}")  # aliased as 'wikiDataId' in database

# Country model fields
country = db.get_country_by_code("US")
print(f"Basic Info: {country.name} ({country.iso2}, {country.iso3})")
print(f"Codes: {country.numeric_code}, {country.phonecode}")
print(f"Location: {country.region}, {country.subregion}")
print(f"Currency: {country.currency} ({country.currency_symbol})")
print(f"Emoji: {country.emoji} ({country.emoji_u})")  # emoji_u aliased as 'emojiU'
```

### API Reference

```python
# DatabaseManager methods
db = DatabaseManager()

# Search cities by name
cities = db.search_cities("Moscow", limit=5)

# Get country information
country = db.get_country_info("US")

# Calculate distance between two points
new_york = (40.7128, -74.0060)  # (latitude, longitude)
london = (51.5074, -0.1278)
distance = db.calculate_distance(new_york, london)
print(f"Distance between cities: {distance:.1f}km")

# Find nearby cities
cities = db.get_nearby_cities(
    latitude=40.7128,
    longitude=-74.0060,
    radius_km=100,
    limit=10
)

# Get cities by country
cities = db.get_cities_by_country("US")

# Get states/regions by country
states = db.get_states_by_country("US")

# Get database statistics
stats = db.get_statistics()
```

### Date Handling

The package handles dates robustly:
- Invalid dates ('0000-00-00 00:00:00') are automatically converted to `None`
- All date fields (`created_at`, `updated_at`) are optional
- Dates are stored in UTC format
- Dates are returned as Python `datetime` objects

Example:
```python
city = db.get_city_by_id(1)
if city.created_at:
    print(f"Created: {city.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
if city.updated_at:
    print(f"Last Updated: {city.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
```

### Distance Calculation

The package uses [geopy](https://geopy.readthedocs.io/) for precise distance calculations using the geodesic formula. Coordinates are passed as tuples of (latitude, longitude).

Example distances:
```python
# Some major city coordinates
new_york = (40.7128, -74.0060)
london = (51.5074, -0.1278)
paris = (48.8566, 2.3522)
tokyo = (35.6762, 139.6503)
seoul = (37.5665, 126.9780)

# Calculate distances
print(f"New York to London: {db.calculate_distance(new_york, london):.1f}km")  # ~5,570km
print(f"Paris to Tokyo: {db.calculate_distance(paris, tokyo):.1f}km")  # ~9,713km
print(f"Tokyo to Seoul: {db.calculate_distance(tokyo, seoul):.1f}km")  # ~1,160km
```

### Database Content

The package includes:
- Countries (250 records)
- Regions (6 records)
- Subregions (22 records)
- States/Regions/Municipalities (5,038 records)
- Cities/Towns/Districts (151,072 records)


---

## Django Integration

AigeoDB provides Django model fields with Select2-powered autocomplete support for cities and countries. The integration includes custom widgets with dark mode support and AJAX search functionality.

### Setup

1. Add to INSTALLED_APPS:
```python
INSTALLED_APPS = [
    ...
    'aigeodb.django',
]
```

2. Add URLs to your project's urls.py:
```python
from django.urls import path, include

urlpatterns = [
    ...
    path('aigeodb/', include('aigeodb.django.urls')),
]
```

3. Make sure you have static files configured:
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```

4. Run collectstatic:
```bash
python manage.py collectstatic
```

### Using Fields

```python
from django.db import models
from aigeodb.django import CityField, CountryField

class Location(models.Model):
    city = CityField()
    country = CountryField()

    # Fields can be optional
    departure_city = CityField(null=True, blank=True)

    def __str__(self):
        return f"{self.city.name}, {self.country.name}"
```

### Admin Integration

The fields work automatically in Django admin with Select2 widgets:

```python
from django.contrib import admin
from aigeodb.django import AutocompleteFieldsMixin

@admin.register(Location)
class LocationAdmin(AutocompleteFieldsMixin, admin.ModelAdmin):
    list_display = ('city', 'country')
    search_fields = ('city__name', 'country__name')
```

### Features

- Built-in Select2 integration with AJAX search
- Automatic dark/light theme support
- Efficient data loading with caching
- Built-in data validation
- Responsive design
- Support for Django admin inlines
- Thread-safe database access

### Widget Customization

The fields use custom Select2 widgets that can be customized:

```python
from django.db import models
from aigeodb.django import CityField, CountryField

class Location(models.Model):
    city = CityField(
        widget_attrs={
            'data-placeholder': 'Search for a city...',
            'data-minimum-input-length': '3',
            'class': 'custom-select'
        }
    )
    country = CountryField(
        widget_attrs={
            'data-placeholder': 'Select a country',
            'style': 'width: 100%'
        }
    )
```

### API Endpoints

The package provides two AJAX endpoints:

- `/aigeodb/search-cities/`
  - Parameters:
    - `term`: Search query (min 2 characters)
    - `page`: Page number for pagination
  - Returns:
    ```json
    {
        "results": [
            {
                "id": "123",
                "text": "New York, United States"
            }
        ],
        "pagination": {
            "more": false
        }
    }
    ```

- `/aigeodb/search-countries/`
  - Parameters:
    - `term`: Search query (min 2 characters)
    - `page`: Page number for pagination
  - Returns:
    ```json
    {
        "results": [
            {
                "id": "US",
                "text": "United States"
            }
        ],
        "pagination": {
            "more": false
        }
    }
    ```

### Static Files

The package includes:
- `aigeodb/js/autocomplete-init.js` - Select2 initialization
- `aigeodb/css/autocomplete-theme.css` - Theme styles with dark mode

These files are automatically included when using `AutocompleteFieldsMixin`.

---

## About

Developed by [Unrealos Inc.](https://unrealos.com/) - We create innovative SaaS and PaaS solutions powered by AI for business. Our expertise includes:
- AI-powered business solutions
- SaaS platforms
- PaaS infrastructure
- Custom enterprise software

## License

MIT License - see the LICENSE file for details.

## Credits

- Data source: [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database)
- Developed by [Unrealos Inc.](https://unrealos.com/)

### Coordinate-Based Lookups

The package provides methods to find cities and countries by coordinates:

```python
# Get city by coordinates
city = db.get_city_by_coordinates(
    latitude=40.7128,
    longitude=-74.0060
)
if city:
    print(f"Nearest city: {city.name}, {city.country_code}")

# Get country by coordinates
country = db.get_country_by_coordinates(
    latitude=40.7128,
    longitude=-74.0060
)
if country:
    print(f"Country at location: {country.name} ({country.iso2})")
```

### Distance Calculation

The package uses [geopy](https://geopy.readthedocs.io/) for precise distance calculations using the geodesic formula. Coordinates are passed as tuples of (latitude, longitude).

Example distances:
```python
# Some major city coordinates
new_york = (40.7128, -74.0060)
london = (51.5074, -0.1278)
paris = (48.8566, 2.3522)
tokyo = (35.6762, 139.6503)
seoul = (37.5665, 126.9780)

# Calculate distances
print(f"New York to London: {db.calculate_distance(new_york, london):.1f}km")  # ~5,570km
print(f"Paris to Tokyo: {db.calculate_distance(paris, tokyo):.1f}km")  # ~9,713km
print(f"Tokyo to Seoul: {db.calculate_distance(tokyo, seoul):.1f}km")  # ~1,160km
```
