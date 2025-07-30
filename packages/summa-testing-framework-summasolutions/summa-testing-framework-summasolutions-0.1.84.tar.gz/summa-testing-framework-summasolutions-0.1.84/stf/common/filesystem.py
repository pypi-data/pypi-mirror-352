import os
import shutil
from .config import tests_folder


def create_test_folder():
    path = os.getcwd() + '/' + tests_folder
    try:
        os.mkdir(path)
        init_file_path = "%s/__init__.py" % path
        with open(init_file_path, 'w') as fp:
            pass

    except OSError as e:
        if e.errno == 17:  # Folder already exists
            return False
        else:
            raise Exception(e)

    return True


def copy_sample_test(name, type):
    original = os.path.dirname(__file__) + '/../test_case/sample/' + type + '.py'
    target = os.getcwd() + '/' + tests_folder + '/' + name + '.py'

    shutil.copyfile(original, target)

    return target
