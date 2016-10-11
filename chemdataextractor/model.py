# -*- coding: utf-8 -*-
"""
chemdataextractor.model
~~~~~~~~~~~~~~~~~~~~~~~

Data model for extracted information.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import copy
from abc import ABCMeta
from collections import Sequence, MutableSequence
import json
import logging

import six


log = logging.getLogger(__name__)


class BaseType(six.with_metaclass(ABCMeta)):

    # This is assigned by ModelMeta to match the attribute on the Model
    name = None

    def __init__(self, default=None, null=False, required=False, contextual=False):
        """

        :param default: (Optional) The default value for this field if none is set.
        :param bool null: (Optional) Include in serialized output even if value is None. Default False.
        :param bool required: (Optional) Whether a value is required. Default False.
        :param bool contextual: (Optional) Whether this value is contextual. Default False.
        """
        self.default = default
        self.null = null
        self.required = required
        self.contextual = contextual

    def __get__(self, instance, owner):
        """Descriptor for retrieving a value from a field in a Model."""
        # Check if Model class is being called, rather than Model instance
        if instance is None:
            return self
        # Get value from Model instance if available
        value = instance._values.get(self.name)
        # If value is None or empty string then return the default value, if set
        # if value in [None, ''] and self.default is not None:
        #     return self.default
        return value

    def __set__(self, instance, value):
        """Descriptor for assigning a value to a field in a Model."""
        instance._values[self.name] = self.process(value)

    def process(self, value):
        """Convert an assigned value into the desired data format."""
        return value

    def serialize(self, value, primitive=False):
        """Serialize this field."""
        if hasattr(value, 'serialize'):
            # i.e. value is a nested model
            return value.serialize(primitive=primitive)
        else:
            return value


class StringType(BaseType):
    """"""
    pass


class FloatType(BaseType):
    """An floating point number field."""

    def process(self, value):
        """Convert value to a float."""
        return float(value)


class ModelType(BaseType):

    def __init__(self, model, **kwargs):
        self.model_class = model
        self.model_name = self.model_class.__name__
        super(ModelType, self).__init__(**kwargs)

    def serialize(self, value, primitive=False):
        """Serialize this field."""
        return value.serialize(primitive=primitive)


class ListType(BaseType):

    def __init__(self, field, default=None, **kwargs):
        super(ListType, self).__init__(**kwargs)
        self.field = field
        self.default = default if default is not None else []

    # def __get__(self, instance, owner):
    #     """Descriptor for retrieving a value from a field in a Model."""
    #     # Check if Model class is being called, rather than Model instance
    #     if instance is None:
    #         return self
    #     # Get value from Model instance if available
    #     value = instance._values.get(self.name)
    #     # If value is None or empty string then return the default value, if set
    #     if value in [None, '', []]:
    #         return self.default if self.default is not None else []
    #     return value

    def serialize(self, value, primitive=False):
        """Serialize this field."""
        return [self.field.serialize(v, primitive=primitive) for v in value]


class ModelMeta(ABCMeta):
    """"""

    def __new__(mcs, name, bases, attrs):
        fields = {}
        for attr_name, attr_value in six.iteritems(attrs):
            if isinstance(attr_value, BaseType):
                # Set the name attribute on the Type to the attribute name on the Model
                attr_value.name = six.text_type(attr_name)
                fields[attr_name] = attr_value
        cls = super(ModelMeta, mcs).__new__(mcs, name, bases, attrs)
        cls.fields = cls.fields.copy()
        cls.fields.update(fields)
        return cls

    def __setattr__(cls, key, value):
        if isinstance(value, BaseType):
            value.name = six.text_type(key)
            cls.fields[key] = value
        return super(ModelMeta, cls).__setattr__(key, value)


@six.python_2_unicode_compatible
class BaseModel(six.with_metaclass(ModelMeta)):
    """"""

    fields = {}

    def __init__(self, **raw_data):
        """"""
        self._values = {}
        for key, value in six.iteritems(raw_data):
            setattr(self, key, value)
        # Set defaults
        for key, field in six.iteritems(self.fields):
            if key not in raw_data:
                setattr(self, key, copy.copy(field.default))

    def __repr__(self):
        return '<%s>' % (self.__class__.__name__,)

    def __str__(self):
        return '<%s>' % (self.__class__.__name__,)

    def __eq__(self, other):
        # TODO: Check this actually works as expected (what about default values?)
        if isinstance(other, self.__class__):
            return self._values == other._values
        return False

    def __iter__(self):
        return iter(self.fields)

    def __delattr__(self, attr):
        """Handle deletion of field values by setting to default if specified."""
        # Set to default value
        if attr in self.fields:
            setattr(self, attr, self.fields[attr].default)
        else:
            super(BaseModel, self).__delattr__(attr)

    def __getitem__(self, key):
        """Redirect dictionary-style field access to attribute-style."""
        try:
            if key in self.fields:
                return getattr(self, key)
        except AttributeError:
            pass
        raise KeyError(key)

    def __setitem__(self, key, value):
        """Redirect dictionary-style field setting to attribute-style."""
        if key not in self.fields:
            raise KeyError(key)
        return setattr(self, key, value)

    def __contains__(self, name):
        try:
            val = getattr(self, name)
            return val is not None
        except AttributeError:
            return False

    def keys(self):
        return list(iter(self))

    def items(self):
        return [(k, getattr(self, k)) for k in self]

    def values(self):
        return [getattr(self, k) for k in self]

    def get(self, key, default=None):
        return getattr(self, key, default)

    # def validate(self):
    #     """"""
    #     for field_name in self:
    #         self.fields[field_name].validate()

    @property
    def is_contextual(self):
        for k in self:
            value = getattr(self, k)
            field = self.fields.get(k)
            # Not contextual if any contextual=False field has a value
            if value not in [None, '', []]:
                # If a ListType, it depends on the contained type
                if isinstance(field, ListType):
                    # If a list of Models, not contextual if any of them isn't
                    if isinstance(field.field, ModelType):
                        for model_value in value:
                            if not model_value.is_contextual:
                                return False
                    elif not field.field.contextual:
                        return False
                else:
                    # If a single Model type, not contextual if it isn't
                    if isinstance(field, ModelType):
                        if not value.is_contextual:
                            return False
                    elif not field.contextual:
                        return False
        return True

    def serialize(self, primitive=False):
        """Convert Model to python dictionary."""
        # Serialize fields to a dict
        data = {}
        for field_name in self:
            value = getattr(self, field_name)
            field = self.fields.get(field_name)
            if value is not None:
                value = field.serialize(value, primitive=primitive)
            # Skip empty fields unless field.null
            if not field.null and value in [None, '', []]:
                continue
            data[field.name] = value
        return data

    def to_json(self, *args, **kwargs):
        """Convert Model to JSON."""
        return json.dumps(self.serialize(primitive=True), *args, **kwargs)


@six.python_2_unicode_compatible
class ModelList(MutableSequence):
    """Wrapper around a list of Models objects to facilitate operations on all at once."""

    def __init__(self, *models):
        self.models = list(models)

    def __getitem__(self, index):
        return self.models[index]

    def __setitem__(self, index, value):
        self.models[index] = value

    def __delitem__(self, index):
        del self.models[index]

    def __len__(self):
        return len(self.models)

    def __repr__(self):
        return self.models.__repr__()

    def __str__(self):
        return self.models.__str__()

    def insert(self, index, value):
        self.models.insert(index, value)

    def serialize(self):
        """Serialize to a list of python dictionaries."""
        return [e.serialize() for e in self.models]

    def to_json(self, *args, **kwargs):
        """Convert ModelList to JSON."""
        return json.dumps(self.serialize(), *args, **kwargs)


class UvvisPeak(BaseModel):
    #: Peak value, i.e. wavelength
    value = StringType()
    #: Peak value units
    units = StringType(contextual=True)
    # Extinction value
    extinction = StringType()
    # Extinction units
    extinction_units = StringType(contextual=True)
    # Peak shape information (e.g. shoulder, broad)
    shape = StringType()


class UvvisSpectrum(BaseModel):
    solvent = StringType(contextual=True)
    temperature = StringType(contextual=True)
    temperature_units = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    apparatus = StringType(contextual=True)
    peaks = ListType(ModelType(UvvisPeak))


class IrPeak(BaseModel):
    value = StringType()
    units = StringType(contextual=True)
    strength = StringType()
    bond = StringType()


class IrSpectrum(BaseModel):
    solvent = StringType(contextual=True)
    temperature = StringType(contextual=True)
    temperature_units = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    apparatus = StringType(contextual=True)
    peaks = ListType(ModelType(IrPeak))


class NmrPeak(BaseModel):
    shift = StringType()
    intensity = StringType()
    multiplicity = StringType()
    coupling = StringType()
    coupling_units = StringType(contextual=True)
    number = StringType()
    assignment = StringType()


class NmrSpectrum(BaseModel):
    nucleus = StringType(contextual=True)
    solvent = StringType(contextual=True)
    frequency = StringType(contextual=True)
    frequency_units = StringType(contextual=True)
    standard = StringType(contextual=True)
    temperature = StringType(contextual=True)
    temperature_units = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    apparatus = StringType(contextual=True)
    peaks = ListType(ModelType(NmrPeak))


class MeltingPoint(BaseModel):
    """A melting point measurement."""
    value = StringType()
    units = StringType(contextual=True)
    solvent = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    apparatus = StringType(contextual=True)


class QuantumYield(BaseModel):
    """A quantum yield measurement."""
    value = StringType()
    units = StringType(contextual=True)
    solvent = StringType(contextual=True)
    type = StringType(contextual=True)
    standard = StringType(contextual=True)
    standard_value = StringType(contextual=True)
    standard_solvent = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    temperature = StringType(contextual=True)
    temperature_units = StringType(contextual=True)
    apparatus = StringType(contextual=True)


class FluorescenceLifetime(BaseModel):
    """A fluorescence lifetime measurement."""
    value = StringType()
    units = StringType(contextual=True)
    solvent = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    temperature = StringType(contextual=True)
    temperature_units = StringType(contextual=True)
    apparatus = StringType(contextual=True)


class ElectrochemicalPotential(BaseModel):
    """An oxidation or reduction potential, from cyclic voltammetry."""
    value = StringType()
    units = StringType(contextual=True)
    type = StringType(contextual=True)
    solvent = StringType(contextual=True)
    concentration = StringType(contextual=True)
    concentration_units = StringType(contextual=True)
    temperature = StringType(contextual=True)
    temperature_units = StringType(contextual=True)
    apparatus = StringType(contextual=True)


class Compound(BaseModel):
    names = ListType(StringType())
    labels = ListType(StringType())
    roles = ListType(StringType())
    nmr_spectra = ListType(ModelType(NmrSpectrum))
    ir_spectra = ListType(ModelType(IrSpectrum))
    uvvis_spectra = ListType(ModelType(UvvisSpectrum))
    melting_points = ListType(ModelType(MeltingPoint))
    quantum_yields = ListType(ModelType(QuantumYield))
    fluorescence_lifetimes = ListType(ModelType(FluorescenceLifetime))
    electrochemical_potentials = ListType(ModelType(ElectrochemicalPotential))

    def merge(self, other):
        """Merge data from another Compound into this Compound."""
        log.debug('Merging: %s and %s' % (self.serialize(), other.serialize()))
        for k in self.keys():
            for new_item in other[k]:
                if new_item not in self[k]:
                    self[k].append(new_item)
        log.debug('Result: %s' % self.serialize())
        return self

    def merge_contextual(self, other):
        """Merge in contextual info from a template Compound."""
        # TODO: This is currently dependent on our data model? Make more robust to schema changes
        # Currently we assume all lists at Compound level, with 1 further potential nested level of lists
        for k in self.keys():
            # print('key: %s' % k)
            for item in self[k]:
                # print('item: %s' % item)
                for other_item in other.get(k, []):
                    # if k in {'names', 'labels'}:
                    #     # TODO: Warn attempting to merge a contextual other that contains names/labels
                    #     continue
                    # print('other_item: %s' % other_item)
                    for otherk in other_item.keys():
                        if isinstance(other_item[otherk], list):
                            if len(other_item[otherk]) > 0 and len(item[otherk]) > 0:
                                other_nested_item = other_item[otherk][0]
                                for othernestedk in other_nested_item.keys():
                                    for nested_item in item[otherk]:
                                        if not nested_item[othernestedk]:
                                            nested_item[othernestedk] = other_nested_item[othernestedk]
                        elif not item[otherk]:
                            item[otherk] = other_item[otherk]
        log.debug('Result: %s' % self.serialize())
        return self

    @property
    def is_unidentified(self):
        if not self.names and not self.labels:
            return True
        return False

    # @property
    # def is_contextual(self):
    #     for k in self:
    #         # Not contextual if we have any names or labels
    #         if k in {'names', 'labels'}:
    #             return False
    #     return super(Compound, self).is_contextual


    @property
    def is_id_only(self):
        """Return True if identifier information only."""
        for key, value in self.items():
            if key not in {'names', 'labels', 'roles'} and value:
                return False
        if self.names or self.labels:
            return True
        return False
