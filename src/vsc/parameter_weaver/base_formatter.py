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
class BaseFormatter(object):
    '''Base class that should be implemented for each target
       language'''
       
    def __init__(self, parameters):
        '''Constructor that takes the list of parameters to handle'''
        self._parameters = parameters
        self.indent_string = '\t'
        self._struct_type_name = None
        self._decl_ext = None
        self._def_ext = None
        self._help_str = None

    @property
    def struct_type_name(self):
        '''If the programming language has a struct-like type, specify the
           name for this type'''
        return self._struct_type_name

    @struct_type_name.setter
    def struct_type_name(self, type_name):
        self._struct_type_name = type_name

    @property
    def indent_string(self):
        return self._indent_string

    @indent_string.setter
    def indent_string(self, indent_str):
        self._indent_string = indent_str

    @property
    def help_str(self):
        return self._help_str

    @help_str.setter
    def help_str(self, help):
        self._help_str = help

    def has_help(self):
        return self.help_str is not None

    def declaration(self):
        '''Returns the parameter structure declaration code'''
        return None
        
    def initialization(self):
        '''Returns the parameter initialization code'''
        return None
        
    def parser(self):
        '''Returns the code to parse the command line arguments and assign
           values to the parameter structure'''
        return None
        
    def dumper(self):
        '''Returns the code to dump the parameter values to a file for
           documentation or debugging'''
        return None

    def finalization(self):
        '''Returns the parameter finalization code'''
        return None
        
    def aux_declaration(self):
        '''Returns the declarations needed for functions used in the CLA parser implementation'''
        return None

    def aux_functions(self):
        '''Returns the definitions needed for functions used in the CLA parser implementation'''
        return None

    @property
    def declaration_extension(self):
        '''return the file name extension for declaration files'''
        return self._decl_ext

    @property
    def definition_extension(self):
        '''return the file name extension for definition files'''
        return self._def_ext

    def declaration_file(self):
        '''Returns contents of declaration file'''
        return None

    def definition_file(self):
        '''Returns contents of definition file'''
        return None

