"""View for API access to Shiny Stuff"""

from django.views.generic import ListView

from .models import Serial


class SerialListView(ListView):
    """View for listing items"""

    model = Serial
    paginate_by = 100
