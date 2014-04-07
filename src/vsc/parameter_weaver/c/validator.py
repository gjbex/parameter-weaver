'''validator for C programmign language'''

from vsc.parameter_weaver.base_validator import BaseValidator
from vsc.parameter_weaver.params import VarType
from vsc.parameter_weaver.c.types import Int, Long, Float, Double, CharPtr, Bool


class Validator(BaseValidator):

    def __init__(self):
        super(Validator, self).__init__()
        self._programming_language = 'C'
        self.add_var_type(Int())
        self.add_var_type(Long())
        self.add_var_type(Float())
        self.add_var_type(Double())
        self.add_var_type(CharPtr())
        self.add_var_type(Bool())

