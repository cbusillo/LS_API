from django.http import HttpResponseRedirect
from urllib.parse import urlencode


class ParameterizedChangeListMixin:
    default_query_parameters = {}

    def changelist_view(self, request, extra_context=None):
        query_params = request.GET.copy()

        # Apply default query parameters if no query parameters are set
        if not query_params and self.default_query_parameters:
            query_params.update(self.default_query_parameters)

        # Remove default query parameters if more specific filters are set
        should_redirect = False
        for key in self.default_query_parameters.keys():
            key_prefix = f"{key}__"
            if any(param.startswith(key_prefix) for param in request.GET.keys()):
                if key in query_params:
                    query_params.pop(key, None)
                    should_redirect = True
            elif key not in request.GET:
                query_params[key] = self.default_query_parameters[key]
                should_redirect = True

        # Redirect only if needed
        if should_redirect:
            query_string = urlencode(query_params)
            return HttpResponseRedirect(f"{request.path}?{query_string}")

        return super().changelist_view(request, extra_context)
