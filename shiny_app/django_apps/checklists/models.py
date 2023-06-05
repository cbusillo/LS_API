"""Shiny Checklist class."""
from typing import TYPE_CHECKING, Iterable, Optional
from django.db import models
from django.db.models import CharField, TextChoices


class Technician(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Test(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=3, unique=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        unique_together = ["name", "code"]

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Specification(models.Model):
    name = models.CharField(max_length=200, unique=True)
    sort_order = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.name


class DeviceType(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self) -> str:
        return self.name


class DevicePart(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name


class Device(models.Model):
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE)
    device_part = models.ForeignKey(DevicePart, on_delete=models.CASCADE)
    specifications = models.ManyToManyField(Specification, through="DeviceSpecification")
    tests = models.ManyToManyField(Test, through="DeviceTest")

    def __str__(self) -> str:
        return str(self.device_type) + " " + str(self.device_part)

    class Meta:
        unique_together = ["device_type", "device_part"]

    @classmethod
    def create(cls, device_type_part, specifications, tests):
        # Check if a device with the same device_type_part and specifications already exists
        existing_devices = cls.objects.filter(device_type_part=device_type_part)

        for device in existing_devices:
            if set(device.specifications.values_list("id", flat=True)) == set(specifications):
                raise ValueError("A device with the same device_type_part and specifications already exists")

            if set(device.tests.values_list("id", flat=True)) == set(tests):
                raise ValueError("A device with the same device_type_part and tests already exists")

        # If no such device exists, create a new one
        new_device = cls(device_type_part=device_type_part)
        new_device.save()

        # Add the specifications to the new device
        for spec in specifications:
            DeviceSpecification.objects.create(device=new_device, specification=spec)

        for test in tests:
            DeviceTest.objects.create(device=new_device, test=test)

        return new_device


class DeviceSpecification(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    specification = models.ForeignKey(Specification, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["device", "specification"]
        verbose_name_plural = "Device Specifications (DU)"
        verbose_name = "Device Specification (DU)"


class DeviceTest(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["device", "test"]
        verbose_name_plural = "Device Tests (DU)"
        verbose_name = "Device Test (DU)"


class TestResult(TextChoices):
    PASS = "P", "Pass"
    FAIL = "F", "Fail"
    OTHER = "O", "Other"
    NOT_APPLICABLE = "NA", "Not Applicable"
    NOT_TESTED = "NT", "Not Tested"


class TestInstance(models.Model):
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE)
    device_part = models.ForeignKey(DevicePart, on_delete=models.CASCADE)
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE)
    specifications = models.ManyToManyField(Specification, through="TestInstanceSpecification")
    date = models.DateField()
    tests = models.ManyToManyField(Test, through="TestInstanceResult")


class TestInstanceResult(models.Model):
    test_instance = models.ForeignKey(TestInstance, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    result = CharField(
        max_length=2,
        choices=TestResult.choices,
        default=TestResult.NOT_TESTED,
        help_text="Select other if the result is not pass or fail.  This can be a cosmetic issue or "
        "something else that does not affect the functionality of the device.",
    )
    comment = models.CharField(max_length=200, blank=True, null=True)


class TestInstanceSpecification(models.Model):
    test_instance = models.ForeignKey(TestInstance, on_delete=models.CASCADE)
    specification = models.ForeignKey(Specification, on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
