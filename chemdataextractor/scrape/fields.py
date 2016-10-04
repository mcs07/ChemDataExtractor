# -*- coding: utf-8 -*-
"""
chemdataextractor.scrape.fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Fields to define on an entity.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import re

import dateutil.parser
import six

from .base import BaseField
from ..text.processors import strip_querystring


log = logging.getLogger(__name__)


class StringField(BaseField):
    """A string field."""

    def __init__(self, selection, lower=False, upper=False, strip=False, **kwargs):
        """

        :param bool lower: (Optional) Whether to lowercase the string. Default False.
        :param bool upper: (Optional) Whether to uppercase the string. Default False.
        :param bool strip: (Optional) Whether to strip whitespace from start/end. Default False.
        """
        super(StringField, self).__init__(selection, **kwargs)
        self.lower = lower
        self.upper = upper
        self.strip = strip

    def process(self, value):
        value = super(StringField, self).process(value)
        if value is not None:
            if self.strip:
                value = value.strip()
            if self.lower:
                value = value.lower()
            if self.upper:
                value = value.upper()
        return value


class UrlField(StringField):
    """A field with optional URL processing."""

    def __init__(self, selection, strip_querystring=False, **kwargs):
        """

        :param strip_querystring: (Optional) Whether to remove the querystring. Default False.
        """
        self.strip_querystring = strip_querystring
        super(UrlField, self).__init__(selection, **kwargs)

    def process(self, value):
        value = super(UrlField, self).process(value)
        if value is not None and self.strip_querystring:
            value = strip_querystring(value)
        return value


class EntityField(BaseField):
    """A field that contains another Entity."""

    def __init__(self, entity, selection, **kwargs):
        """

        :param entity: The embedded entity.
        """
        self.entity = entity
        super(EntityField, self).__init__(selection, **kwargs)

    def scrape(self, selector, cleaner=None, processor=None):
        """Scrape the value for this field from the selector."""
        value = self.entity.scrape(selector, root=self.selection, xpath=self.xpath)
        return self._post_scrape(value, processor=processor)


class IntField(BaseField):
    """An integer number field."""

    def process(self, value):
        """Convert value to an int."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return None


class FloatField(BaseField):
    """An floating point number field."""

    def process(self, value):
        """Convert value to a float."""
        try:
            return float(value)
        except (ValueError, TypeError):
            return None


class BoolField(BaseField):
    """A boolean field type."""

    def __init__(self, selection, true=re.compile('true|yes|1', re.I), false=re.compile('false|no|0', re.I), **kwargs):
        """

        :param true: Regular expression match that evaluates to True.
        :param false: Regular expression match that evaluates to False.
        """
        self.true = re.compile(true, re.U) if isinstance(true, six.string_types) else true
        self.false = re.compile(false, re.U) if isinstance(false, six.string_types) else false
        super(BoolField, self).__init__(selection, **kwargs)

    def process(self, value):
        if self.true.match(value):
            return True
        elif self.false.match(value):
            return False
        return None


class DateTimeField(BaseField):
    """A datetime field. Depends on python-dateutil."""

    def process(self, value):
        if value == '':
            return None
        try:
            # Ignore year-only values
            if 32 < float(value) < 9999:
                return None
        except ValueError:
            pass
        try:
            return dateutil.parser.parse(value)
        except (TypeError, ValueError):
            return None

    def serialize(self, value):
        return six.text_type(value.isoformat())
