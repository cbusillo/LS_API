"""Flask helpers."""
from werkzeug.utils import import_string, cached_property


class LazyView(object):
    """Lazy load a view. From flask docs."""

    def __init__(self, import_name):
        self.__module__, self.__name__ = import_name.rsplit('.', 1)
        self.import_name = import_name

    @cached_property
    def view(self):
        """returns object from string"""
        return import_string(self.import_name)

    def __call__(self, *args, **kwargs):
        """run view which is the object from the string"""
        return self.view(*args, **kwargs)  # pylint: disable=not-callable
