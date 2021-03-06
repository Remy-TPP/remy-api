import os
from django.conf import settings
from django.shortcuts import _get_queryset
from django.utils.http import urlencode
from django.urls import reverse
from pint import UnitRegistry
import qrcode


ureg = UnitRegistry()
ureg.load_definitions(os.path.join(settings.BASE_DIR, 'common/unit_definitions/units.txt'))
Q_ = ureg.Quantity


def query_reverse(viewname, kwargs=None, query_kwargs=None):
    """
    Custom reverse to add a query string after the url
    Example usage:
    url = my_reverse('my_test_url', kwargs={'pk': object.id}, query_kwargs={'next': reverse('home')})
    """
    url = reverse(viewname, kwargs=kwargs)

    if query_kwargs:
        # remove items with value None
        query_kwargs = {k: v for k, v in query_kwargs.items() if v is not None}

    if query_kwargs:
        return u'%s?%s' % (url, urlencode(query_kwargs))

    return url


def get_object_or_none(klass, *args, **kwargs):
    """
    Uses get() to return an object or None if the object does not exist.
    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.
    Note: Like with get(), a MultipleObjectsReturned will be raised if more than one
    object is found.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None


def qr_image_from_string(s):
    return qrcode.make(s)
