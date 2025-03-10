from django.urls import path
from . import views

app_name = 'aigeodb'

urlpatterns = [
    # Autocomplete endpoints
    path(
        'aigeodb/cities/autocomplete/',
        views.CityAutocompleteView.as_view(),
        name='city_autocomplete'
    ),
    path(
        'aigeodb/countries/autocomplete/',
        views.CountryAutocompleteView.as_view(),
        name='country_autocomplete'
    ),
    
    # Data endpoints
    path(
        'aigeodb/cities/<int:city_id>/',
        views.CityDataView.as_view(),
        name='city_data'
    ),
    path(
        'aigeodb/countries/<int:country_id>/',
        views.CountryDataView.as_view(),
        name='country_data'
    ),
] 