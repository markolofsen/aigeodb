import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Sequence, TypeVar, Type

from geopy.distance import geodesic
# Import models
from .db_models import (
    DBBaseModel,
    DBCity,
    DBCountry,
    DBRegion,
    DBState,
    DBSubregion,
    database,
)
from .py_models import (
    CityDTO,
    CountryDTO,
    RegionDTO,
    StateDTO,
    SubregionDTO,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ModelT = TypeVar('ModelT', DBCity, DBCountry, DBRegion, DBState, DBSubregion)
PydanticT = TypeVar('PydanticT', CityDTO, CountryDTO, RegionDTO, StateDTO, SubregionDTO)


class DatabaseManager:
    # Model mapping dictionary
    MODEL_MAPPING = {
        DBCity: CityDTO,
        DBCountry: CountryDTO,
        DBRegion: RegionDTO,
        DBState: StateDTO,
        DBSubregion: SubregionDTO,
    }

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

    def _convert_to_pydantic(
        self, peewee_model: DBBaseModel, pydantic_model: Type[PydanticT]
    ) -> PydanticT:
        """Convert a Peewee model instance to a Pydantic model"""
        data = peewee_model.__data__.copy()

        # Handle invalid dates
        if 'created_at' in data and data['created_at'] == '0000-00-00 00:00:00':
            data['created_at'] = None
        if 'updated_at' in data and data['updated_at'] == '0000-00-00 00:00:00':
            data['updated_at'] = None

        return pydantic_model(**data)

    def query(
        self,
        model: Type[ModelT],
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Sequence[Any]:
        """
        Generic query method
        :param model: Peewee model class
        :param filters: Dictionary of filters {column_name: value}
        :param limit: Maximum number of records to return
        :param offset: Number of records to skip
        :return: List of Pydantic model instances
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

            pydantic_model = self.MODEL_MAPPING[model]
            return [self._convert_to_pydantic(item, pydantic_model) for item in query]
        except Exception as e:
            logger.error(f"Query error: {e}")
            raise e

    def search(
        self,
        model: Type[ModelT],
        term: str,
        fields: List[str],
        limit: Optional[int] = None
    ) -> Sequence[Any]:
        """
        Search records by term in specified fields using OR condition

        Args:
            model: Peewee model class
            term: Search term
            fields: List of field names to search in
            limit: Maximum number of records to return

        Returns:
            Sequence of matching Pydantic model instances
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
            if len(search_conditions) == 1:
                query = model.select().where(search_conditions[0])
            else:
                # Combine conditions with OR operator using Peewee's | operator
                condition = search_conditions[0]
                for additional_condition in search_conditions[1:]:
                    condition = condition | additional_condition
                query = model.select().where(condition)

            if limit:
                query = query.limit(limit)

            pydantic_model = self.MODEL_MAPPING[model]
            return [self._convert_to_pydantic(item, pydantic_model) for item in query]

        except Exception as e:
            logger.error(f"Search error: {e}")
            raise e

    def get_cities_by_country(self, country_code: str) -> Sequence[CityDTO]:
        """Get all cities for a specific country"""
        return self.query(DBCity, filters={"country_code": country_code})

    def get_states_by_country(self, country_code: str) -> Sequence[StateDTO]:
        """Get all states for a specific country"""
        return self.query(DBState, filters={"country_code": country_code})

    def search_cities(self, term: str, limit: int = 10) -> Sequence[CityDTO]:
        """Search cities by name"""
        return self.search(DBCity, term, ["name"], limit)

    def search_countries(self, term: str, limit: int = 10) -> Sequence[CountryDTO]:
        """Search countries by name"""
        return self.search(DBCountry, term, ["name", "iso2", "iso3"], limit)

    def get_country_info(self, country_code: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a country"""
        try:
            country = DBCountry.select().where(DBCountry.iso2 == country_code).first()
            if not country:
                return None

            country_model = self._convert_to_pydantic(country, CountryDTO)
            return country_model.dict()
        except Exception as e:
            logger.error(f"Error getting country info: {e}")
            raise e

    def get_nearby_cities(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 100,
        limit: int = 10,
    ) -> Sequence[CityDTO]:
        """
        Get cities within a radius of a point, sorted by distance.

        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius in kilometers
            limit: Maximum number of results

        Returns:
            Sequence of cities sorted by distance from the given point
        """
        try:
            # First get approximate results using bounding box
            degree_radius = radius_km / 111.0

            candidates = (
                DBCity.select()
                .where(
                    DBCity.latitude.between(
                        latitude - degree_radius, latitude + degree_radius
                    ),
                    DBCity.longitude.between(
                        longitude - degree_radius, longitude + degree_radius
                    ),
                    DBCity.flag,
                )
                .execute()
            )

            # Calculate exact distances and filter
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

            # Return only the cities, sorted by distance
            return [self._convert_to_pydantic(city, CityDTO) for city, _ in results]

        except Exception as e:
            logger.error(f"Error getting nearby cities: {e}")
            raise e

    def get_statistics(self) -> Dict[str, int]:
        """Get count of records in each table"""
        try:
            return {
                "countries": DBCountry.select().count(),
                "regions": DBRegion.select().count(),
                "subregions": DBSubregion.select().count(),
                "states": DBState.select().count(),
                "cities": DBCity.select().count(),
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

    def __get_by_id(self, model: Type[ModelT], id: int) -> Optional[PydanticT]:
        """
        Get model instance by ID
        :param model: Peewee model class
        :param id: ID of the record
        :return: Pydantic model instance or None
        """
        try:
            instance = model.get_or_none(model.id == id)
            if not instance:
                return None

            pydantic_model = self.MODEL_MAPPING[model]
            try:
                return self._convert_to_pydantic(instance, pydantic_model)
            except Exception as e:
                logger.error(f"Error converting model: {e}")
                return None

        except Exception as e:
            logger.error(f"Error getting record by ID: {e}")
            return None

    def get_city_by_id(self, city_id: int) -> Optional[CityDTO]:
        """
        Get city by ID
        :param city_id: City ID
        :return: City instance or None
        """
        return self.__get_by_id(DBCity, city_id)

    def get_country_by_id(self, country_id: int) -> Optional[CountryDTO]:
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
                return self.__get_by_id(DBCountry, country_id)
        except Exception as e:
            logger.error(f"Error getting country by ID: {e}")
            return None

    def get_country_by_code(self, country_code: str) -> Optional[CountryDTO]:
        """
        Get country by ISO2 code
        :param country_code: ISO2 country code (2 letters)
        :return: Country instance or None
        """
        try:
            code = str(country_code).upper()
            country = DBCountry.get_or_none(DBCountry.iso2 == code)
            if country:
                return self._convert_to_pydantic(country, CountryDTO)
            return None
        except Exception as e:
            logger.error(f"Error getting country by code: {e}")
            return None

    def get_all_cities(self) -> Sequence[CityDTO]:
        """
        Get all cities
        :return: List of all cities
        """
        return self.query(DBCity, filters={"flag": True})

    def get_all_countries(self) -> Sequence[CountryDTO]:
        """
        Get all countries
        :return: List of all countries
        """
        return self.query(DBCountry, filters={"flag": True})
