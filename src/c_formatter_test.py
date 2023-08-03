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
'''Module to test the C parameter definition formatter'''

import os
import shutil
import subprocess
import unittest

from vsc.parameter_weaver.params import Parameter, ParameterParser, WeaverError
from vsc.parameter_weaver.templatefile import TemplateFile
from vsc.parameter_weaver.c.validator import Validator
from vsc.parameter_weaver.base_validator import ParameterDefinitionError
from vsc.parameter_weaver.help_formatter import HelpFormatter
from vsc.parameter_weaver.c.formatter import Formatter

class CFormatterTest(unittest.TestCase):
    '''Tests for the parameter definition formatter'''

    def  setUp(self):
        TemplateFile.template_dir = 'tmpl'
        file_name = 'tests/good_c.txt'
        parser = ParameterParser(Validator())
        parameters = parser.parse(file_name)
        self._formatter = Formatter(parameters)
        if not os.path.isdir('tmp'):
            os.mkdir('tmp')
        shutil.copy('tests/main.c', 'tmp/main.c')

    def test_declaration_file(self):
        base_name = 'parser'
        try:
            artifacts = self._formatter.get_artifacts(base_name)
            for artifact in artifacts:
                if artifact.name.endswith(f'{base_name}.h'):
                    file_name = artifact.path
                artifact.action(os.path.join('tmp', artifact.name))
            os.chdir('tmp')
            exit_code = subprocess.call(['gcc', '-c', file_name])
        finally:
            os.chdir('..')
        self.assertEqual(0, exit_code)        

    def test_definition_file(self):
        base_name = 'parser'
        try:
            artifacts = self._formatter.get_artifacts(base_name)
            for artifact in artifacts:
                if artifact.name.endswith(f'{base_name}.c'):
                    file_name = artifact.path
                artifact.action(os.path.join('tmp', artifact.name))
            os.chdir('tmp')
            exit_code = subprocess.call(['gcc', '-c', file_name])
        finally:
            os.chdir('..')
        self.assertEqual(0, exit_code)        

    def test_linking(self):
        base_name = 'parser'
        main_file = 'main.c'
        exec_file = 'cl_test'
        try:
            artifacts = self._formatter.get_artifacts(base_name)
            for artifact in artifacts:
                artifact.action(os.path.join('tmp', artifact.name))
            c_files = [x.name for x in artifacts if x.name.endswith('.c')]
            c_files.append(main_file)
            args = ['gcc', '-o', exec_file] + c_files + ['-lm']
            os.chdir('tmp')
            exit_code = subprocess.call(args)
        finally:
            os.chdir('..')
        self.assertEqual(0, exit_code)        

    def test_default_dump_to_file(self):
        main_file = 'main.c'
        exec_file = './cl_test'
        base_name = 'parser'
        try:
            artifacts = self._formatter.get_artifacts(base_name)
            for artifact in artifacts:
                artifact.action(os.path.join('tmp', artifact.name))
            c_files = [x.name for x in artifacts if x.name.endswith('.c')]
            c_files.append(main_file)
            args = ['gcc', '-o', exec_file] + c_files + ['-lm']
            os.chdir('tmp')
            exit_code = subprocess.call(args)
            if exit_code == 0:
                exit_code = subprocess.call([exec_file])
            else:
                self.fail('link failed')
            if exit_code == 0:
                with open('out.txt', 'r') as out:
                    out_string = '\n'.join(out.readlines())
                with open('../tests/out_c.txt', 'r') as target_out:
                    target_out_string = '\n'.join(target_out.readlines())
                self.assertEqual(target_out_string, out_string)
            else:
                self.fail('run failed')
        finally:
            os.chdir('..')
        self.assertEqual(0, exit_code)        


if __name__ == '__main__':
    unittest.main()

