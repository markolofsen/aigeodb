from typing import Dict, Optional

from ...core.database import DatabaseManager
from ...core.models import City
from .base import AiGeoField


class CityField(AiGeoField):
    """Field for storing city ID with autocomplete support"""
    
    def __init__(self, *args, **kwargs):
        kwargs['autocomplete_url'] = '/api/aigeodb/cities/autocomplete/'
        super().__init__(*args, **kwargs)
        self.db = DatabaseManager()
    
    def get_data(self, city_id: int) -> Optional[Dict]:
        """Get city data by ID"""
        city: City = self.db.get_by_id(City, city_id)
        if city:
            return {
                'id': city.id,
                'name': city.name,
                'country_code': city.country_code,
                'state_code': city.state_code,
                'latitude': city.latitude,
                'longitude': city.longitude
            }
        return None
    
    @classmethod
    def search(cls, term: str, country_code: str = None, limit: int = 20) -> list:
        """Search cities for autocomplete"""
        db = DatabaseManager()
        
        # Apply country filter if provided
        filters = {'country_code': country_code} if country_code else None
        
        # Search using DatabaseManager
        cities = db.search(
            model=City,
            term=term,
            fields=['name', 'state_code'],
            limit=limit
        )
        
        # Apply country filter to results if needed
        if filters:
            cities = [c for c in cities if c.country_code == country_code]
            
        return [{
            'id': city.id,
            'text': f'{city.name}, {city.country_code}'
        } for city in cities] 