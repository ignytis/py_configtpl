from copy import deepcopy
import os
import os.path
from typing import Callable
import yaml

from configtpl.utils.dicts import dict_deep_merge
from configtpl.jinja.env_factory import JinjaEnvFactory

DEFAULT_DIRECTIVE_KEY = "@configtpl"


class ConfigBuilder:
    def __init__(self, jinja_constructor_args: dict | None = None, jinja_globals: dict | None = None,
                 jinja_filters: dict | None = None, defaults: dict | None = None,
                 directives_key: str | None = DEFAULT_DIRECTIVE_KEY):
        """
        A constructor for Cofnig Builder.

        Args:
            constructor_args (dict | None): argument for Jinja environment constructor
            globals (dict | None): globals to inject into Jinja environment
            defaults (dict | None): Default values for configuration
            directives_key (str | None): parameter key for library directives. If None, no directives will be processed
        """
        self.jinja_env_factory = JinjaEnvFactory(constructor_args=jinja_constructor_args, globals=jinja_globals,
                                                 filters=jinja_filters)
        if defaults is None:
            defaults = {}
        self.defaults = defaults
        self.directives_key = directives_key

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

        loaded_configs = []
        while len(paths) > 0:
            cfg_path = os.path.realpath(paths.pop(0))
            cfg_dir = os.path.dirname(cfg_path)
            if cfg_path in loaded_configs:
                raise Exception(f"Attempt to load '{cfg_path}' config multiple times. An exception is thrown "
                                "to prevent from infinite recursion")
            ctx = {**output_cfg, **ctx}
            cfg_iter: dict = self._render_cfg_from_file(cfg_path, ctx)
            loaded_configs.append(cfg_path)
            self._apply_directives(cfg_iter, cfg_dir, paths)

            output_cfg = dict_deep_merge(output_cfg, cfg_iter)

        # Append overrides
        output_cfg = dict_deep_merge(output_cfg, overrides)
        return output_cfg

    def build_from_str(self, input: str, work_dir: str | None = None, defaults: dict | None = None,
                       overrides: dict | None = None) -> dict:
        """
        Renders config from string.
        NB! This function does NOT resolve the directives currently

        Args:
            input (str): a Jinja template string which can be rendered into YAML format
            work_dir (str): a working directory.
                Include statements in Jinja template will be resolved relatively to this path
            defaults (dict | None): Default values for configuration
            overrides (dict | None): Overrides are applied at the very end stage after all templates are rendered
        Returns:
            dict: The rendered configuration
        """
        # TODO: load it the same way as build_from_files - use files stack, apply directives, etc
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

    def _apply_directives(self, config: dict, cfg_dir: str, paths: list[str]) -> None:
        """
        Applies configuration directives
        """
        directives: dict | None = config.get(self.directives_key)
        if directives is None:
            return

        # Inject the next templates to load. Consider path to current config
        # TODO: an opposite directive. load_before? base? It might call this function recursively
        for p in directives.get("load_next_defer", []):
            real_path = os.path.realpath(os.path.join(cfg_dir, p))
            paths.append(real_path)

        del config[self.directives_key]
