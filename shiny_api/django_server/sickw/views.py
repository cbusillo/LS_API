"""View for sickw"""
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from pydantic import BaseModel


class SickwGroup(BaseModel):
    """Class to hold label group data"""


def bulk_lookup(request: WSGIRequest):
    """Bulk lookup view"""
    return render(request, template_name="sickw/bulk_lookup.html")
