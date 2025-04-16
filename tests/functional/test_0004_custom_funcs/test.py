import unittest

from configtpl.config_builder import ConfigBuilder


def str_rev(input: str) -> str:
    return "".join(list(reversed(input)))


def gen_seq(min: int, max: int) -> list:
    return list(range(min, max)) + [max]


class TestCustomFuncs(unittest.TestCase):
    """
    Tests the custom function in Jinja environment
    """
    def setUp(self):
        self.maxDiff = None
        return super().setUp()

    def test_custom_funcs(self):
        builder = ConfigBuilder()
        builder.set_filter("str_rev", str_rev)
        builder.set_global("gen_seq", gen_seq)
        cfg = builder.build_from_files("config.cfg")

        self.assertDictEqual({
            "simple_value": "abc",
            "custom_filter": "olleh",
            "custom_function": [3, 4, 5, 6, 7, 8, 9],
        }, cfg)


if __name__ == "__main__":
    unittest.main()
