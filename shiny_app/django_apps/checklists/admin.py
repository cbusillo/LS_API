from django.contrib import admin

from .models import (
    Technician,
    Test,
    Specification,
    DeviceType,
    DevicePart,
    Device,
    DeviceSpecification,
    DeviceTest,
    TestInstance,
    TestInstanceResult,
    TestInstanceSpecification,
)


@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    """Admin for Technicians."""

    list_display = ("name",)


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    """Admin for Tests."""

    list_display = ("name", "code", "sort_order")


@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    """Admin for Specifications."""

    list_display = ("name", "sort_order")


@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    """Admin for Device Types."""

    list_display = ("name",)


@admin.register(DevicePart)
class DevicePartAdmin(admin.ModelAdmin):
    """Admin for Device Parts."""

    list_display = ("name",)


class DeviceSpecificationInline(admin.TabularInline):
    model = DeviceSpecification
    extra = 5


class DeviceTestInline(admin.TabularInline):
    model = DeviceTest
    extra = 5


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """Admin for Devices."""

    list_display = ("device_type", "device_part")
    inlines = [DeviceSpecificationInline, DeviceTestInline]


class TestInstanceResultInline(admin.TabularInline):
    model = TestInstanceResult
    extra = 5


class TestInstanceSpecificationInline(admin.TabularInline):
    model = TestInstanceSpecification
    extra = 5


@admin.register(TestInstance)
class TestInstanceAdmin(admin.ModelAdmin):
    """Admin for Test Instances."""

    list_display = ("device_type", "device_part", "technician", "date")
    inlines = [TestInstanceResultInline, TestInstanceSpecificationInline]
