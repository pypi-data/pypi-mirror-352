"""General utility for reading/parsing config files"""

import os
import platform
import shutil

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar, Optional

from platformdirs import user_config_dir

from jbutils.types import T, Predicate, Patterns
from jbutils.utils import utils


sample_files_1 = {
    "common/tools/test.json": {"a": 5, "b": "b", "c": {"c1": 1, "c2": False}},
    "common/tools/test.yaml": {"a": 10, "b": "B", "c": [{"c1": 2, "c2": True}]},
    "init.yaml": {"a": 15, "b": "test", "c": {"c1": 3, "c2": "true"}},
}

sample_files_2 = {
    "common": {
        "tools": {
            "test.json": {"a": 5, "b": "b", "c": {"c1": 1, "c2": False}},
            "test.yaml": {"a": 10, "b": "B", "c": [{"c1": 2, "c2": True}]},
        }
    },
    "init.yaml": {"a": 15, "b": "test", "c": {"c1": 3, "c2": "true"}},
}

CFG_EXTS = [
    ".cfg",
    ".ini",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
]


def get_dirs_files(path: str) -> tuple[list[str], list[str]]:
    """Get the directories and files from sub_path separated into two lists

    Args:
        path (str): Path to check

    Returns:
        tuple[list[str], list[str]]: Two lists containing the directories
            and config files at the provided location (dirs, files)
    """

    dirs = utils.list_paths(path, os.path.isdir)
    files = utils.list_paths(path, lambda fname: utils.get_ext(fname) in CFG_EXTS)
    return dirs, files


def get_default_cfg_files(path: str, cfgs: Optional[dict] = None) -> dict:
    cfgs = cfgs or {}

    dirs, files = get_dirs_files(path)
    for fname in files:
        cfgs[fname] = utils.read_file(os.path.join(path, fname))

    for dname in dirs:
        sub_cfgs = get_default_cfg_files(os.path.join(path, dname))
        if sub_cfgs:
            cfgs[dname] = sub_cfgs

    return cfgs


@dataclass
class Configurator:
    app_name: str = ""
    cfg_dir: str = ""
    author: str = ""
    version: str = ""

    platform: str = platform.platform()

    files: list[str] | dict[str, str] = field(default_factory=list)

    ignored_paths: Patterns = field(default_factory=list)
    """Paths ignored during normal reset of config data (e.g., directories for saved files etc..)"""

    # Flags
    roaming: bool = False
    ensure_exists: bool = True
    use_default_path: bool = True
    trim_key_exts: bool = True
    reset_cfgs: bool = False
    reset_ignored: bool = False
    create_cfg_dir: bool = True
    """ Create the cfg directory if it doesn't exist """

    use_glob_ignore: bool = True
    """Use Glob syntax for ignore patterns"""

    _sep: str = "/"
    _data: dict = field(default_factory=dict)
    _path_map: dict[tuple[str, ...], str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.initialize()

    def initialize(self) -> None:
        self.cfg_dir = self.cfg_dir or self._get_cfg_dir()
        if self.reset_cfgs:
            self.clear_cfgs(self.reset_ignored)
            self._get_cfg_dir()

        if self.platform == "Windows":
            self._sep = "\\"

        if not os.path.exists(self.cfg_dir):
            # TODO: improve logging
            if not self.create_cfg_dir:
                print(f"[WARNING]: '{self.cfg_dir}' does not exist")
                return

            print(f"Path: '{self.cfg_dir}' doesn't exist, attempting to create")
            os.makedirs(self.cfg_dir, exist_ok=True)

        if isinstance(self.files, list):
            for file_name in self.files:
                fpath = os.path.join(self.cfg_dir, file_name)
                self._set_file_data(fpath, {})

        elif isinstance(self.files, dict):
            for key, value in self.files.items():
                self._get_files_dict(key, value)

    def reset(self, reset_ignored: bool = False) -> None:
        self.clear_cfgs(reset_ignored)
        self.initialize()

    def get(self, key: list[str] | str, default: Any = None) -> Any:
        if isinstance(key, str) and not self.trim_key_exts:
            key = key.split(".")
            if len(key) >= 2:
                ext = key.pop()
                fname = key.pop()
                key.append(f"{fname}{ext}")
        return utils.get_nested(self._data, key, default_val=default)

    def set(self, key: str | list[str], value: Any) -> None:
        utils.set_nested(self._data, key, value)

        key_path = self.get_path_from_key(key)
        if key_path:
            filepath = self._path_map[tuple(key_path)]
            data = self.get(key_path)
            utils.write_file(filepath, data)

    def get_path_from_key(self, key: str | list[str]) -> list[str]:
        path = key.split(".") if isinstance(key, str) else key
        while path:
            if tuple(path) in self._path_map:
                return path
            path.pop()
        return []

    def get_as_class(
        self, cls: type[T], path: str | list[str], default: Any = None
    ) -> T:
        default = default or {}
        data = self.get(path, default)
        return cls(**data)

    def clear_cfgs(self, reset_ignored: bool | None = None) -> None:
        self._data = {}
        self._path_map = {}

        ignored = None if reset_ignored else self.ignored_paths

        if os.path.exists(self.cfg_dir):
            utils.rm_dirs(
                self.cfg_dir, ignored=ignored, use_glob=self.use_glob_ignore
            )

    def _set_file_data(self, path: str, default: Optional[dict] = None) -> None:
        default = default or {}
        # root_path = os.path.join(root_path, filename)

        if not os.path.exists(path) and self.ensure_exists:
            utils.write_file(path, default)
            data = default
        else:
            data = utils.read_file(path, default_val=default)

        root = os.path.commonpath([path, self.cfg_dir])

        data_path = utils.split_path(
            path.replace(root, ""), keep_ext=not self.trim_key_exts
        )
        self._path_map[tuple(data_path)] = path
        utils.set_nested(self._data, data_path, data)

    def _get_files_dict(
        self, prop_key: str, prop: Any, path: Optional[list[str]] = None
    ):
        path = path + [prop_key] if path else [prop_key]
        path_str = os.path.join(self.cfg_dir, self._sep.join(path))

        if not utils.get_ext(prop_key):
            os.makedirs(path_str, exist_ok=True)
            if isinstance(prop, dict):
                for key, value in prop.items():
                    self._get_files_dict(key, value, path)
            elif isinstance(prop, list):
                for item in prop:
                    self._set_file_data(path_str, item)
        else:
            self._set_file_data(path_str, prop)

    def _get_cfg_dir(self) -> str:
        return user_config_dir(
            self.app_name,
            self.author,
            self.version,
            self.roaming,
            self.ensure_exists,
        )
