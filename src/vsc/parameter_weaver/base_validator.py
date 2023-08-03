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
'''module containing base class for Parameter validators, this class has to be
subclassed for every language implementation'''

from params import WeaverError

class ParameterDefinitionError(WeaverError):
    '''base class for exceptions in parameter definition'''

    def __init__(self, msg):
        super(ParameterDefinitionError, self).__init__(msg)
        self._name = None
        self._line_no = None

    @property
    def msg(self):
        return self._msg

    @property
    def parameter_name(self):
        return self._name

    @parameter_name.setter
    def parameter_name(self, name):
        self._name = name

    @property
    def line_no(self):
        return self._line_no

    @line_no.setter
    def line_no(self, line_no):
        self._line_no = line_no

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, file_name):
        self._file_name = file_name

    def __str__(self):
        return "{msg} for '{name}' in {file}, line {line_no}".format(
                msg=self.msg, name=self.parameter_name, file=self.file_name,
                line_no=self.line_no)

import re

class BaseValidator(object):
    '''elementary validator for Parameter arguments'''

    def __init__(self):
        self._types = {}
        self._programming_language = None

    def add_var_type(self, var_type):
        self._types[var_type.name] = var_type

    def has_type(self, type_name):
        return self._types.has_key(type_name)

    def get_type(self, type_name):
        if self.has_type(type_name):
            return self._types[type_name]
        error = ParameterDefinitionError(
                "type '{0}' is unknown for language {1}".format(type,
                    self.programming_language))
        raise error

    def types(self):
        return self._types.keys()

    @property
    def programming_language(self):
        return self._programming_language

    def validate(self, type, name, default):
        '''method to validate a list of valuess that are to be used to construct
           a Parameter.  The first element is a type, the second a name, the third
           a default value and the optional fourth is a description of the semantics'''
        if not self.has_type(type):
            error = ParameterDefinitionError(
                    "type '{0}' is unknown for language {1}".format(type,
                        self.programming_language))
            error.parameter_name = name
            raise error
        try:
            self._types[type].is_valid_var_name(name)
            self._types[type].is_of_type(default)
        except ParameterDefinitionError as error:
            error.parameter_name = name
            raise error

    def is_valid_type_name(self, type_name):
        return re.match(r'^[A-Za-z_]\w*$', type_name)

