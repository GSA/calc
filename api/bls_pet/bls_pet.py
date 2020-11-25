# from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
# from django.conf import settings
from django.http import JsonResponse


@require_http_methods(["GET", "POST"])
def autocomplete(request, search_type=None):
    if request.method == 'POST':
        response = JsonResponse({'Error': '1', 'ErrorMessage': 'FROM POST'})
        return response
    elif request.method == 'GET':
        response = JsonResponse({'Error': search_type, 'ErrorMessage': 'FROM GET'})
        return response
