import unittest

from configtpl.config_builder import ConfigBuilder


CFG = """\
{% set domain = "example.com" %}
domain: {{ domain }}
subdomain: mysite.{{ domain }}

"""


class TestRenderStr(unittest.TestCase):
    """
    Tests rendering config from string
    """
    def setUp(self):
        self.maxDiff = None
        return super().setUp()

    def test_custom_funcs(self):
        builder = ConfigBuilder()
        cfg = builder.build_from_str(CFG)
        self.assertDictEqual({
            "domain": "example.com",
            "subdomain": "mysite.example.com",
        }, cfg)


if __name__ == "__main__":
    unittest.main()
