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
import logging

from schematics.models import Model as SchematicsModel
from schematics.types import StringType, BooleanType
from schematics.types.compound import ListType, ModelType


log = logging.getLogger(__name__)


class BaseModel(SchematicsModel):
    """Abstract base class for model objects."""

    class Options:
        # Don't include None values in primitive serialization
        # Warning: Possible future changes, see https://github.com/schematics/schematics/issues/366
        serialize_when_none = False


class UvvisPeak(BaseModel):
    #: Peak value, i.e. wavelength
    value = StringType()
    #: Peak value units
    units = StringType()
    # Extinction value
    extinction = StringType()
    # Extinction units
    extinction_units = StringType()
    # Peak shape information (e.g. shoulder, broad)
    shape = StringType()


class UvvisSpectrum(BaseModel):
    solvent = StringType()
    temperature = StringType()
    temperature_units = StringType()
    concentration = StringType()
    concentration_units = StringType()
    apparatus = StringType()
    peaks = ListType(ModelType(UvvisPeak), default=[])


class IrPeak(BaseModel):
    value = StringType()
    units = StringType()
    strength = StringType()
    bond = StringType()


class IrSpectrum(BaseModel):
    solvent = StringType()
    temperature = StringType()
    temperature_units = StringType()
    concentration = StringType()
    concentration_units = StringType()
    apparatus = StringType()
    peaks = ListType(ModelType(IrPeak), default=[])


class NmrPeak(BaseModel):
    shift = StringType()
    intensity = StringType()
    multiplicity = StringType()
    coupling = StringType()
    coupling_units = StringType()
    number = StringType()
    assignment = StringType()


class NmrSpectrum(BaseModel):
    nucleus = StringType()
    solvent = StringType()
    frequency = StringType()
    frequency_units = StringType()
    standard = StringType()
    temperature = StringType()
    temperature_units = StringType()
    concentration = StringType()
    concentration_units = StringType()
    apparatus = StringType()
    peaks = ListType(ModelType(NmrPeak), default=[])


class MeltingPoint(BaseModel):
    """A melting point measurement."""
    value = StringType()
    units = StringType()
    solvent = StringType()
    concentration = StringType()
    concentration_units = StringType()
    apparatus = StringType()


class QuantumYield(BaseModel):
    """A quantum yield measurement."""
    value = StringType()
    units = StringType()
    solvent = StringType()
    type = StringType()
    standard = StringType()
    standard_value = StringType()
    standard_solvent = StringType()
    concentration = StringType()
    concentration_units = StringType()
    temperature = StringType()
    temperature_units = StringType()
    apparatus = StringType()


class FluorescenceLifetime(BaseModel):
    """A fluorescence lifetime measurement."""
    value = StringType()
    units = StringType()
    solvent = StringType()
    concentration = StringType()
    concentration_units = StringType()
    temperature = StringType()
    temperature_units = StringType()
    apparatus = StringType()


class ElectrochemicalPotential(BaseModel):
    """An oxidation or reduction potential, from cyclic voltammetry."""
    value = StringType()
    units = StringType()
    type = StringType()
    solvent = StringType()
    concentration = StringType()
    concentration_units = StringType()
    temperature = StringType()
    temperature_units = StringType()
    apparatus = StringType()


class Compound(BaseModel):
    names = ListType(StringType(), default=[])
    labels = ListType(StringType(), default=[])
    roles = ListType(StringType(), default=[])
    nmr_spectra = ListType(ModelType(NmrSpectrum), default=[])
    ir_spectra = ListType(ModelType(IrSpectrum), default=[])
    uvvis_spectra = ListType(ModelType(UvvisSpectrum), default=[])
    melting_points = ListType(ModelType(MeltingPoint), default=[])
    quantum_yields = ListType(ModelType(QuantumYield), default=[])
    fluorescence_lifetimes = ListType(ModelType(FluorescenceLifetime), default=[])
    electrochemical_potentials = ListType(ModelType(ElectrochemicalPotential), default=[])

    def merge(self, other):
        """Merge data from another Compound into this Compound."""
        log.debug('Merging: %s and %s' % (self.to_primitive(), other.to_primitive()))
        for k in self.keys():
            for new_item in other[k]:
                if new_item not in self[k]:
                    self[k].append(new_item)
        log.debug('Result: %s' % self.to_primitive())
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
        log.debug('Result: %s' % self.to_primitive())
        return self

    @property
    def is_unidentified(self):
        if not self.names and not self.labels:
            return True
        return False

    @property
    def is_contextual(self):
        for k in self.keys():
            for item in self[k]:
                # Not contextual if we have any names or labels
                if k in {'names', 'labels'}:
                    return False
                # Not contextual if we have any values or peaks values
                if item.get('value') or (item.get('peaks') and any(p.get('value') or p.get('extinction') or p.get('shift') for p in item.get('peaks'))):
                    return False
        return True

    @property
    def is_id_only(self):
        """Return True if identifier information only."""
        for key, value in self.items():
            if key not in {'names', 'labels', 'roles'} and value:
                return False
        if self.names or self.labels:
            return True
        return False
