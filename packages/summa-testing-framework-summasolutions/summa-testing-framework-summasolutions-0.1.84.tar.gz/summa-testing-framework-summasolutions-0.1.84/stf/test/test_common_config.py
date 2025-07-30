import stf.common.config as common_config
import unittest
import os


class TestCommonConfigGetConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current_dir = os.path.dirname(os.path.realpath(__file__)) + '/fixtures'

    def test_non_existent_file(self):
        config_file = 'non_existent_file.yml'
        with self.assertRaises(FileNotFoundError):
            common_config.get_config(self.current_dir, config_file)

    def test_empty_file(self):
        config_file = 'empty_config_file.yml'
        config = common_config.get_config(self.current_dir, config_file)
        self.assertIsNone(config)

    def test_basic_file(self):
        config_file = 'basic_config_file.yml'
        actual = common_config.get_config(self.current_dir, config_file)
        expected = {
            'dev': {
                'url': 'https://example.com/'
            }
        }
        self.assertEqual(expected, actual)


class TestCommonConfigIsValid(unittest.TestCase):
    def test_empty_config(self):
        config = None
        actual = common_config.is_valid(config)
        self.assertFalse(actual)

    def test_only_one_empty_environment(self):
        config = {
            'dev': None
        }
        actual = common_config.is_valid(config)
        self.assertFalse(actual)


class TestCommonConfigGetSampleBaseDir(unittest.TestCase):
    def test_get_base_dir(self):
        expected = os.path.abspath(os.path.dirname(__file__) + '/../test_case/sample/')
        actual = common_config.get_sample_base_dir()
        self.assertEqual(expected, actual)