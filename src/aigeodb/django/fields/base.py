from django.db import models
from django.forms.widgets import AutocompleteWidget
from django.core.cache import cache
from typing import Optional, Any


def cached_method(timeout=3600):
    """Cache method results with a default timeout of 3600 seconds."""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if not hasattr(cache, 'get') or not hasattr(cache, 'set'):
                # If cache is not properly configured, just return the function result
                return func(self, *args, **kwargs)

            key = f"aigeodb:{func.__name__}:{args}:{kwargs}"
            result = cache.get(key)
            if result is None:
                result = func(self, *args, **kwargs)
                cache.set(key, result, timeout)
            return result
        return wrapper
    return decorator


class AiGeoAutocompleteWidget(AutocompleteWidget):
    """Custom widget for geographic autocomplete"""
    
    def __init__(self, field, attrs=None):
        super().__init__(attrs)
        self.field = field
        
    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs['data-url'] = self.field.autocomplete_url
        return attrs


class AiGeoField(models.IntegerField):
    """Base field for geographical data that stores only ID"""
    
    CACHE_TIMEOUT = 3600  # 1 hour
    
    def __init__(self, *args, **kwargs):
        self.autocomplete_url = kwargs.pop('autocomplete_url', None)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        if self.autocomplete_url:
            kwargs['widget'] = AiGeoAutocompleteWidget(self)
        return super().formfield(**kwargs)
    
    @classmethod
    def clear_cache(cls, key_pattern: str = '*'):
        """Clear cache for this field type"""
        if hasattr(cache, 'delete_pattern'):
            # For Redis cache
            cache.delete_pattern(f'aigeodb:{key_pattern}')
        else:
            # For other cache backends
            cache.clear()
            
    @cached_method(timeout=CACHE_TIMEOUT)
    def get_data(self, value: Any) -> Optional[dict]:
        """Get data for value with caching"""
        raise NotImplementedError(
            "Subclasses must implement get_data method"
        )
    
    @classmethod
    @cached_method(timeout=CACHE_TIMEOUT)
    def search(cls, term: str, **kwargs) -> list:
        """Search with caching"""
        raise NotImplementedError(
            "Subclasses must implement search method"
        )