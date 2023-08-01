from django.utils import lru_cache
from django.utils.module_loading import import_string

from urlmiddleware.base import MiddlewareResolver404
from urlmiddleware.urlresolvers import resolve


@lru_cache.lru_cache(maxsize=None)
def matched_middleware(path):
    return resolve(path)


class URLMiddleware(object):
    """
    To install urlmiddleware, one global middleware class needs to be
    added so it can then act as an entry point and match other middleware
    classes.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def get_matched_middleware(self, path):

        try:
            middleware_matches = matched_middleware(path)
        except MiddlewareResolver404:
            return []

        return middleware_matches

    def __call__(self, request):
        matched_middleware = self.get_matched_middleware(request.path)
        chain = self.get_response
        for middleware_path in matched_middleware:
            middleware = import_string(middleware_path)
            chain = middleware(chain)
        response = chain(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        matched_middleware = self.get_matched_middleware(request.path)
        for middleware in matched_middleware:
            if hasattr(middleware, 'process_view'):
                response = middleware.process_view(request, view_func, view_args, view_kwargs)
                if response:
                    return response
        return None

    def process_exception(self, request, exception):
        matched_middleware = self.get_matched_middleware(request.path)
        for middleware in matched_middleware:
            if hasattr(middleware, 'process_exception'):
                response = middleware.process_exception(request, exception)
                if response:
                    return response
        return None
