from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from pathlib import Path
from typing import Optional, List, Dict, Any
from .models import Base, Country, Region, Subregion, State, City
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_name: str = 'world'):
        """
        Initialize database connection
        :param db_name: Name of the database file (without .sqlite3 extension)
        """
        base_dir = Path(__file__).parent.parent / 'sqlite'
        self.db_path = base_dir / f'{db_name}.sqlite3'

        logger.info(f"Database path: {self.db_path}")
        logger.info(f"Database exists: {self.db_path.exists()}")
        logger.info(f"Database is file: {self.db_path.is_file() if self.db_path.exists() else False}")
        logger.info(f"Current working directory: {Path.cwd()}")

        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

        self.engine = create_engine(f'sqlite:///{self.db_path}')
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)

    def query(self, model: Base, filters: Optional[Dict[str, Any]] = None,
              limit: Optional[int] = None, offset: Optional[int] = None) -> List[Base]:
        """
        Generic query method
        :param model: SQLAlchemy model class
        :param filters: Dictionary of filters {column_name: value}
        :param limit: Maximum number of records to return
        :param offset: Number of records to skip
        :return: List of model instances
        """
        session = self.Session()
        try:
            query = session.query(model)

            if filters:
                for key, value in filters.items():
                    if isinstance(value, (list, tuple)):
                        query = query.filter(getattr(model, key).in_(value))
                    else:
                        query = query.filter(getattr(model, key) == value)

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            results = query.all()
            for result in results:
                session.merge(result)
            return results
        except Exception as e:
            session.rollback()
            raise e

    def get_by_id(self, model: Base, id: int) -> Optional[Base]:
        """Get record by ID"""
        session = self.Session()
        try:
            result = session.query(model).get(id)
            if result:
                session.merge(result)
            return result
        except Exception as e:
            session.rollback()
            raise e

    def search(self, model: Base, term: str, fields: List[str],
               limit: Optional[int] = None) -> List[Base]:
        """
        Search records by term in specified fields
        :param model: SQLAlchemy model class
        :param term: Search term
        :param fields: List of field names to search in
        :param limit: Maximum number of records to return
        :return: List of matching records
        """
        session = self.Session()
        try:
            query = session.query(model)
            search_conditions = []

            for field in fields:
                search_conditions.append(getattr(model, field).ilike(f'%{term}%'))

            query = query.filter(*search_conditions)
            if limit:
                query = query.limit(limit)

            results = query.all()
            for result in results:
                session.merge(result)
            return results
        except Exception as e:
            session.rollback()
            raise e

    def get_cities_by_country(self, country_code: str) -> List[City]:
        """Get all cities for a specific country"""
        return self.query(City, filters={'country_code': country_code})

    def get_states_by_country(self, country_code: str) -> List[State]:
        """Get all states for a specific country"""
        return self.query(State, filters={'country_code': country_code})

    def search_cities(self, term: str, limit: int = 10) -> List[City]:
        """Search cities by name"""
        return self.search(City, term, ['name'], limit)

    def get_country_info(self, country_code: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a country"""
        session = self.Session()
        try:
            country = session.query(Country).filter(Country.iso2 == country_code).first()
            if not country:
                return None

            session.merge(country)
            return {
                'id': country.id,
                'name': country.name,
                'iso2': country.iso2,
                'iso3': country.iso3,
                'capital': country.capital,
                'currency': country.currency,
                'currency_symbol': country.currency_symbol,
                'region': country.region,
                'subregion': country.subregion,
                'timezones': country.timezones,
                'latitude': country.latitude,
                'longitude': country.longitude,
                'emoji': country.emoji,
            }
        except Exception as e:
            session.rollback()
            raise e

    def get_nearby_cities(self, latitude: float, longitude: float,
                          radius_km: float = 100, limit: int = 10) -> List[City]:
        """
        Get cities within a radius of a point
        Using simplified distance calculation
        """
        session = self.Session()
        try:
            # Approximate degrees for the given radius (1 degree ≈ 111km)
            degree_radius = radius_km / 111.0

            results = session.query(City).filter(
                City.latitude.between(latitude - degree_radius, latitude + degree_radius),
                City.longitude.between(longitude - degree_radius, longitude + degree_radius),
                City.flag.is_(True)
            ).limit(limit).all()

            for result in results:
                session.merge(result)
            return results
        except Exception as e:
            session.rollback()
            raise e

    def get_statistics(self) -> Dict[str, int]:
        """Get count of records in each table"""
        session = self.Session()
        try:
            return {
                'countries': session.query(Country).count(),
                'regions': session.query(Region).count(),
                'subregions': session.query(Subregion).count(),
                'states': session.query(State).count(),
                'cities': session.query(City).count(),
            }
        except Exception as e:
            session.rollback()
            raise e
