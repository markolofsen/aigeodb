from django.apps import AppConfig
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class AigeoDBConfig(AppConfig):
    name = 'aigeodb.django'
    verbose_name = 'AigeoDB'
    
    def ready(self):
        """
        Initialize the application when Django starts.
        This method is called once the registry is fully populated.
        """
        from aigeodb import DatabaseManager
        
        try:
            # Initialize database manager with cache if available
            cache_backend = cache if hasattr(cache, 'get') and hasattr(cache, 'set') else None
            
            if not hasattr(self, '_db'):
                self._db = DatabaseManager()
                if cache_backend:
                    logger.info("AigeoDB: Cache backend detected and configured")
                else:
                    logger.info("AigeoDB: No cache backend available, working without cache")
                
            # Make database manager thread-local
            from threading import local
            thread_local = local()
            thread_local.db = self._db
            
            # Initialize components with thread-local db
            from . import views
            views.thread_local = thread_local
            
            from .fields.city import CityField
            from .fields.country import CountryField
            CityField.get_db = lambda: thread_local.db
            CountryField.get_db = lambda: thread_local.db
            
            logger.info("AigeoDB: Django integration initialized successfully")
            
        except Exception as e:
            logger.error(f"AigeoDB: Failed to initialize Django integration: {e}")
            raise


default_app_config = 'aigeodb.django.AigeoDBConfig' 