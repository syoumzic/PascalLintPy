#!/bin/python3

import sys

from ArgumentParser import ArgumentParser
from FileManager import FileManager
from Linter import Linter

def main():
    script_name = sys.argv[0]
    linter = Linter()

    for path in FileManager.parse(ArgumentParser(script_name).parse().path_pattern):
        linter.check(path)


if __name__ == "__main__":
    main()
