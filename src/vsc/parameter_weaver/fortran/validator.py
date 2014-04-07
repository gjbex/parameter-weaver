'''validator for Fortran programmign language'''

from vsc.parameter_weaver.base_validator import BaseValidator
from vsc.parameter_weaver.params import VarType
from vsc.parameter_weaver.fortran.types import Integer, Real, DoublePrecision, CharacterArray, Logical

class Validator(BaseValidator):

    def __init__(self):
        super(Validator, self).__init__()
        self._programming_language = 'Fortran'
        self.add_var_type(Integer())
        self.add_var_type(Real())
        self.add_var_type(DoublePrecision())
        self.add_var_type(CharacterArray())
        self.add_var_type(Logical())

