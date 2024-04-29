import glob
import os

class FileManager:
    @staticmethod
    def parse(path_pattern):
        list_paths = glob.glob(path_pattern, recursive=True)

        if not list_paths:
            print("указан пустой список файлов")

        for path in list_paths:
            if os.path.isdir(path):
                print(f"{path} не является файлом")
            elif not path.endswith(".pas"):
                print(f"{os.path.basename(path)} не является файлом pascal")
            else:
                yield path

    @staticmethod
    def load(path):
        with open(path, 'r') as file:
            document = file.read()

        return document

    @staticmethod
    def save(path, document):
        with open(path, "w") as file:
            for line in document:
                file.write(line + '\n')
