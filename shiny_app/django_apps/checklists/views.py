from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic.edit import FormView
from django.urls import reverse_lazy

from .forms import TestInstanceForm, TestInstanceResultForm, TestInstanceSpecificationForm
from .models import Test, TestResult, Specification, Device


class DeviceTestsView(View):
    def get(self, request, *args, **kwargs):
        device_type_id = kwargs.get("device_type_id")
        device_part_id = kwargs.get("device_part_id")

        device_id = (
            Device.objects.filter(device_type_id=device_type_id, device_part_id=device_part_id).values_list("id", flat=True).first()
        )

        tests = list(Test.objects.filter(devicetest__device_id=device_id).values("id", "name"))

        choices = {key: value for key, value in TestResult.choices}
        return JsonResponse(
            {"tests": tests, "choices": choices},
            safe=False,
        )


class DeviceSpecificationsView(View):
    def get(self, request, *args, **kwargs):
        device_type_id = kwargs.get("device_type_id")
        device_part_id = kwargs.get("device_part_id")
        device_id = (
            Device.objects.filter(device_type_id=device_type_id, device_part_id=device_part_id).values_list("id", flat=True).first()
        )
        specifications = list(Specification.objects.filter(devicespecification__device_id=device_id).values("id", "name"))
        return JsonResponse(specifications, safe=False)


class TestInstanceView(FormView):
    template_name = "checklists/test_instance.html"
    form_class = TestInstanceForm
    success_url = reverse_lazy("success")

    def form_valid(self, form):
        # Process the TestInstanceForm
        test_instance = form.save()

        # Get the lists of TestInstanceResultForm and TestInstanceSpecificationForm from the request
        results_form_list = self.request.POST.getlist("result_forms")
        specs_form_list = self.request.POST.getlist("spec_forms")

        # Process each TestInstanceResultForm
        for result_form in results_form_list:
            form = TestInstanceResultForm(result_form)
            if form.is_valid():
                form.save()

        # Process each TestInstanceSpecificationForm
        for spec_form in specs_form_list:
            form = TestInstanceSpecificationForm(spec_form)
            if form.is_valid():
                form.save()

        return super().form_valid(form)
