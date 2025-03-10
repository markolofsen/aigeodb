from django.conf import settings
from django.core.paginator import Paginator
from django.http import JsonResponse

from ..core.database import DatabaseManager


def search_cities(request):
    """Handle city search requests for Select2."""
    try:
        term = request.GET.get("term", "").strip()
        page = int(request.GET.get("page", 1))

        db = DatabaseManager()
        results = db.search_cities(term)

        # Paginate results
        paginator = Paginator(results, 10)  # 10 items per page
        current_page = paginator.page(page)

        return JsonResponse(
            {
                "results": [
                    {"id": city.id, "text": f"{city.name}, {city.country.name}"}
                    for city in current_page.object_list
                ],
                "pagination": {"more": current_page.has_next()},
            }
        )
    except Exception as e:
        if settings.DEBUG:
            print(f"Error in city search: {str(e)}")
        return JsonResponse({"results": [], "pagination": {"more": False}})


def search_countries(request):
    """Handle country search requests for Select2."""
    try:
        term = request.GET.get("term", "").strip()
        page = int(request.GET.get("page", 1))

        db = DatabaseManager()
        results = db.search_countries(term)

        # Paginate results
        paginator = Paginator(results, 10)  # 10 items per page
        current_page = paginator.page(page)

        return JsonResponse(
            {
                "results": [
                    {"id": country.id, "text": f"{country.name} ({country.iso2})"}
                    for country in current_page.object_list
                ],
                "pagination": {"more": current_page.has_next()},
            }
        )
    except Exception as e:
        if settings.DEBUG:
            print(f"Error in country search: {str(e)}")
        return JsonResponse({"results": [], "pagination": {"more": False}})
