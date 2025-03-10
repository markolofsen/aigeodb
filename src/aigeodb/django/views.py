from django.http import JsonResponse
from django.views import View


class CityAutocompleteView(View):
    def get(self, request):
        from . import thread_local
        
        term = request.GET.get('term', '')
        country_id = request.GET.get('country')
        
        if not term:
            return JsonResponse({'results': []})
        
        try:
            cities = thread_local.db.search_cities(term, limit=20)
            if country_id:
                try:
                    country_id = int(country_id)
                    cities = [
                        city for city in cities 
                        if city.country_id == country_id
                    ]
                except (ValueError, TypeError):
                    pass
                
            results = [
                {'id': city.id, 'text': f"{city.name}, {city.country_code}"}
                for city in cities
            ]
            return JsonResponse({'results': results})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class CountryAutocompleteView(View):
    def get(self, request):
        from . import thread_local
        
        term = request.GET.get('term', '')
        
        if not term:
            return JsonResponse({'results': []})
        
        try:
            countries = thread_local.db.search_countries(term, limit=20)
            results = [
                {'id': country.id, 'text': f"{country.name} ({country.iso2})"}
                for country in countries
            ]
            return JsonResponse({'results': results})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class CityDataView(View):
    def get(self, request, city_id):
        from . import thread_local
        
        try:
            city = thread_local.db.get_city_by_id(city_id)
            if city:
                return JsonResponse({
                    'id': city.id,
                    'name': city.name,
                    'country_code': city.country_code,
                    'state_code': city.state_code
                })
            return JsonResponse({'error': 'City not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class CountryDataView(View):
    def get(self, request, country_id):
        from . import thread_local
        
        try:
            country = thread_local.db.get_country_by_id(country_id)
            if country:
                return JsonResponse({
                    'id': country.id,
                    'name': country.name,
                    'iso2': country.iso2,
                    'iso3': country.iso3
                })
            return JsonResponse({'error': 'Country not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500) 