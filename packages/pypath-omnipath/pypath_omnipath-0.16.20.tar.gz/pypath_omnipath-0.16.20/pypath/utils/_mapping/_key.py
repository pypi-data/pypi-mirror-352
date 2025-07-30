#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#  This file is part of the `pypath` python module
#
#  Copyright 2014-2024
#  EMBL, EMBL-EBI, Uniklinik RWTH Aachen, Heidelberg University
#
#  Authors: see the file `README.rst`
#  Contact: Dénes Türei (turei.denes@gmail.com)
#
#  Distributed under the GPLv3 License.
#  See accompanying file LICENSE.txt or copy at
#      https://www.gnu.org/licenses/gpl-3.0.html
#
#  Website: https://pypath.omnipathdb.org/
#

from typing import NamedTuple

import pypath.internals.models import Entity, Organism


class Identifier(NamedTuple):
    name: str
    entity_type: str
    organism: Organism


class Mapping(NamedTuple):
    source: Identifier
    target: Identifier
    resource: str  # MappingResource in the future?
