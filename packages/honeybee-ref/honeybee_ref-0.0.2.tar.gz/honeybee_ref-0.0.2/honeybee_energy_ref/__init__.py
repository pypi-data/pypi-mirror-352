# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Package: Honeybee-Energy-Ref Classes and functions.

These classes are designed to be used within a Honeybee-editing environment, such as Rhino or
Grasshopper. These classes will allow for reference data (URLS, etc) to be added to certain
relevant Honeybee entities and logged for later use.
"""

# load all functions that extends honeybee core library
# Make sure the load `honeybee_energy` before anything else to avoid import errors.
import honeybee_energy._extend_honeybee

import honeybee_energy_ref._extend_honeybee_energy_ref
