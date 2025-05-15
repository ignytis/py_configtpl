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
        cfg = ConfigBuilder().build_from_files("config_01.cfg:config_02.cfg",
                                               ctx={"my_context_dict": {"ctx_param": 1234}})

        self.assertDictEqual({
            "urls": {
                "base": "example.com",
                "mail": "mail.example.com",
                "news": "news.example.com",
                "mirror": "example2.com",
            },
            "server": {
                "host": "example.com",
                "port": 1234,
            },
            "modules": ["module_a", "module_b"],
            "project_name": "my_project",
            "strategies": ["second"]  # lists are replaced (config_01 is replaced with config_02)
        }, cfg)


if __name__ == "__main__":
    unittest.main()
