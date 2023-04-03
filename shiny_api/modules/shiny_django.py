"""functions to work with django models"""
# pylint: disable=wrong-import-position
import django
django.setup()
from django.db import models


def get_updatable_fields(model: type[models.Model]) -> list[str]:
    """Get updatable fields for a model"""
    return [
        field.name for field in model._meta.get_fields()
        if not (
            isinstance(field, models.AutoField) or
            (isinstance(field, models.ForeignKey) and field.auto_created) or
            (hasattr(field, 'primary_key') and field.primary_key)
        )
    ]
    