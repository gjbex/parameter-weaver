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

import re

from vsc.parameter_weaver.base_formatter import BaseFormatter
from vsc.parameter_weaver.temporaryfile import TemporaryFile
from vsc.parameter_weaver.templatefile import TemplateFile
from vsc.parameter_weaver.c.validator import CharPtr, Bool
from vsc.util import Indenter

class Formatter(BaseFormatter):

    def __init__(self, parameters):
        super(Formatter, self).__init__(parameters)
        self.struct_type_name = 'Params'
        self._decl_ext = '.h'
        self._def_ext = '.c'

    def declaration(self):
        indenter = Indenter(self.indent_string)
        indenter.add('typedef struct {{')
        indenter.incr()
        for param in self._parameters:
            indenter.add('{0} {1};'.format(param.type, param.name))
        indenter.decr()
        indenter.add('}} {name};')
        return indenter.text().format(name=self.struct_type_name)

    def init_signature(self):
        return 'void initCL({0} *params)'.format(self.struct_type_name)

    def initialization(self):
        indenter = Indenter(self.indent_string)
        indenter.add('{0} {{'.format(self.init_signature()))
        indenter.incr()
        no_char_ptrs = True
        for param in self._parameters:
            name = param.name
            default = param.default
            if isinstance(param.type, CharPtr):
                if no_char_ptrs:
                    indenter.add('int len;')
                    no_char_ptrs = False
                indenter.add('len = strlen("{0}");'.format(default))
                indenter.add('if (!(params->{0} = (char *) calloc(len + 1, sizeof(char))))'.format(name))
                indenter.incr().add('errx(EXIT_CL_ALLOC_FAIL, "can not allocate {0} field");'.format(name))
                indenter.decr()
                indenter.add('strncpy(params->{0}, "{1}", len + 1);'.format(name, default))
            elif isinstance(param.type, Bool):
                indenter.add('params->{0} = false;'.format(name))
            else:
                indenter.add('params->{0} = {1};'.format(name, default))
        indenter.decr()
        indenter.add('}')
        return indenter.text()

    def parser_signature(self):
        return 'void parseCL({0} *params, int *argc, char **argv[])'.format(self.struct_type_name)

    def parser(self):
        indenter = Indenter(self.indent_string)
        indenter.add('{0} {{'.format(self.parser_signature()))
        indenter.incr()
        indenter.add('char *argv_str;')
        indenter.add('int i = 1;')
        indenter.add('while (i < *argc) {')
        indenter.incr()
        if self.has_help():
            indenter.add(' if (!strncmp((*argv)[i], "-?", 3)) {')
            indenter.incr()
            indenter.add('printHelpCL(stderr);')
            indenter.add('finalizeCL(params);')
            indenter.add('exit(EXIT_SUCCESS);')
            indenter.decr().add('}')
        for param in self._parameters:
            name = param.name
            indenter.add('if (!strncmp((*argv)[i], "-{0}", {1})) {{'.format(name, len(name) + 2))
            indenter.incr()
            if isinstance(param.type, Bool):
                indenter.add('params->{0} = true;'.format(name))
            else:
                indenter.add('shiftCL(&i, *argc, *argv);')
                indenter.add('argv_str = (*argv)[i];')
                val_func = param.type.validation_function('argv_str')
                indenter.add('if (!{0}) {{'.format(val_func)).incr()
                indenter.add('fprintf(stderr, "### error: invalid value for option \'-{0}\' of type {1}\\n");'.format(name, param.type.name))
                indenter.add('exit(EXIT_CL_INVALID_VALUE);')
                indenter.decr().add('}')
                indenter.add(param.type.input_conversion('params->{0}'.format(name)))
            indenter.add('i++;')
            indenter.add('continue;')
            indenter.decr().add('}')
        indenter.add('break;')
        indenter.decr().add('}')
        indenter.add('if (i > 1) {')
        indenter.incr()
        indenter.add('(*argv)[i - 1] = (*argv)[0];')
        indenter.add('*argv = &((*argv)[i - 1]);')
        indenter.add('*argc -= (i - 1);')
        indenter.decr().add('}')
        indenter.decr().add('}')
        return indenter.text()

    def file_parser_signature(self):
        return 'void parseFileCL({0} *params, char *fileName)'.format(self.struct_type_name)

    def file_parser(self):
        indenter = Indenter(self.indent_string)
        indenter.add('{0} {{'.format(self.file_parser_signature())).incr()
        indenter.add('char line_str[MAX_CL_LINE_LEN];')
        indenter.add('char argv_str[MAX_CL_LINE_LEN];')
        indenter.add('FILE *fp;')
        indenter.add('if (!(fp = fopen(fileName, "r"))) {').incr()
        indenter.add('fprintf(stderr, "### error: can not open file \'%s\'\\n", fileName);')
        indenter.add('exit(EXIT_CL_FILE_OPEN_FAIL);')
        indenter.decr().add('}')
        indenter.add('while (fgets(line_str, MAX_CL_LINE_LEN, fp)) {').incr()
        indenter.add('if (isCommentCL(line_str)) continue;')
        indenter.add('if (isEmptyLineCL(line_str)) continue;')
        for param in self._parameters:
            name = param.name
            indenter.add('if (sscanf(line_str, {0}, argv_str) == 1) {{'.format(param.type.input_tmpl(name))).incr()
            val_func = param.type.validation_function('argv_str')
            indenter.add('if (!{0}) {{'.format(val_func)).incr()
            indenter.add('fprintf(stderr, "### error: invalid value for option \'-{0}\' of type {1}\\n");'.format(name, param.type.name))
            indenter.add('exit(EXIT_CL_INVALID_VALUE);')
            indenter.decr().add('}')
            indenter.add(param.type.input_conversion('params->{0}'.format(name), indenter.indent_str))
            if isinstance(param.type, CharPtr):
                indenter.add('stripQuotesCL(params->{0});'.format(name))
            indenter.add('continue;')
            indenter.decr().add('}')
        indenter.add('fprintf(stderr, "### warning, line can not be parsed: \'%s\'\\n", line_str);') 
        indenter.decr().add('}')
        indenter.add('fclose(fp);')
        indenter.decr().add('}')
        return indenter.text()

    def dumper_signature(self):
        return 'void dumpCL(FILE *fp, char prefix[], {0} *params)'.format(self.struct_type_name)

    def dumper(self):
        indenter = Indenter(self.indent_string)
        indenter.add('{0} {{'.format(self.dumper_signature()))
        indenter.incr()
        for param in self._parameters:
            name = param.name
            format_string = param.type.format_string
            if isinstance(param.type, CharPtr):
                format_string = "'{0}'".format(format_string)
            indenter.add('fprintf(fp, "%s{0} = {1}\\n", prefix, params->{0});'.format(name, format_string))
        indenter.decr().add('}')
        return indenter.text()

    def print_help_signature(self):
        return 'void printHelpCL(FILE *fp)'

    def quote_help(self, help_str):
        help_str = re.sub(r'\n', r'\\n', help_str)
        help_str = re.sub(r'\r', r'\\r', help_str)
        help_str = re.sub(r'\t', r'\\t', help_str)
        help_str = re.sub(r'"', r'\\"', help_str)
        help_str = re.sub('%', '%%', help_str)
        return help_str

    def help_printer(self):
        indenter = Indenter(self.indent_string)
        indenter.add('{0} {{'.format(self.print_help_signature()))
        indenter.incr()
        help_str = self.quote_help(self.help_str)
        indenter.add('fprintf(fp, "{0}");'.format(help_str))
        indenter.decr().add('}')
        return indenter.text()


    def finalizer_signature(self):
        return 'void finalizeCL({0} *params)'.format(self.struct_type_name)

    def finalization(self):
        indenter = Indenter(self.indent_string)
        indenter.add('{0} {{'.format(self.finalizer_signature()))
        indenter.incr()
        for param in self._parameters:
            if isinstance(param.type, CharPtr):
                name = param.name
                indenter.add('free(params->{0});'.format(name))
        indenter.decr().add('}')
        return indenter.text()

    def declaration_file(self, base_name):
        '''Returns contents of declaration file'''
        incl_guard = '{0}_HDR'.format(base_name.upper())
        indenter = Indenter(self.indent_string)
        indenter.add('#ifndef {0}'.format(incl_guard))
        indenter.add('#define {0}'.format(incl_guard))
        indenter.add()
        for param in self._parameters:
            if isinstance(param.type, Bool):
                indenter.add('#include <stdbool.h>')
                break
        indenter.add('#include <stdio.h>')
        indenter.add()
        indenter.add(self.declaration())
        indenter.add()
        indenter.add('{0};'.format(self.init_signature()))
        indenter.add('{0};'.format(self.parser_signature()))
        indenter.add('{0};'.format(self.file_parser_signature()))
        indenter.add('{0};'.format(self.dumper_signature()))
        indenter.add('{0};'.format(self.finalizer_signature()))
        if self.has_help():
            indenter.add('{0};'.format(self.print_help_signature()))
        indenter.add()
        indenter.add('#endif')
        return indenter.text()

    def definition_file(self, base_name):
        '''Returns contents of definition file'''
        indenter = Indenter(self.indent_string)
        indenter.add('#include <err.h>')
        indenter.add('#include <stdlib.h>')
        indenter.add('#include <string.h>')
        indenter.add()
        indenter.add('#include "{0}.h"'.format(base_name))
        indenter.add('#include "{0}_aux.h"'.format(base_name))
        indenter.add()
        indenter.add('#define MAX_CL_OPT_LEN 128')
        indenter.add('#define MAX_CL_LINE_LEN 1024')
        indenter.add()
        indenter.add(self.initialization())
        indenter.add()
        indenter.add(self.parser())
        indenter.add()
        indenter.add(self.file_parser())
        indenter.add()
        indenter.add(self.dumper())
        indenter.add()
        indenter.add(self.finalization())
        indenter.add()
        if self.has_help():
            indenter.add(self.help_printer())
        return indenter.text()

    def get_artifacts(self, base_name):
        return [
            TemporaryFile(base_name, '.h', self.declaration_file(base_name)),
            TemporaryFile(base_name, '.c', self.definition_file(base_name)),
            TemplateFile('{0}_aux.c'.format(base_name), 'c/cl_aux.c',
                         {'base_name': base_name}),
            TemplateFile('{0}_aux.h'.format(base_name), 'c/cl_aux.h')]

