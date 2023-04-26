from django.shortcuts import render


def home(request):
    return render(request, "serial_camera/home.html")
