# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""This is called during __init__ and extends the base honeybee class Properties with a new ._ref slot"""

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
###### IMPORTANT ######
## ALL HONEYBEE-CORE / HONEYBEE-ENERGY CLASSES MUST BE IMPORTED **FIRST** BEFORE ANY OF THE
## HONEYBEE-REVIVE EXTENSIONS CAN BE LOADED. SEE ISSUE HERE:
## https://discourse.pollination.cloud/t/honeybee-ph-causing-error/
#


# -- Import the Honeybee-Energy Program and HVAC Items
# -- Import the Honeybee-Energy Materials
# -- Import the Honeybee-Energy Constructions
import honeybee_energy
from honeybee_energy.properties.extension import (
    AllAirSystemProperties,
    DOASSystemProperties,
    EnergyMaterialNoMassProperties,
    EnergyMaterialProperties,
    EnergyMaterialVegetationProperties,
    EnergyWindowFrameProperties,
    EnergyWindowMaterialBlindProperties,
    EnergyWindowMaterialGasCustomProperties,
    EnergyWindowMaterialGasMixtureProperties,
    EnergyWindowMaterialGasProperties,
    EnergyWindowMaterialGlazingsProperties,
    EnergyWindowMaterialShadeProperties,
    EnergyWindowMaterialSimpleGlazSysProperties,
    HeatCoolSystemProperties,
    IdealAirSystemProperties,
    OpaqueConstructionProperties,
    ShadeConstructionProperties,
    WindowConstructionProperties,
    WindowConstructionShadeProperties,
)


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# -- Now that Honeybee-Energy is imported, import the relevant HB-Ref classes

from honeybee_energy_ref.properties.hb_obj import _HBObjectWithReferences

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------


# Step 1)
# set a private ._ref attribute on each relevant HB-Energy Property class to None

# -- Constructions
setattr(OpaqueConstructionProperties, "_ref", None)
setattr(WindowConstructionProperties, "_ref", None)
setattr(WindowConstructionShadeProperties, "_ref", None)
setattr(ShadeConstructionProperties, "_ref", None)

# -- Regular Materials
setattr(EnergyMaterialProperties, "_ref", None)
setattr(EnergyMaterialNoMassProperties, "_ref", None)
setattr(EnergyMaterialVegetationProperties, "_ref", None)

# -- Window Materials
setattr(EnergyWindowMaterialGlazingsProperties, "_ref", None)
setattr(EnergyWindowMaterialSimpleGlazSysProperties, "_ref", None)
setattr(EnergyWindowMaterialShadeProperties, "_ref", None)
setattr(EnergyWindowMaterialBlindProperties, "_ref", None)
setattr(EnergyWindowFrameProperties, "_ref", None)
setattr(EnergyWindowMaterialGasProperties, "_ref", None)
setattr(EnergyWindowMaterialGasCustomProperties, "_ref", None)
setattr(EnergyWindowMaterialGasMixtureProperties, "_ref", None)

# -- HVAC
setattr(AllAirSystemProperties, "_ref", None)
setattr(DOASSystemProperties, "_ref", None)
setattr(HeatCoolSystemProperties, "_ref", None)
setattr(IdealAirSystemProperties, "_ref", None)

# -----------------------------------------------------------------------------

# Step 2)
# create methods to define the public .property.<extension> @property instances on each obj.properties container


def opaque_construction_ref_properties(self):
    if self._ref is None:
        self._ref = _HBObjectWithReferences(self.host)
    return self._ref


def energy_material_ref_properties(self):
    if self._ref is None:
        self._ref = _HBObjectWithReferences(self.host)
    return self._ref


def energy_no_mass_ref_properties(self):
    if self._ref is None:
        self._ref = _HBObjectWithReferences(self.host)
    return self._ref


def energy_vegetation_ref_properties(self):
    if self._ref is None:
        self._ref = _HBObjectWithReferences(self.host)
    return self._ref


def energy_window_glazing_ref_properties(self):
    if self._ref is None:
        self._ref = _HBObjectWithReferences(self.host)
    return self._ref


