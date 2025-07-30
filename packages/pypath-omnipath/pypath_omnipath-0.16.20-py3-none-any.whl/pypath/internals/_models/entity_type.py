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

import enum

import pypath.share.common as _common


class EntityType(enum.Enum):
    """
    Types of molecular entities.
    """
    GENE = 'gene'
    PROTEIN = 'protein'
    MRNA = 'mrna'
    MIRNA = 'mirna'
    LNCRNA = 'lncrna'
    TRNA = 'trna'
    RRNA = 'rrna'
    RNA = {'rna', MRNA, MIRNA, LNCRNA, TRNA, RRNA}
    COMPOUND = 'compound'
    DRUG = 'compound'
    HORMONE = 'hormone'
    CYTOKINE = 'cytokine'
    LIPID = 'lipid'
    CARBOHYDRATE = 'carbohydrate'
    SACCHARIDE = 'carbohydrate'
    AMINOACID = 'aminoacid'
    PEPTIDE = 'peptide'
    METABOLITE = {
        'metabolite',
        LIPID,
        CARBOHYDRATE,
        AMINOACID,
        PEPTIDE,
        HORMONE,
        CYTOKINE,
    }
    SMALL_MOLECULE = {'small_molecule', COMPOUND} | METABOLITE


    def __eq__(self, other) -> bool:

        other = getattr(other, 'value', other)
        return _common.eq(self.value, other)


    def __contains__(self, other) -> bool:

        return self == other
