'''validator for Octave programmign language'''

from vsc.parameter_weaver.base_validator import BaseValidator
from vsc.parameter_weaver.params import VarType
from vsc.parameter_weaver.octave.types import Double, String, Logical


class Validator(BaseValidator):

    def __init__(self):
        super(Validator, self).__init__()
        self._programming_language = 'Octave'
        self.add_var_type(Double())
        self.add_var_type(String())
        self.add_var_type(Logical())

