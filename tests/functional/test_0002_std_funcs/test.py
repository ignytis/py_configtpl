import unittest

from configtpl.config_builder import ConfigBuilder


class TestStdFunccs(unittest.TestCase):
    """
    Tests standard Jinja functions.
    "Standard" means "standard for this library" or "default" functions
    """
    def setUp(self):
        self.maxDiff = None
        return super().setUp()

    def test_std_funcs(self):
        cfg = ConfigBuilder().build_from_files("config.cfg")

        self.assertDictEqual({
            # "greetings" is based on output of a system command splitted by line break
            # TODO: does it works on Windows! Perhaps another test is needed. As an option - OS check
            "greetings": [
                "Hello, First!",
                "Hello, Second!",
                "Hello, Third!",
            ],
            "server": {
                "host": "example.com",
                "port": 1234,
            },
            "urls": {
                "base": "example.com",
                "subdomain": "sample_value.example.com",
            },
        }, cfg)


if __name__ == "__main__":
    unittest.main()
