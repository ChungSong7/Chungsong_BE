# middlewares.py 파일에 HttpsRedirectMiddleware 클래스를 작성합니다.
from django.conf import settings
from django.http import HttpResponsePermanentRedirect

class HttpsRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.is_secure() and settings.DEBUG:
            new_url = request.build_absolute_uri().replace('http://', 'https://', 1)
            return HttpResponsePermanentRedirect(new_url)
        return self.get_response(request)
