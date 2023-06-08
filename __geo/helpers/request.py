
def get_api_base_url(request):
    api_base_url = 'https://' if request.is_secure else 'http://'
    api_base_url += request.get_host() + '/'
    return api_base_url