def energy_window_simple_glazing_system_ref_properties(self):
    if self._ref is None:
        self._ref = _HBObjectWithReferences(self.host)
    return self._ref


def material_window_shade_ref_properties(self):
    if self._ref is None:
        self._ref = _HBObjectWithReferences(self.host)
    return self._ref


def material_window_blind_ref_properties(self):
    if self._ref is None:
        self._ref = _HBObjectWithReferences(self.host)
    return self._ref


def window_construction_ref_properties(self):
    if self._ref is None:
        self._ref = _HBObjectWithReferences(self.host)
    return self._ref


def window_construction_shade_ref_shade(self):
    if self._ref is None:
        self._ref = _HBObjectWithReferences(self.host)
    return self._ref


def window_frame_properties(self):
    if self._ref is None:
        self._ref = _HBObjectWithReferences(self.host)
    return self._ref


def material_gas_properties(self):
    if self._ref is None:
        self._ref = _HBObjectWithReferences(self.host)
    return self._ref


def material_gas_custom_properties(self):
    if self._ref is None:
        self._ref = _HBObjectWithReferences(self.host)
    return self._ref


def material_gas_mixture_properties(self):
    if self._ref is None:
        self._ref = _HBObjectWithReferences(self.host)
    return self._ref


def shade_construction_ref_properties(self):
    if self._ref is None:
        self._ref = _HBObjectWithReferences(self.host)
    return self._ref


def pv_properties_ref_properties(self):
    if self._ref is None:
        self._ref = _HBObjectWithReferences(self.host)
    return self._ref


def all_air_system_ref_properties(self):
    if self._ref is None:
        self._ref = _HBObjectWithReferences(self.host)
    return self._ref


def doas_system_ref_properties(self):
    if self._ref is None:
        self._ref = _HBObjectWithReferences(self.host)
    return self._ref


def heat_cool_system_ref_properties(self):
    if self._ref is None:
        self._ref = _HBObjectWithReferences(self.host)
    return self._ref


def ideal_air_system_ref_properties(self):
    if self._ref is None:
        self._ref = _HBObjectWithReferences(self.host)
    return self._ref


# -----------------------------------------------------------------------------

# Step 3)
# add public .ref @property methods to the appropriate Properties classes

# -- Constructions
setattr(OpaqueConstructionProperties, "ref", property(opaque_construction_ref_properties))
setattr(WindowConstructionProperties, "ref", property(window_construction_ref_properties))
setattr(WindowConstructionShadeProperties, "ref", property(window_construction_shade_ref_shade))
setattr(ShadeConstructionProperties, "ref", property(shade_construction_ref_properties))

# -- Regular Materials
setattr(EnergyMaterialProperties, "ref", property(energy_material_ref_properties))
setattr(EnergyMaterialNoMassProperties, "ref", property(energy_no_mass_ref_properties))
setattr(EnergyMaterialVegetationProperties, "ref", property(energy_vegetation_ref_properties))
setattr(EnergyWindowMaterialGlazingsProperties, "ref", property(energy_window_glazing_ref_properties))
setattr(
    EnergyWindowMaterialSimpleGlazSysProperties,
    "ref",
    property(energy_window_simple_glazing_system_ref_properties),
)

# -- Window Materials
setattr(EnergyWindowFrameProperties, "ref", property(window_frame_properties))
setattr(EnergyWindowMaterialGasProperties, "ref", property(material_gas_properties))
setattr(EnergyWindowMaterialGasCustomProperties, "ref", property(material_gas_custom_properties))
setattr(EnergyWindowMaterialGasMixtureProperties, "ref", property(material_gas_mixture_properties))
setattr(EnergyWindowMaterialShadeProperties, "ref", property(material_window_shade_ref_properties))
setattr(EnergyWindowMaterialBlindProperties, "ref", property(material_window_blind_ref_properties))


# -- HVAC
setattr(AllAirSystemProperties, "ref", property(all_air_system_ref_properties))
setattr(DOASSystemProperties, "ref", property(doas_system_ref_properties))
setattr(HeatCoolSystemProperties, "ref", property(heat_cool_system_ref_properties))
setattr(IdealAirSystemProperties, "ref", property(ideal_air_system_ref_properties))
