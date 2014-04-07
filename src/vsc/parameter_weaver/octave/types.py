'''Octave types and implementation of their methods for validation and formatting'''

import re

from vsc.parameter_weaver.base_validator import ParameterDefinitionError
from vsc.parameter_weaver.params import VarType
from vsc.util import Indenter

class OctaveType(VarType):

    def __init__(self, name):
        super(OctaveType, self).__init__(name)

    def is_valid_var_name(self, var_name):
        if not re.match(r'^[A-Za-z]\w*$', var_name):
            msg = "not a valid name for type '{0}'".format(self.name)
            raise ParameterDefinitionError(msg)

    def validation_function(self, name):
        return '1'


class Double(OctaveType):

    def __init__(self):
        super(Double, self).__init__('double')
        
    def is_of_type(self, value):
        re1 = r'^(?:\+|-)?[0-9]+(\.[0-9]*)?((e|E)(\+|-)?[0-9]+)?$'
        re2 = r'^(?:\+|-)?[0-9]*\.[0-9]+((e|E)(\+|-)?[0-9]+)?$'
        if not re.match(re1, value) and not re.match(re2, value):
            msg = "value '{0}' is invalid for type '{1}'".format(value, self.name)
            raise ParameterDefinitionError(msg)

    def input_conversion(self, var):
        return '{0} = str2double(argv_str);'.format(var)

    @property
    def format_string(self):
        return '%.16f'

    def validation_function(self, name):
        return'!isnan(str2double({0}))'.format(name)


class Logical(OctaveType):

    def __init__(self):
        super(Logical, self).__init__('logical')

    def is_of_type(self, value):
        re1 = r'^(?:\+|-)?[0-9]+(\.[0-9]*)?((e|E)(\+|-)?[0-9]+)?$'
        re2 = r'^(?:\+|-)?[0-9]*\.[0-9]+((e|E)(\+|-)?[0-9]+)?$'
        if not re.match(re1, value) and not re.match(re2, value):
            msg = "value '{0}' is invalid for type '{1}'".format(value, self.name)
            raise ParameterDefinitionError(msg)
        
    def input_conversion(self, var, indent):
        return '{0} = logical(str2double(argv_str));'.format(var)

    @property
    def format_string(self):
        return '%1d'


class String(OctaveType):

    def __init__(self):
        super(String, self).__init__('string')
        
    def is_of_type(self, value):
        if not re.match(r'^("|\').*\1$', value):
            msg = "value '{0}' is invalid for type '{1}'".format(value, self.name)
            raise ParameterDefinitionError(msg)

    def input_conversion(self, var):
        return '{0} = char(argv_str);'.format(var)

    def transform(self, value):
        if value.startswith('"') and value.endswith('"'):
            return value.strip('"')
        elif value.startswith("'") and value.endswith("'"):
            return value.strip("'")
        else:
            msg = "value '{0}' is invalid for type '{1}'".format(value, self.name)
            raise ParameterDefinitionError(msg)

    @property
    def format_string(self):
        return '%s'

