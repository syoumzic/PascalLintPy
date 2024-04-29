import configparser
import re
import os

from FileManager import FileManager


class Linter:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('linterConf.ini')

        self.allow_check_tab = int(config['Config']['allow_check_tab'])
        self.tab_value = int(config['Config']['tab_value'])

        self.allow_check_empty_lines = int(config['Config']['allow_check_empty_lines'])
        self.empty_lines_count = int(config['Config']['empty_lines_count'])

        self.allow_check_unnecessary_space = int(config['Config']['allow_check_unnecessary_space'])

        self.allow_check_identifiers = int(config['Config']['allow_check_identifiers'])

        self.identifiers = [
            'and', 'array', 'begin', 'case', 'const', 'div', 'do', 'downto', 'else',
            'end', 'file', 'for', 'function', 'goto', 'if', 'in', 'label', 'mod', 'nil',
            'not', 'of', 'or', 'packed', 'procedure', 'program', 'record', 'repeat',
            'set', 'then', 'to', 'type', 'unit', 'until', 'uses', 'var', 'while', 'with'
        ]

        self.pascal_pattern = re.compile(r'^[A-Za-z][a-z0-9]*$')
        self.structures_pattern = re.compile(
            r'((?:var|const)((?:(?: *\w+ *,)* *\w+ *:.*?;)+))|(function.*?\((.*?)\).*?)', flags=re.I)
        self.variables_pattern = re.compile(r'(.*?):.*?;')
        self.variable_pattern = re.compile(r' *(\w+) *')
        self.used_variable_pattern = re.compile(r'\w+')

    def check(self, path):
        document = FileManager.load(path).split('\n')
        self.filename = os.path.basename(path)

        if self.allow_check_empty_lines:
            self.check_empty_lines(document)

        if self.allow_check_tab:
            self.check_tab(document)

        if self.allow_check_identifiers:
            self.check_identifiers(document)

        if self.allow_check_unnecessary_space:
            self.check_space(document)

        self.check_unused_variables(document)

    def print_warning(self, description, i=0, j=0, error_line=None):
        if i == 0 and j == 0:
            print(f'Файл "{self.filename}": Предупреждение: {description}')

        else:
            print(f'Файл "{self.filename}": Предупреждение ({i + 1}:{j + 1}): {description}')

        if error_line:
            print(error_line)
            print(' ' * j + '^')

    def check_empty_lines(self, document):
        empty_line_count = 0

        for i in range(len(document)):
            line = document[i].strip()

            if line.strip() == '':
                empty_line_count += 1

                if empty_line_count > self.empty_lines_count:
                    self.print_warning('обнаружена недопустимая пустая строка', i, 0)

            else:
                empty_line_count = 0

    @staticmethod
    def begin_space_count(str):
        return len(str) - len(str.lstrip())

    def check_tab(self, document):
        current_tab = 0

        for i in range(len(document)):
            line = document[i].rstrip()

            if line.lstrip() == '':
                continue

            split_line = re.split('\W+', line.lstrip())

            if split_line[0].lower() == 'end':
                current_tab -= self.tab_value

            line_space = self.begin_space_count(line)
            if line_space != current_tab:
                self.print_warning('не соблюдены правила табуляции', i, line_space, error_line=line)

            if split_line[0].lower() == 'begin':
                current_tab += self.tab_value

            for j in range(1, len(split_line)):
                lower_word = split_line[j].lower()

                if lower_word == 'begin':
                    current_tab += self.tab_value

                elif lower_word == 'end':
                    current_tab -= self.tab_value

    def check_space(self, document):
        for i in range(len(document)):
            line = document[i].strip()

            for match in re.finditer(' {2,}', line):
                self.print_warning('лишний пробел', i, match.start(), error_line=line)

    @staticmethod
    def split_keep_position(line):
        for m in re.finditer(r'\w+', line):
            yield m.group(0), m.start(), m.end()

    def check_identifiers(self, document):
        for i in range(len(document)):
            line = document[i]
            for word, begin_position, end_position in self.split_keep_position(line):
                if word.lower() in self.identifiers and not re.match(self.pascal_pattern, word):
                    self.print_warning(f'идентификатор "{word}" не соответствует pascal формату идентификатора', i,
                                       begin_position, error_line=line)

    def get_function_end(self, start_position, document):
        begin_count = 0
        end_count = 0

        for keyword, start_keyword, end_keyword in self.split_keep_position(document[start_position:]):
            lower_keyword = keyword.lower()

            if lower_keyword == 'begin':
                begin_count += 1

            elif lower_keyword == 'end':
                end_count += 1

            if begin_count > 0 and begin_count == end_count:
                return end_keyword + start_position

    def check_variables_in_scope(self, scope, variable_structure):
        for variables_match in re.finditer(self.variables_pattern, variable_structure):
            for variable_match in re.finditer(self.variable_pattern, variables_match.group(1)):
                variable = variable_match.group(1)
                if re.findall(self.used_variable_pattern, scope).count(variable) == 1:
                    self.print_warning(f'неиспользуемая переменная {variable}')

    def check_unused_variables(self, document):
        document = ' '.join(document)

        structure_matches = list(re.finditer(self.structures_pattern, document))

        i = 0
        while i < len(structure_matches):
            structure_match = structure_matches[i]

            if structure_match.group(1):
                variable_scope = document
                self.check_variables_in_scope(variable_scope, structure_match.group(2))
                i += 1

            else:
                function_last_index = self.get_function_end(structure_match.start(), document)
                function_scope = document[structure_match.start():function_last_index]

                self.check_variables_in_scope(function_scope, structure_match.group(4) + ';')

                while True:
                    i += 1
                    if i >= len(structure_matches):
                        break
                    inner_structure_match = structure_matches[i]
                    if inner_structure_match.start() > function_last_index:
                        break
                    self.check_variables_in_scope(function_scope, inner_structure_match.group(2))