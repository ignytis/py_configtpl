from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch, mock_open

from configtpl.config_builder import ConfigBuilder

FILE_CONFIG_CONTENTS_SIMPLE = """\
{% set name = "John" %}
params:
  user_name: {{ name }}
  greeting: "Hello, {{ name }}!"
"""

FILE_CONFIG_CONTENTS_COMPOSITE_FIRST = """\
{% set name = "John" %}
params:
  user_name: {{ name }}
  greeting: "Hello, {{ name }}!"

"@configtpl":
  load_next:
  - another_config.cfg
"""

FILE_CONFIG_CONTENTS_COMPOSITE_SECOND = """\
some_paths:
- /home/{{ params.user_name | lower }}
"""

CONFIG_COMPILED_SIMPLE = {
    "params": {
        "user_name": "John",
        "greeting": "Hello, John!",
    },
}


@patch("pathlib.Path.cwd", return_value="/test/cwd")
@patch("pathlib.Path.home", return_value="/test/home")
@patch("os.path.isfile", return_value=True)
@patch("os.path.getmtime", return_value=123)
class CompilerTest(TestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.maxDiff = None

    @patch("builtins.open", new_callable=mock_open, read_data=FILE_CONFIG_CONTENTS_SIMPLE)
    def test_compile_simple(self, _a, _b, _c, _d, _e) -> None:
        self.assertDictEqual(CONFIG_COMPILED_SIMPLE, get_instance().build_from_files("/test/sample.cfg"))

    @patch("builtins.open", new_callable=mock_open, read_data=FILE_CONFIG_CONTENTS_SIMPLE)
    def test_compile_simple_override(self, _a, _b, _c, _d, _e) -> None:
        cfg_compiled = deepcopy(CONFIG_COMPILED_SIMPLE)
        cfg_compiled["params"] = {
            **cfg_compiled["params"],
            "some_param": "some_param_val1",
            "greeting": "Overridden greeting",
        }
        self.assertDictEqual(cfg_compiled,
                             get_instance().build_from_files(
                                 "/test/sample.cfg",
                                 overrides={
                                     "params": {
                                         "some_param": "some_param_val1",
                                         "greeting": "Overridden greeting",
                                      }
                                 }))

    @patch("builtins.open", new_callable=mock_open, read_data=FILE_CONFIG_CONTENTS_COMPOSITE_FIRST)
    def test_compile_composite(self, mock_file, _b, _c, _d, _e) -> None:
        handlers = (mock_file.return_value, mock_open(read_data=FILE_CONFIG_CONTENTS_COMPOSITE_SECOND).return_value)
        mock_file.side_effect = handlers

        self.assertDictEqual({
            "params": {
                "user_name": "John",
                "greeting": "Hello, John!",
            },
            "some_paths": ["/home/john"],
        }, get_instance().build_from_files("/test/sample.cfg"))


def get_instance() -> ConfigBuilder:
    return ConfigBuilder()
