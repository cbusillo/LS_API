"""Central storage for all config values."""
from django.db import models


class Config(models.Model):
    """Global config values."""

    key = models.CharField(max_length=255, unique=True)
    value = models.TextField()

    def __str__(self) -> str:
        return f"{self.key = } {self.value =}"
