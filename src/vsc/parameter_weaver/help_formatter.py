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

from textwrap import fill

class HelpFormatter(object):
    '''Formatter for application usage messages'''

    def __init__(self, params, pre_params='', post_params='',
                 application=None, description=None, copyright=None):
        self._is_flag_boolean = True
        self._params = params
        self._pre_params = pre_params
        self._post_params = post_params
        self._application = application
        self._description = description
        self._copyright = copyright

    @property
    def is_flag_boolean(self):
        '''returns True if the boolean type is such that the presence
           of a flag indicates True, its absence False'''
        return self._is_flag_boolean

    @is_flag_boolean.setter
    def is_flag_boolean(self, value):
        self._is_flag_boolean = value

    @property
    def params(self):
        return self._params

    @property
    def pre_params(self):
        return self._pre_params

    @pre_params.setter
    def pre_params(self, pre_params):
        self._pre_params = pre_params

    @property
    def post_params(self):
        return self._post_params

    @post_params.setter
    def post_params(self, post_params):
        self._post_params = post_params

    @property
    def application(self):
        return self._application

    @application.setter
    def application(self, appl):
        self._application = appl

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, descr):
        self._description = descr

    @property
    def copyright(self):
        return self._copyright

    @copyright.setter
    def copyright(self, copyright):
        self._copyright = copyright

    def create_help(self):
        '''create a usage string based on the parameter descriptions'''
        help_lines = []
        param_strs = []
        for param in self.params:
            param_type = type=param.type.enduser_name
            if param_type == 'boolean' and self.is_flag_boolean:
                param_str = '-{name}'.format(name=param.name)
            else:
                param_str = '-{name} <{type}>'.format(name=param.name,
                                                      type=param_type)
            param_strs.append(param_str)
            help_line = '  {param}'.format(param=param_str)
            if param.description:
                offset = len(help_line) + 2
                help_line += ': {descr}'.format(descr=param.description)
                if param_type == 'string':
                    help_line += " (default: '{val}')".format(val=param.default)
                elif param_type != 'boolean' or not self.is_flag_boolean:
                    help_line += ' (default: {val})'.format(val=param.default)
                help_line = fill(help_line, subsequent_indent=' '*offset)
            help_lines.append(help_line)
        param_strs.append('-?')
        help_lines.append('  -?: print this message')
        if self.description:
            description = fill(self.description, initial_indent='  ',
                               subsequent_indent='  ')
            help_lines.insert(0, description)
        if self.application:
            usage_str = 'usage: {appl} {pre} {params} {post}'
            usage = usage_str.format(appl=self.application,
                                      pre=self.pre_params,
                                      post=self.post_params,
                                      params=' '.join(param_strs))
            help_lines.insert(0, usage)
        if self.copyright:
            help_lines.append(self.copyright)
        return '\n'.join(help_lines)

