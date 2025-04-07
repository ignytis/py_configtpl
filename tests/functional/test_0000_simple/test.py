import unittest

from configtpl.config_builder import ConfigBuilder


class TestSimple(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        return super().setUp()

    def test_simple(self):
        cfg = ConfigBuilder().build_from_files("config.cfg")

        self.assertDictEqual({
            "urls": {
                "base": "example.com",
                "mail": "mail.example.com",
            },
            "server": {
                "host": "example.com",
                "port": 1234,
            }
        }, cfg)


if __name__ == "__main__":
    unittest.main()
