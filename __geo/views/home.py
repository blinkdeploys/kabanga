from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required


@login_required
def home_view(request):
    context = {
        'return': {
            'title': 'home',
            'path': '/',
        },
        'navigation': [
            [
                {
                    'title': 'Polling Stations',
                    'url': '/geo/stations',
                    'details': 'Manage polling stations',
                    'theme': 'text-dark bg-light',
                },
                {
                    'title': 'Nation',
                    'url': '/geo/nations',
                    'details': 'Manage nation details',
                    'theme': 'text-dark bg-light',
                },
            ],
            [
                {
                    'title': 'Constituencies',
                    'url': '/geo/constituencies',
                    'details': 'Manage constituencies',
                    'theme': 'text-dark bg-light',
                },
            ],
            [
                {
                    'title': 'Regions',
                    'url': '/geo/regions',
                    'details': 'Manage regions',
                    'theme': 'text-dark bg-light',
                },
            ],
        ],
    }
    return render(request, "home.html", context)
