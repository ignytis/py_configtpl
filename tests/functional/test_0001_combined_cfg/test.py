import unittest

from configtpl.config_builder import ConfigBuilder


class TestCombinedCfg(unittest.TestCase):
    """
    Tests the configuration which is combined from multiple files
    """
    def setUp(self):
        self.maxDiff = None
        return super().setUp()

    def test_combined_cfg(self):
        cfg = ConfigBuilder().build_from_files("config_01.cfg:config_02.cfg")

        self.assertDictEqual({
            "urls": {
                "base": "example.com",
                "mail": "mail.example.com",
                "mirror": "example2.com",
                "sub_domain": "my_project.example.com",  # resolved as directive in config_01 using value from config_02
            },
            "server": {
                "host": "example.com",
                "port": 1234,
            },
            "modules": ["module_a", "module_b"],
            "project_name": "my_project",
            "strategies": ["second"]  # lists are replaced (config_01 is replaced with config_02)
        }, cfg)

    def test_recursion_exception(self):
        with self.assertRaisesRegex(Exception, "Attempt to load '.+' config multiple times\\. "
                                    "An exception is thrown to prevent from infinite recursion"):
            ConfigBuilder().build_from_files("config_wrong_01_recursion_1.cfg:config_wrong_01_recursion_2.cfg")


if __name__ == "__main__":
    unittest.main()
