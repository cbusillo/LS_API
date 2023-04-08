"""App to check customers in"""
from django.http import JsonResponse
from django.shortcuts import render
from . import forms


def get_text_data(request):
    """Receive form data as it is being entered"""
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        data = request.POST.get("text_data")

        response_data = {"message": f"Received data: {data}"}
        return JsonResponse(response_data)

    return JsonResponse({"message": "Invalid request."}, status=400)


def home(request):
    """Render home page"""
    check_in_form = forms.CheckIn()
    context = {"form": check_in_form}
    return render(request, "check_in/home.html", context)
