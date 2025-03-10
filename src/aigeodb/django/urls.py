from django.urls import path

from . import views

app_name = "aigeodb"

urlpatterns = [
    path("search-cities/", views.search_cities, name="search-cities"),
    path("search-countries/", views.search_countries, name="search-countries"),
]
