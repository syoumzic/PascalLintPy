import argparse


class ArgumentParser:
    def __init__(self, script_name: str):
        self.cli_parser = argparse.ArgumentParser(
            prog=script_name,
            description='Программа предназначенная для проверки синтаксиса на языке Pascal',
            epilog='Введите директорию файлов для проверки')

        self.cli_parser.add_argument('path_pattern', help="путь к файлам в виде регулярного выражения")  # positional argument

    def parse(self):
        paths = self.cli_parser.parse_args()
        return paths
