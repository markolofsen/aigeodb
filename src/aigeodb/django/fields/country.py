from typing import Dict, Optional

from ...core.database import DatabaseManager
from ...core.models import Country
from .base import AiGeoField


class CountryField(AiGeoField):
    """Field for storing country ID with autocomplete support"""
    
    def __init__(self, *args, **kwargs):
        kwargs['autocomplete_url'] = '/api/aigeodb/countries/autocomplete/'
        super().__init__(*args, **kwargs)
        self.db = DatabaseManager()
    
    def get_data(self, country_id: int) -> Optional[Dict]:
        """Get country data by ID"""
        country: Country = self.db.get_by_id(Country, country_id)
        if country:
            return {
                'id': country.id,
                'name': country.name,
                'code': country.iso2,
                'code3': country.iso3,
                'currency': country.currency,
                'currency_name': country.currency_name,
                'currency_symbol': country.currency_symbol,
                'latitude': country.latitude,
                'longitude': country.longitude
            }
        return None
    
    @classmethod
    def search(cls, term: str, limit: int = 20) -> list:
        """Search countries for autocomplete"""
        db = DatabaseManager()
        
        # Search using DatabaseManager
        countries = db.search(
            model=Country,
            term=term,
            fields=['name', 'iso2', 'iso3'],
            limit=limit
        )
        
        return [{
            'id': country.id,
            'text': f'{country.name} ({country.iso2})'
        } for country in countries] 