#!/usr/bin/env python
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
'''Module to test the Fortran parameter definition formatter'''

import os
import shutil
import subprocess
import unittest

from vsc.parameter_weaver.params import Parameter, ParameterParser, WeaverError
from vsc.parameter_weaver.fortran.validator import Validator
from vsc.parameter_weaver.base_validator import ParameterDefinitionError
from vsc.parameter_weaver.fortran.formatter import Formatter

class FortranFormatterTest(unittest.TestCase):
    '''Tests for the parameter definition formatter'''

    def  setUp(self):
        file_name = 'tests/good_fortran.txt'
        parser = ParameterParser(Validator())
        parameters = parser.parse(file_name)
        self._formatter = Formatter(parameters)
        if not os.path.isdir('tmp'):
            os.mkdir('tmp')
        shutil.copy('tests/main.f90', 'tmp/main.f90')
        shutil.copy('tests/flag_main.f90', 'tmp/flag_main.f90')

    def test_module(self):
        base_name = 'parser'
        artifacts = self._formatter.get_artifacts(base_name)
        artifacts[0].action(os.path.join('tmp', artifacts[0].name))
        file_name = artifacts[0].name
        os.chdir('tmp')
        try:
            exit_code = subprocess.call(['gfortran', '-c', '-std=f2003',
                                                     file_name])
        finally:
            os.chdir('..')
        self.assertEqual(0, exit_code)        

    def test_linking(self):
        base_name = 'parser'
        module_file = 'parser.f90'
        main_file = 'main.f90'
        exec_file = 'cl_test'
        artifacts = self._formatter.get_artifacts(base_name)
        artifacts[0].action(os.path.join('tmp', artifacts[0].name))
        os.chdir('tmp')
        try:
            exit_code = subprocess.call(['gfortran', '-o', exec_file,
                                         module_file, main_file,
                                                '-lm'])
        finally:
            os.chdir('..')
        self.assertEqual(0, exit_code)        

    def test_default_dump_to_file(self):
        base_name = 'parser'
        module_file = 'parser.f90'
        main_file = 'main.f90'
        exec_file = './cl_test_f'
        artifacts = self._formatter.get_artifacts(base_name)
        artifacts[0].action(os.path.join('tmp', artifacts[0].name))
        os.chdir('tmp')
        try:
            exit_code = subprocess.call(['gfortran', '-o', exec_file,
                                                     module_file, main_file,
                                                     '-lm'])
            if exit_code == 0:
                exit_code = subprocess.call([exec_file])
            else:
                self.fail('link failed')
            if exit_code == 0:
                with open('out.txt', 'r') as out:
                    out_string = '\n'.join(out.readlines())
                with open('../tests/out_fortran.txt', 'r') as target_out:
                    target_out_string = '\n'.join(target_out.readlines())
                self.assertEqual(target_out_string, out_string)
            else:
                self.fail('run failed')
        finally:
            os.chdir('..')
        self.assertEqual(0, exit_code)        

    def test_flag_dump_to_file(self):
        file_name = 'tests/flag_fortran.txt'
        parser = ParameterParser(Validator())
        parameters = parser.parse(file_name)
        formatter = Formatter(parameters)
        base_name = 'flag_parser'
        main_file = 'flag_main.f90'
        exec_file = './flag'
        artifacts = formatter.get_artifacts(base_name)
        artifacts[0].action(os.path.join('tmp', artifacts[0].name))
        module_file = artifacts[0].name
        os.chdir('tmp')
        try:
            exit_code = subprocess.call(['gfortran', '-o', exec_file,
                                                module_file, main_file,
                                                '-lm'])
            if exit_code == 0:
                exit_code = subprocess.call([exec_file])
            else:
                self.fail('link failed')
            if exit_code == 0:
                with open('out.txt', 'r') as out:
                    out_string = '\n'.join(out.readlines())
                with open('../tests/out_flag_fortran.txt', 'r') as target_out:
                    target_out_string = '\n'.join(target_out.readlines())
                self.assertEqual(target_out_string, out_string)
            else:
                self.fail('run failed')
        finally:
            os.chdir('..')
        self.assertEqual(0, exit_code)        


if __name__ == '__main__':
    unittest.main()

