# configtpl

This library builds configuration in two stages:

1. Renders the provided configuration as Jinja templates
1. Parses the rendered data as YAML file

# Features

- Uses Jinja2 and Yaml capabilities to build a dynamic configuration
- Multiple configuration files might be passed. The library merges all of them into single config.
- Basic confuration includes Jinja functions and filters for general-purpose tasks:
  - Reading the environment variables
  - Execution of system commands
  - Hashing

# Examples

You can check the [functional tests folder](tests/functional) for more examples.

A very simple example of usage is provided below:

```yaml
# my_first_config.cfg

{% set my_val = "abc" %}
app:
  param_env: "{{ env('MY_ENV_VAR', 'default') }}"
  param1: "{{ my_val }}"
```

```yaml
# my_second_config.cfg

app:
  param2: def
  param3: "{{ app.param1 }}123"
hash: "{{ app.param1 | md5 }}"
```


```python
# app.py

import json
from configtpl.config_builder import ConfigBuilder

builder = ConfigBuilder()
cfg = builder.build_from_files("my_first_config.cfg:my_second_config.cfg")
print(json.dumps(cfg, indent=2))

```

```bash
# Execution

MY_ENV_VAR=testing python ./app.py

# output
{
  "app": {
    "param_env": "testing",
    "param1": "abc",
    "param2": "def",
    "param3": "abc123"
  },
  "hash": "900150983cd24fb0d6963f7d28e17f72"
}
```
