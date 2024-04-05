#!/usr/bin/env python3

import pickle
import os

module_dir = os.path.dirname(__file__)

class UnitCon():
    '''
    Primary  conversion  factors  in  ConversionFactors.xlsx. To
    regenerate   the   fully   connected   network   run  script
    unitexpander.py.
    '''
    conversion_facts = pickle.load(open(os.path.join(
                            module_dir,
                            '..',
                            'data',
                            'conversion_facts.pkl'),'rb'))
    hc = 1239.8424749521
    @classmethod
    def con_factor(cls, source_unit, target_unit):
        '''
        This function returns how much of the target_unit
        is in the source_unit.

        For Angstrom use Å.

        --------
        Examples

        UnitCon.con_factor('Kg','g') -> 1e-3
        UnitCon.con_factor('Ha','Ry') -> 2.0
        '''
        if source_unit == target_unit:
            return 1.
        elif (source_unit, target_unit) in cls.conversion_facts.keys():
            return cls.conversion_facts[(source_unit, target_unit)]
        else:
            raise ValueError('This conversion I know not of.')