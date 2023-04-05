from django.shortcuts import render


def index(request):
    return render(request, "serial_camera/index.html")
