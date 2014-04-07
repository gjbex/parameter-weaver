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
''' types and implementation of their methods for validation and formatting''' 

import re

from vsc.parameter_weaver.base_validator import ParameterDefinitionError
from vsc.parameter_weaver.params import VarType
from vsc.util import Indenter

class FortranType(VarType):

    def __init__(self, name):
        super(FortranType, self).__init__(name)

    def is_valid_var_name(self, var_name):
        if not re.match(r'^[A-Za-z]\w*$', var_name):
            msg = "not a valid name for type '{0}'".format(self.name)
            raise ParameterDefinitionError(msg)
    
    def input_conversion(self, var):
        return 'read (argv, fmt=*, iostat=status) {0}'.format(var)


class Integer(FortranType):

    def __init__(self):
        super(Integer, self).__init__('integer')
        
    def is_of_type(self, value):
        if not re.match(r'^(?:\+|-)?[0-9]+$', value):
            msg = "value '{0}' is invalid for type '{1}'".format(value, self.name)
            raise ParameterDefinitionError(msg)

    @property
    def format_string(self):
        return 'I20';


class Real(FortranType):

    def __init__(self):
        super(Real, self).__init__('real')
        
    def is_of_type(self, value):
        re1 = r'^(?:\+|-)?[0-9]+(\.[0-9]*)?((e|E)(\+|-)?[0-9]+)?$'
        re2 = r'^(?:\+|-)?[0-9]*\.[0-9]+((e|E)(\+|-)?[0-9]+)?$'
        if not re.match(re1, value) and not re.match(re2, value):
            msg = "value '{0}' is invalid for type '{1}'".format(value, self.name)
            raise ParameterDefinitionError(msg)

    @property
    def format_string(self):
        return 'F16.7';


class DoublePrecision(FortranType):

    def __init__(self):
        super(DoublePrecision, self).__init__('double precision')
        
    def is_of_type(self, value):
        re1 = r'^(?:\+|-)?[0-9]+(\.[0-9]*)?((d|D)(\+|-)?[0-9]+)?$'
        re2 = r'^(?:\+|-)?[0-9]*\.[0-9]+((d|D)(\+|-)?[0-9]+)?$'
        if not re.match(re1, value) and not re.match(re2, value):
            msg = "value '{0}' is invalid for type '{1}'".format(value, self.name)
            raise ParameterDefinitionError(msg)

    @property
    def format_string(self):
        return 'F24.15';


class CharacterArray(FortranType):

    def __init__(self):
        self._max_len = 1024
        type_name = 'character(len={0})'.format(self.max_len)
        super(CharacterArray, self).__init__(type_name)

    @property
    def max_len(self):
        return self._max_len

    def is_of_type(self, value):
        if not re.match(r'^("|\').*\1$', value):
            msg = "value '{0}' is invalid for type '{1}'".format(value, self.name)
            raise ParameterDefinitionError(msg)

    def input_conversion(self, var):
        return '{0} = trim(argv)'.format(var)

    @property
    def format_string(self):
        return "'''', A, ''''";

    def transform(self, value):
        if value.startswith('"') and value.endswith('"'):
            return value.strip('"')
        elif value.startswith("'") and value.endswith("'"):
            return value.strip("'")
        else:
            msg = "value '{0}' is invalid for type '{1}'".format(value, self.name)
            raise ParameterDefinitionError(msg)


class Logical(FortranType):

    def __init__(self):
        super(Logical, self).__init__('logical')
        self._re_true = re.compile(r'((\.true\.)|t)', re.I)
        self._re_false = re.compile(r'((\.false\.)|f)', re.I)
        
    def is_of_type(self, value):
        if self._re_true.match(value) is None and self._re_false.match(value) is None:
            msg = "value '{0}' is invalid for type '{1}'".format(value, self.name)
            raise ParameterDefinitionError(msg)

    def is_true(self, value):
        return self._re_true.match(value) is not None

    @property
    def format_string(self):
        return 'L'

