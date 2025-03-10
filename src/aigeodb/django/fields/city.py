from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.conf import settings

from ...core.database import DatabaseManager
from .widgets import BaseSelectWidget


class CitySelectWidget(BaseSelectWidget):
    """Widget for city selection with Select2 integration.

    This widget provides:
    - Asynchronous city search
    - City display with country name
    - Automatic value handling
    """

    def __init__(self, attrs=None):
        attrs = attrs or {}
        attrs["class"] = "city-select"
        attrs["data-placeholder"] = "Search for a city..."
        super().__init__(attrs=attrs)
        self._db = DatabaseManager()

    def get_url(self):
        """Get URL for city search endpoint."""
        return reverse("aigeodb:search-cities")

    def get_object_by_id(self, value):
        """Get city object by ID.

        Args:
            value: City ID (int or str)

        Returns:
            City object or None if not found
        """
        try:
            return self._db.get_city_by_id(int(value))
        except (ValueError, TypeError) as e:
            if settings.DEBUG:
                print(f"Error converting city ID: {str(e)}")
            return None

    def format_choice(self, obj):
        """Format city for display.

        Args:
            obj: City object

        Returns:
            Formatted string: "City Name, Country Name"
        """
        return f"{obj.name}, {obj.country.name}" if obj else ""


class CityField(models.IntegerField):
    """Field for storing city IDs with autocomplete widget."""
    
    def __init__(self, *args, **kwargs):
        self._db = DatabaseManager()
        kwargs['null'] = kwargs.get('null', True)
        kwargs['blank'] = kwargs.get('blank', True)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'widget': CitySelectWidget,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        if value is not None:
            city = self._db.get_city_by_id(value)
            if not city:
                raise ValidationError('Invalid city ID')

    def get_prep_value(self, value):
        """Convert value before saving to database."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def from_db_value(self, value, expression, connection):
        """Convert value when reading from database."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def to_python(self, value):
        """Convert value to Python object."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
