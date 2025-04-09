from copy import deepcopy
import os.path
import yaml

from configtpl.utils.dicts import dict_deep_merge
from configtpl.jinja.env_factory import JinjaEnvFactory


class ConfigBuilder:
    def __init__(self, jinja_constructor_args: dict | None = None, jinja_globals: dict | None = None,
                 jinja_filters: dict | None = None):
        self.jinja_env_factory = JinjaEnvFactory(constructor_args=jinja_constructor_args, globals=jinja_globals,
                                                 filters=jinja_filters)

    def build_from_files(self, paths_colon_separated: str | list[str], defaults: dict | None = None,
                         overrides: dict | None = None, directives_key: str | None = "@configtpl") -> dict:
        """
        Renders files from provided paths.

        Args:
            paths_colon_separated (str | list[str]): Paths to configuration files.
                It might be a single item (str) or list of paths (list(str)).
                Additionally, each path might be colon-separated.
                Examples: '/opt/myapp/myconfig.cfg', '/opt/myapp/myconfig_first.cfg:/opt/myapp/myconfig_second.cfg',
                ['/opt/myapp/myconfig.cfg', '/opt/myapp/myconfig_first.cfg:/opt/myapp/myconfig_second.cfg']
            defaults (dict | None): Default values for configuration
            overrides (dict | None): Overrides are applied at the very end stage after all templates are rendered
            directives_key (str | None): parameter key for library directives. If None, no directives will be processed
        Returns:
            dict: The rendered configuration
        """
        output_cfg = {} if defaults is None else deepcopy(defaults)
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
            cfg_iter: dict = self._render_jinja_yaml_config(cfg_path, output_cfg)
            loaded_configs.append(cfg_path)

            # Apply the config lib directives
            directives: dict | None = cfg_iter.get(directives_key)
            if directives is not None:
                # Inject the next templates to load. Consider path to current config
                new_paths = [os.path.realpath(os.path.join(cfg_dir, p))
                             for p in directives.get("load_next", [])]
                paths += new_paths
                del cfg_iter[directives_key]

            output_cfg = dict_deep_merge(output_cfg, cfg_iter)

        # Append overrides
        output_cfg = dict_deep_merge(output_cfg, overrides)

        return output_cfg

    def _render_jinja_yaml_config(self, path: str, ctx: dict) -> dict:
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
