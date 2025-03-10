from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.conf import settings

from ...core.database import DatabaseManager
from .widgets import BaseSelectWidget


class CountrySelectWidget(BaseSelectWidget):
    """Widget for country selection with Select2 integration.

    This widget provides:
    - Asynchronous country search
    - Country display with ISO code
    - Automatic value handling
    """

    def __init__(self, attrs=None):
        attrs = attrs or {}
        attrs["class"] = "country-select"
        attrs["data-placeholder"] = "Search for a country..."
        super().__init__(attrs=attrs)
        self._db = DatabaseManager()

    def get_url(self):
        """Get URL for country search endpoint."""
        return reverse("aigeodb:search-countries")

    def get_object_by_id(self, value):
        """Get country object by ID.

        Args:
            value: Country ISO2 code (str)

        Returns:
            Country object or None if not found
        """
        try:
            # Always convert to uppercase for consistency
            return self._db.get_country_by_id(str(value).upper())
        except (ValueError, TypeError) as e:
            if settings.DEBUG:
                print(f"Error getting country: {str(e)}")
            return None

    def format_choice(self, obj):
        """Format country for display.

        Args:
            obj: Country object

        Returns:
            Formatted string: "Country Name (ISO2)"
        """
        return f"{obj.name} ({obj.iso2})" if obj else ""


class CountryField(models.CharField):
    """Field for storing country ISO2 codes with autocomplete widget."""
    
    def __init__(self, *args, **kwargs):
        self._db = DatabaseManager()
        kwargs['max_length'] = 2  # ISO2 country code
        kwargs['null'] = kwargs.get('null', True)
        kwargs['blank'] = kwargs.get('blank', True)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'widget': CountrySelectWidget,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        if value is not None:
            country = self._db.get_country_by_id(value)
            if not country:
                raise ValidationError('Invalid country code')

    def get_prep_value(self, value):
        """Convert value before saving to database."""
        if value is None:
            return None
        try:
            # Always store as uppercase ISO2 code
            return str(value).upper()
        except (ValueError, TypeError):
            return None

    def from_db_value(self, value, expression, connection):
        """Convert value when reading from database."""
        if value is None:
            return None
        try:
            # Always return as uppercase ISO2 code
            return str(value).upper()
        except (ValueError, TypeError):
            return None

    def to_python(self, value):
        """Convert value to Python object."""
        if value is None:
            return None
        try:
            # Always convert to uppercase ISO2 code
            return str(value).upper()
        except (ValueError, TypeError):
            return None
