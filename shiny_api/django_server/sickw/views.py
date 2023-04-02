"""View for sickw"""
from django.core.handlers.wsgi import WSGIRequest  # type: ignore
from django.shortcuts import render  # type: ignore
from pydantic import BaseModel


class SickwGroup(BaseModel):
    """Class to hold label group data"""


def bulk_lookup(request: WSGIRequest):
    pass