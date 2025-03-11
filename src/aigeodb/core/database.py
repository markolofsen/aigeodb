import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from geopy.distance import geodesic
# Peewee modules
import peewee as pw

# Import models
from .models import BaseModel, City, Country, Region, State, Subregion, database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_name: str = "world"):
        """
        Initialize database connection
        :param db_name: Name of the database file (without .sqlite3 extension)
        """
        base_dir = Path(__file__).parent.parent / "sqlite"
        self.db_path = base_dir / f"{db_name}.sqlite3"

        logger.debug(f"Database path: {self.db_path}")
        logger.debug(f"Database exists: {self.db_path.exists()}")
        is_file = self.db_path.is_file() if self.db_path.exists() else False
        logger.debug(f"Database is file: {is_file}")
        logger.debug(f"Current working directory: {Path.cwd()}")

        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

        # Initialize the database
        database.init(str(self.db_path))
        
        # Check connection
        if not database.is_closed():
            database.close()
        database.connect()

    def query(
        self,
        model: BaseModel,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[BaseModel]:
        """
        Generic query method
        :param model: Peewee model class
        :param filters: Dictionary of filters {column_name: value}
        :param limit: Maximum number of records to return
        :param offset: Number of records to skip
        :return: List of model instances
        """
        try:
            query = model.select()

            if filters:
                conditions = []
                for key, value in filters.items():
                    field = getattr(model, key)
                    if isinstance(value, (list, tuple)):
                        conditions.append(field.in_(value))
                    else:
                        conditions.append(field == value)
                
                if conditions:
                    query = query.where(*conditions)

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            return list(query)
        except Exception as e:
            logger.error(f"Query error: {e}")
            raise e

    def search(
        self, model: BaseModel, term: str, fields: List[str], 
        limit: Optional[int] = None
    ) -> List[BaseModel]:
        """
        Search records by term in specified fields using OR condition

        Args:
            model: Peewee model class
            term: Search term
            fields: List of field names to search in
            limit: Maximum number of records to return

        Returns:
            List of matching records where ANY of the fields match the term
        """
        try:
            # Clean and validate search term
            if not term or not term.strip():
                return []
            term = term.strip()

            # Build OR conditions for each field
            search_conditions = []
            for field in fields:
                if hasattr(model, field):
                    field_obj = getattr(model, field)
                    search_conditions.append(field_obj.contains(term))

            if not search_conditions:
                return []

            # Apply OR conditions and limit
            query = model.select().where(pw.OR(*search_conditions))
            if limit:
                query = query.limit(limit)

            return list(query)

        except Exception as e:
            logger.error(f"Search error: {e}")
            raise e

    def get_cities_by_country(self, country_code: str) -> List[City]:
        """Get all cities for a specific country"""
        return self.query(City, filters={"country_code": country_code})

    def get_states_by_country(self, country_code: str) -> List[State]:
        """Get all states for a specific country"""
        return self.query(State, filters={"country_code": country_code})

    def search_cities(self, term: str, limit: int = 10) -> List[City]:
        """Search cities by name"""
        return self.search(City, term, ["name"], limit)
        
    def search_countries(self, term: str, limit: int = 10) -> List[Country]:
        """Search countries by name"""
        return self.search(Country, term, ["name", "iso2", "iso3"], limit)

    def get_country_info(self, country_code: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a country"""
        try:
            country = Country.select().where(Country.iso2 == country_code).first()
            if not country:
                return None

            return {
                "id": country.id,
                "name": country.name,
                "iso2": country.iso2,
                "iso3": country.iso3,
                "capital": country.capital,
                "currency": country.currency,
                "currency_symbol": country.currency_symbol,
                "region": country.region,
                "subregion": country.subregion,
                "timezones": country.timezones,
                "latitude": country.latitude,
                "longitude": country.longitude,
                "emoji": country.emoji,
            }
        except Exception as e:
            logger.error(f"Error getting country info: {e}")
            raise e

    def get_nearby_cities(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 100,
        limit: int = 10,
        with_distance: bool = False,
    ) -> Union[List[City], List[Tuple[City, float]]]:
        """
        Get cities within a radius of a point with optional distance calculation.

        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius in kilometers
            limit: Maximum number of results
            with_distance: If True, returns tuples (city, distance_km)

        Returns:
            If with_distance=False: List[City] sorted by distance
            If with_distance=True: List[Tuple[City, float]] sorted by distance
        """
        try:
            # First get approximate results using bounding box
            degree_radius = radius_km / 111.0

            candidates = (
                City.select()
                .where(
                    City.latitude.between(
                        latitude - degree_radius, latitude + degree_radius
                    ),
                    City.longitude.between(
                        longitude - degree_radius, longitude + degree_radius
                    ),
                    City.flag,
                )
                .execute()
            )

            # Calculate exact distances
            cities_with_distances = []
            for city in candidates:
                distance = self.calculate_distance(
                    (latitude, longitude), (city.latitude, city.longitude)
                )
                if distance <= radius_km:
                    cities_with_distances.append((city, distance))

            # Sort by distance and limit results
            cities_with_distances.sort(key=lambda x: x[1])
            results = cities_with_distances[:limit]

            # Return results in requested format
            if with_distance:
                return results
            return [city for city, _ in results]

        except Exception as e:
            logger.error(f"Error getting nearby cities: {e}")
            raise e

    def get_statistics(self) -> Dict[str, int]:
        """Get count of records in each table"""
        try:
            return {
                "countries": Country.select().count(),
                "regions": Region.select().count(),
                "subregions": Subregion.select().count(),
                "states": State.select().count(),
                "cities": City.select().count(),
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            raise e

    def calculate_distance(
        self, point1: Tuple[float, float], point2: Tuple[float, float]
    ) -> float:
        """
        Calculate distance between two points in kilometers
        :param point1: (latitude, longitude)
        :param point2: (latitude, longitude)
        :return: Distance in kilometers
        """
        try:
            return geodesic(point1, point2).kilometers
        except Exception as e:
            logger.error(f"Error calculating distance: {e}")
            return float("inf")  # Return infinity on error

    def get_by_id(self, model: BaseModel, id: int) -> Optional[BaseModel]:
        """
        Get model instance by ID
        :param model: Peewee model class
        :param id: ID of the record
        :return: Model instance or None
        """
        try:
            return model.get_or_none(model.id == id)
        except Exception as e:
            logger.error(f"Error getting record by ID: {e}")
            return None

    def get_city_by_id(self, city_id: int) -> Optional[City]:
        """
        Get city by ID
        :param city_id: City ID
        :return: City instance or None
        """
        return self.get_by_id(City, city_id)

    def get_country_by_id(self, country_id: int) -> Optional[Country]:
        """
        Get country by ID
        :param country_id: Country ID
        :return: Country instance or None
        """
        try:
            if isinstance(country_id, str):
                # If string provided, treat it as ISO2 code and use get_country_by_code
                return self.get_country_by_code(country_id)
            else:
                # Otherwise, use the numeric ID
                return Country.get_or_none(Country.id == country_id)
        except Exception as e:
            logger.error(f"Error getting country by ID: {e}")
            return None
            
    def get_country_by_code(self, country_code: str) -> Optional[Country]:
        """
        Get country by ISO2 code
        :param country_code: ISO2 country code (2 letters)
        :return: Country instance or None
        """
        try:
            code = str(country_code).upper()
            return Country.get_or_none(Country.iso2 == code)
        except Exception as e:
            logger.error(f"Error getting country by code: {e}")
            return None

    def get_all_cities(self) -> List[City]:
        """
        Get all cities
        :return: List of all cities
        """
        return list(City.select().where(City.flag))

    def get_all_countries(self) -> List[Country]:
        """
        Get all countries
        :return: List of all countries
        """
        return list(Country.select().where(Country.flag))
