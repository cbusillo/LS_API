"""View for API access to Shiny Stuff"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from .models import Serial


class SerialListView(LoginRequiredMixin, ListView):
    """View for listing items"""

    model = Serial
    paginate_by = 100
