#
# ParameterWeaver: a code generator to handle command line parameters
# and configuration files for C/C++/Fortran/R/Octave
# Copyright (C) 2013 Geert Jan Bex <geertjan.bex@uhasselt.be>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
'''R types and implementation of their methods for validation and formatting'''

import re

from vsc.parameter_weaver.base_validator import ParameterDefinitionError
from vsc.parameter_weaver.params import VarType
from vsc.util import Indenter

class RType(VarType):

    def __init__(self, name):
        super(RType, self).__init__(name)

    def is_valid_var_name(self, var_name):
        if not re.match(r'^[A-Za-z]\w*$', var_name):
            msg = "not a valid name for type '{0}'".format(self.name)
            raise ParameterDefinitionError(msg)

    def validation_function(self, name):
        return 'TRUE'


class Integer(RType):

    def __init__(self):
        super(Integer, self).__init__('integer')
        
    def is_of_type(self, value):
        if not re.match(r'^(?:\+|-)?[0-9]+$', value):
            msg = "value '{0}' is invalid for type '{1}'".format(value, self.name)
            raise ParameterDefinitionError(msg)

    def input_conversion(self, var):
        return '{0} <- as.integer(argv_str)'.format(var)

    @property
    def format_string(self):
        return '%d';

    def validation_function(self, name):
        return'!is.na({0})'.format(name)


class Double(RType):

    def __init__(self):
        super(Double, self).__init__('double')
        
    def is_of_type(self, value):
        re1 = r'^(?:\+|-)?[0-9]+(\.[0-9]*)?((e|E)(\+|-)?[0-9]+)?$'
        re2 = r'^(?:\+|-)?[0-9]*\.[0-9]+((e|E)(\+|-)?[0-9]+)?$'
        if not re.match(re1, value) and not re.match(re2, value):
            msg = "value '{0}' is invalid for type '{1}'".format(value, self.name)
            raise ParameterDefinitionError(msg)

    def input_conversion(self, var):
        return '{0} <- as.double(argv_str)'.format(var)

    @property
    def format_string(self):
        return '%.16f'

    def validation_function(self, name):
        return'!is.na({0})'.format(name)


class Logical(RType):

    def __init__(self):
        super(Logical, self).__init__('logical')

    def is_of_type(self, value):
        if value != 'TRUE' and value != 'T' and value != 'FALSE' and value != 'F':
            msg = "value '{0}' is invalid for type '{1}'".format(value, self.name)
            raise ParameterDefinitionError(msg)
        
    def input_conversion(self, var, indent):
        return '{0} <- as.logical(argv_str)'.format(var)

    @property
    def format_string(self):
        return '%s'


class String(RType):

    def __init__(self):
        super(String, self).__init__('string')
        
    def is_of_type(self, value):
        if not re.match(r'^("|\').*\1$', value):
            msg = "value '{0}' is invalid for type '{1}'".format(value, self.name)
            raise ParameterDefinitionError(msg)

    def input_conversion(self, var):
        return '{0} <- argv_str'.format(var)

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

