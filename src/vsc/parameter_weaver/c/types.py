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
'''C types and implementation of their methods for validation and formatting'''

import re

from vsc.parameter_weaver.base_validator import ParameterDefinitionError
from vsc.parameter_weaver.params import VarType
from vsc.util import Indenter

class CType(VarType):

    def __init__(self, name, enduser_name):
        super(CType, self).__init__(name, enduser_name)

    def is_valid_var_name(self, var_name):
        if not re.match(r'^[A-Za-z_]\w*$', var_name):
            msg = "not a valid name for type '{0}'".format(self.name)
            raise ParameterDefinitionError(msg)

    def validation_function(self, name):
        return '1'

    @property
    def struct_sep(self):
        return '->'

    @property
    def input_format_string(self):
        return self.format_string()

    def input_tmpl(self, name):
        return '"{0} = %[^\\n]"'.format(name)


class Int(CType):

    def __init__(self):
        super(Int, self).__init__('int', enduser_name='integer')
        
    def is_of_type(self, value):
        if not re.match(r'^(?:\+|-)?[0-9]+$', value):
            msg = "value '{0}' is invalid for type '{1}'".format(value, self.name)
            raise ParameterDefinitionError(msg)

    def input_conversion(self, var, indent=None):
        return '{0} = atoi(argv_str);'.format(var)

    @property
    def format_string(self):
        return '%d';

    def validation_function(self, name):
        return 'isIntCL({0}, 0)'.format(name)


class Long(CType):

    def __init__(self):
        super(Long, self).__init__('long', enduser_name='long integer')
        
    def is_of_type(self, value):
        if not re.match(r'^(?:\+|-)?[0-9]+L?$', value):
            msg = "value '{0}' is invalid for type '{1}'".format(value, self.name)
            raise ParameterDefinitionError(msg)

    def input_conversion(self, var, indent=None):
        return '{0} = atol(argv_str);'.format(var)

    @property
    def format_string(self):
        return '%ld'

    def validation_function(self, name):
        return 'isLongCL({0}, 0)'.format(name)


class Float(CType):

    def __init__(self):
        super(Float, self).__init__('float', 'SP float')
        
    def is_of_type(self, value):
        re1 = r'^(?:\+|-)?[0-9]+(\.[0-9]*)?((e|E)(\+|-)?[0-9]+)?$'
        re2 = r'^(?:\+|-)?[0-9]*\.[0-9]+((e|E)(\+|-)?[0-9]+)?$'
        if not re.match(re1, value) and not re.match(re2, value):
            msg = "value '{0}' is invalid for type '{1}'".format(value, self.name)
            raise ParameterDefinitionError(msg)

    def input_conversion(self, var, indent=None):
        return '{0} = atof(argv_str);'.format(var)

    @property
    def format_string(self):
        return '%.7f'

    def validation_function(self, name):
        return 'isFloatCL({0}, 0)'.format(name)


class Double(CType):

    def __init__(self):
        super(Double, self).__init__('double', 'DP float')
        
    def is_of_type(self, value):
        re1 = r'^(?:\+|-)?[0-9]+(\.[0-9]*)?((e|E)(\+|-)?[0-9]+)?$'
        re2 = r'^(?:\+|-)?[0-9]*\.[0-9]+((e|E)(\+|-)?[0-9]+)?$'
        if not re.match(re1, value) and not re.match(re2, value):
            msg = "value '{0}' is invalid for type '{1}'".format(value, self.name)
            raise ParameterDefinitionError(msg)

    def input_conversion(self, var, indent=None):
        return '{0} = atof(argv_str);'.format(var)

    @property
    def format_string(self):
        return '%.16lf'

    def validation_function(self, name):
        return 'isDoubleCL({0}, 0)'.format(name)


class Bool(CType):

    def __init__(self):
        super(Bool, self).__init__('bool', 'boolean')

    def is_of_type(self, value):
        if value != 'true' and value != 'false' and not re.match(r'^(?:\+|-)?[0-9]+$', value):
            msg = "value '{0}' is invalid for type '{1}'".format(value, self.name)
            raise ParameterDefinitionError(msg)
        
    def input_conversion(self, var, indent):
        indenter = Indenter(indent)
        indenter.add('if (!strncmp("false", argv_str, 6)) {').incr()
        indenter.add('{0} = false;'.format(var))
        indenter.decr().add('} else if (!strncmp("true", argv_str, 5)) {').incr()
        indenter.add('{0} = true;'.format(var))
        indenter.decr().add('} else {').incr()
        indenter.add('{0} = atoi(argv_str);'.format(var))
        indenter.decr().add('}')
        return indenter.text()

    @property
    def format_string(self):
        return '%d'


class CharPtr(CType):

    def __init__(self):
        super(CharPtr, self).__init__('char *', 'string')
        
    def is_of_type(self, value):
        if not re.match(r'^("|\').*\1$', value):
            msg = "value '{0}' is invalid for type '{1}'".format(value, self.name)
            raise ParameterDefinitionError(msg)

    def input_conversion(self, var, indent=None):
        indenter = Indenter('\t')
        indenter.add('char *tmp;')
        indenter.add('int len = strlen(argv_str);')
        indenter.add('free({var});')
        indenter.add('if (!(tmp = (char *) calloc(len + 1, sizeof(char))))')
        indenter.incr().add('errx(EXIT_CL_ALLOC_FAIL, "can not allocate char* field");')
        indenter.decr()
        indenter.add('{var} = strncpy(tmp, argv_str, len + 1);')
        return indenter.text().format(var=var)

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

