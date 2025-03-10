from django.contrib import admin

from .fields.city import CityField, CitySelectWidget
from .fields.country import CountryField, CountrySelectWidget


class AutocompleteFieldsMixin:
    """
    A mixin for Django admin that automatically sets up autocomplete widgets
    for CityField and CountryField with dark/light theme support.

    This mixin:
    1. Adds necessary CSS/JS for Select2 widgets
    2. Sets up formfield_overrides for CityField and CountryField
    3. Supports automatic dark/light theme switching
    4. Provides better styling for Select2 widgets

    Usage:
        class MyModelAdmin(AutocompleteFieldsMixin, admin.ModelAdmin):
            ...
    """

    class Media:
        css = {
            "all": (
                "admin/css/vendor/select2/select2.min.css",
                "admin/css/autocomplete.css",
                "aigeodb/css/autocomplete-theme.css",
            )
        }
        js = (
            "admin/js/vendor/jquery/jquery.min.js",
            "admin/js/vendor/select2/select2.full.min.js",
            "admin/js/jquery.init.js",
            "aigeodb/js/autocomplete-init.js",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.formfield_overrides = {
            CityField: {"widget": CitySelectWidget},
            CountryField: {"widget": CountrySelectWidget},
            **(
                self.formfield_overrides if hasattr(self, "formfield_overrides") else {}
            ),
        }

    def changelist_view(self, request, extra_context=None):
        """Add extra context for the changelist view."""
        extra_context = extra_context or {}
        extra_context["has_autocomplete_fields"] = True
        return super().changelist_view(request, extra_context)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        """Add extra context for the changeform view."""
        extra_context = extra_context or {}
        extra_context["has_autocomplete_fields"] = True
        return super().changeform_view(request, object_id, form_url, extra_context)
