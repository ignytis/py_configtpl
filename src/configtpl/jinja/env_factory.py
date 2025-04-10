import jinja2

from configtpl.jinja import filters as jinja_filters
from configtpl.jinja import globals as jinja_globals
from configtpl.utils.dicts import dict_deep_merge


class JinjaEnvFactory:
    def __init__(self, constructor_args: dict | None = None, globals: dict | None = None, filters: dict | None = None):
        """
        A constructor for Jinja Envoronment Factory

        Args:
            constructor_args (dict | None): argument for Jinja environment constructor
            globals (dict | None): globals to inject into Jinja environment
        """
        self._constructor_args = dict_deep_merge(
            {
                "undefined": jinja2.StrictUndefined,
            },
            {} if constructor_args is None else constructor_args,
        )
        self._globals = dict_deep_merge(
            {
                "cmd": jinja_globals.jinja_global_cmd,
                "env": jinja_globals.jinja_global_env,
            },
            {} if globals is None else globals,
        )
        self._filters = dict_deep_merge(
            {
                "split_space": jinja_filters.jinja_filter_split_space,
            },
            {} if globals is None else globals,
        )

        self._fs_loader_cache = {}

    def get_fs_jinja_environment(self, dir: str) -> jinja2.Environment:
        """
        Creates an instance of Jinja environment with filesystem loaded for provided directory
        """
        if dir in self._fs_loader_cache:
            return self._fs_loader_cache[dir]

        jinja_env = jinja2.Environment(**self._constructor_args, loader=jinja2.FileSystemLoader(dir))
        jinja_env.globals.update(self._globals)
        jinja_env.filters.update(self._filters)

        self._fs_loader_cache[dir] = jinja_env

        return jinja_env
