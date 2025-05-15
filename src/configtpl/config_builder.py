from copy import deepcopy
import os
import os.path
from typing import Callable
import yaml

from configtpl.utils.dicts import dict_deep_merge
from configtpl.jinja.env_factory import JinjaEnvFactory


class ConfigBuilder:
    def __init__(self, jinja_constructor_args: dict | None = None, jinja_globals: dict | None = None,
                 jinja_filters: dict | None = None, defaults: dict | None = None):
        """
        A constructor for Cofnig Builder.

        Args:
            constructor_args (dict | None): argument for Jinja environment constructor
            globals (dict | None): globals to inject into Jinja environment
            defaults (dict | None): Default values for configuration
        """
        self.jinja_env_factory = JinjaEnvFactory(constructor_args=jinja_constructor_args, globals=jinja_globals,
                                                 filters=jinja_filters)
        if defaults is None:
            defaults = {}
        self.defaults = defaults

    def set_global(self, k: str, v: Callable) -> None:
        """
        Sets a global for children Jinja environments
        """
        self.jinja_env_factory.set_global(k, v)

    def set_filter(self, k: str, v: Callable) -> None:
        """
        Sets a filter for children Jinja environments
        """
        self.jinja_env_factory.set_filter(k, v)

    def build_from_files(self, paths_colon_separated: str | list[str], overrides: dict | None = None,
                         ctx: dict | None = None) -> dict:
        """
        Renders files from provided paths.

        Args:
            ctx (dict | None): additional rendering context which is NOT injected into configuration
            overrides (dict | None): Overrides are applied at the very end stage after all templates are rendered
            paths_colon_separated (str | list[str]): Paths to configuration files.
                It might be a single item (str) or list of paths (list(str)).
                Additionally, each path might be colon-separated.
                Examples: '/opt/myapp/myconfig.cfg', '/opt/myapp/myconfig_first.cfg:/opt/myapp/myconfig_second.cfg',
                ['/opt/myapp/myconfig.cfg', '/opt/myapp/myconfig_first.cfg:/opt/myapp/myconfig_second.cfg']
        Returns:
            dict: The rendered configuration
        """
        output_cfg = deepcopy(self.defaults)
        if ctx is None:
            ctx = {}
        if overrides is None:
            overrides = {}
        # Convert the path input into list of paths
        paths_colon_separated: list[str] = [paths_colon_separated] \
            if isinstance(paths_colon_separated, str) \
            else paths_colon_separated
        paths: list[str] = []
        for path_colon_separated in paths_colon_separated:
            paths += path_colon_separated.split(":")

        for cfg_path in paths:
            cfg_path = os.path.realpath(cfg_path)
            ctx = {**output_cfg, **ctx}
            cfg_iter: dict = self._render_cfg_from_file(cfg_path, ctx)

            output_cfg = dict_deep_merge(output_cfg, cfg_iter)

        # Append overrides
        output_cfg = dict_deep_merge(output_cfg, overrides)
        return output_cfg

    def build_from_str(self, input: str, work_dir: str | None = None, defaults: dict | None = None,
                       overrides: dict | None = None) -> dict:
        """
        Renders config from string.

        Args:
            input (str): a Jinja template string which can be rendered into YAML format
            work_dir (str): a working directory.
                Include statements in Jinja template will be resolved relatively to this path
            defaults (dict | None): Default values for configuration
            overrides (dict | None): Overrides are applied at the very end stage after all templates are rendered
        Returns:
            dict: The rendered configuration
        """
        if work_dir is None:
            work_dir = os.getcwd()
        output_cfg = {} if defaults is None else deepcopy(defaults)
        if overrides is None:
            overrides = {}

        cfg = self._render_cfg_from_str(input, output_cfg, work_dir)
        output_cfg = dict_deep_merge(cfg, overrides)
        return output_cfg

    def _render_cfg_from_file(self, path: str, ctx: dict) -> dict:
        """
        Renders a template file into config dictionary in two steps:
        1. Renders a file as Jinja template
        2. Parses the rendered file as YAML template
        """
        dir = os.path.dirname(path)
        filename = os.path.basename(path)
        jinja_env = self.jinja_env_factory.get_fs_jinja_environment(dir)
        tpl = jinja_env.get_template(filename)
        tpl_rendered = tpl.render(ctx)
        return yaml.load(tpl_rendered, Loader=yaml.FullLoader)

    def _render_cfg_from_str(self, input: str, ctx: dict, work_dir: str) -> dict:
        jinja_env = self.jinja_env_factory.get_fs_jinja_environment(work_dir)
        tpl = jinja_env.from_string(input)
        tpl_rendered = tpl.render(ctx)
        return yaml.load(tpl_rendered, Loader=yaml.FullLoader)
