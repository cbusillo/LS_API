"""django_poetry_example URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include  # type: ignore
from django.views.generic import RedirectView  # type: ignore
from pwa import urls as pwa_urls  # type: ignore

urlpatterns = [
    path("", include(pwa_urls)),
    path("", RedirectView.as_view(url="label_printer/")),
    path("api/", include("shiny_api.django_server.api.urls")),
    path("ls_functions/", include("shiny_api.django_server.ls_functions.urls")),
    path("label_printer/", include("shiny_api.django_server.label_printer.urls")),
    path("sickw/", include("shiny_api.django_server.sickw.urls")),
]
