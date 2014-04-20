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
'''module containing the Parameter class definition, the parameter
definition parser and other Parameter related utilities'''

class WeaverError(Exception):
    '''base class for ParameterWeaver exceptions'''

    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg


class Parameter(object):
    '''class representing a parameter'''

    def __init__(self, type, name, default_value, descr=None):
        '''constructor taking the Parameter's name, type and default
           value as arguments'''
        self._name = name
        self._type = type
        self._default = default_value
        self._descr = descr

    @property
    def name(self):
        '''parameter name, read-only attribute'''
        return self._name

    @property
    def type(self):
        '''parameter type, read-only'''
        return self._type

    @property
    def default(self):
        '''default value for parameter, read-only'''
        return self._default

    @property
    def description(self):
        '''description of the parameter, read-only'''
        if self._descr is None:
            return ''
        else:
            return self._descr

    def __repr__(self):
        '''representation of the parameter, as is read from definition
           file'''
        return "'{type}'\t'{name}'\t'{default}'\t'{descr}'".format(
                name=self.name, type=self.type,
                default=self.default, descr=self.description
            )

    def __eq__(self, other):
        '''method to check whether all attributes are the same'''
        return self.__dict__ == other.__dict__


class VarType(object):
    '''Base class for representing types of variables'''

    def __init__(self, name, enduser_name=None):
        '''Constructor, takes type name as parameter'''
        self._name = name
        if enduser_name:
            self._enduser_name = enduser_name
        else:
            self._enduser_name = name

    @property
    def name(self):
        return self._name

    @property
    def enduser_name(self):
        return self._enduser_name

    def is_of_type(self, value):
        if True:
            raise ParameterDefinitionError(
                    "method not implemented for type '{0}'".format(self.name))
        else:
            raise ParameterDefinitionError(
                    "value '{0}' is invalid for type '{1}'".format(value,
                                                                   self.name))

    def is_valid_var_name(self, var_name):
        if True:
            raise ParameterDefinitionError(
                    "method not implemented for type '{0}'".format(self.name))
        else:
            raise ParameterDefinitionError(
                    "not a valid name for type '{0}'".format(self.name))
    
    def is_valid_type_name(self, type_name):
        return self.is_valid_var_name(type_name)

    def transform(self, value):
        return value

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return type(self) == type(other) and self.name == other.name


from base_validator import ParameterDefinitionError

from ConfigParser import SafeConfigParser

class ParameterConfigParser(object):
    '''class to parse a parameter definition file in config format'''

    def __init__(self, validator):
        '''constructor, takes a Validator as argument'''
        self._validator = validator;
        self._cfg = SafeConfigParser()
        self._info = None

    @property
    def get_info(self):
        return self._info

    def parse_file(self, cfg_file):
        self._cfg.readfp(cfg_file)
        if not self._cfg.has_section('parameters'):
            raise WeaverError('defintion file has no parameters section')
        params_info = {}
        for item in self._cfg.items('parameters'):
            param_name, param_prop = item[0].split('.')
            if not param_name in params_info:
                params_info[param_name] = {'description': None}
            params_info[param_name][param_prop] = item[1]
        parameters = []
        for param_name, param_props in params_info.items():
            try:
                self._validator.validate(param_props['type'], param_name,
                                         param_props['default'])
            except ParameterDefinitionError as error:
                error.line_no = line_no
                error.file_name = cfg_file.name
                raise error
            var_type = self._validator.get_type(param_props['type'])
            default = var_type.transform(param_props['default'])
            parameter = Parameter(var_type, param_name, default,
                                  param_props['description'])
            parameters.append(parameter)
        if self._cfg.has_section('info'):
            self._info = {}
            for item in self._cfg.items('info'):
                self._info[item[0]] = item[1]
        return parameters

    def parse(self, cfg_file_name):
        '''parses the given parameter file, returns a list of Parameter
           objects'''
        with open(cfg_file_name, 'rb') as cfg_file:
            return self.parse_file(cfg_file)


import csv
import re

class ParameterCsvParser(object):
    '''class to parse a parameter definition file in CSV format'''

    def __init__(self, validator, delimiter=None):
        '''constructor, takes a Validator as argument'''
        self._validator = validator;
        self._delimiter = delimiter
        self._comment_line_pattern = re.compile(r'^\s*#.*$')

    @property
    def delimiter(self):
        return self._delimiter

    def is_comment(self, line):
        '''returns true if line is a comment'''
        return self._comment_line_pattern.match(line) is not None;

    def is_data_row(self, row):
        return not (row['name'] is None and self.is_comment(row['type']))

    def parse_file(self, csv_file):
        if self.delimiter is None:
            try:
                dialect = csv.Sniffer().sniff(csv_file.read(1024))
            except csv.Error as error:
                raise WeaverError('format autodetect for parameter '
                                  'definition failed, check file format')
            csv_file.seek(0)
            csv_reader = csv.DictReader(csv_file,
                    fieldnames=['type', 'name', 'default', 'description'],
                    restkey='rest', restval=None, dialect=dialect)
        else:
            csv_reader = csv.DictReader(csv_file, delimiter=self.delimiter,
                    fieldnames=['type', 'name', 'default', 'description'],
                    restkey='rest', restval=None)
        parameters = []
        line_no = 0
        for row in csv_reader:
            line_no += 1
            if not self.is_data_row(row):
                continue
            try:
                self._validator.validate(row['type'], row['name'],
                                         row['default'])
            except ParameterDefinitionError as error:
                error.line_no = line_no
                error.file_name = csv_file.name
                raise error
            var_type = self._validator.get_type(row['type'])
            default = var_type.transform(row['default'])
            parameter = Parameter(var_type, row['name'], default,
                                  row['description'])
            parameters.append(parameter)
        return parameters

    def parse(self, parameter_file_name):
        '''parses the given parameter file, returns a list of Parameter
           objects'''
        with open(parameter_file_name, 'rb') as csv_file:
            return self.parse_file(csv_file)

