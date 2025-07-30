import yaml
import os

tests_folder = 'tests'

suite_types = ['simple', 'magento']


def get_config(base_path, config_file='config.yml'):
    with open(base_path + "/" + config_file, 'r') as ymlfile:
        cfg = yaml.full_load(ymlfile)

    return cfg


def is_valid(cfg):
    if cfg is None:
        return False

    return True


def get_sample_base_dir():
    return os.path.abspath(os.path.dirname(__file__) + '/../test_case/sample/')


def get_assets_dir():
    return os.path.abspath(os.path.dirname(__file__) + '/../assets/')

def get_report_template_path():
    return os.path.abspath(os.path.dirname(__file__) + '/../report/custom_template.html')
