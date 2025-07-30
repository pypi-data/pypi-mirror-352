from lt_utils.common import *
from lt_utils.file_ops import load_json, save_json, FileScan
from lt_utils.misc_utils import log_traceback, get_current_time
from lt_utils.type_utils import is_pathlike, is_file, is_dir, is_dict, is_str
from lt_tensor.misc_utils import updateDict


class ModelConfig(ABC, OrderedDict):
    _default_settings: Dict[str, Any] = {}
    _forbidden_list: List[str] = [
        "_settings",
    ]

    def __init__(
        self,
        settings: Dict[str, Any] = None,
        path_name: Optional[Union[str, PathLike]] = None,
    ):
        assert is_dict(settings)
        self._default_settings = settings
        if path_name is not None and is_pathlike(path_name):
            if not str(path_name).endswith(".json"):
                self.path_name = str(Path(path_name, "config.json")).replace("\\", "/")
            else:
                self.path_name = str(path_name).replace("\\", "/")
        else:
            self.path_name = "config.json"
        self.reset_settings()

    def _setup_path_name(self, path_name: Union[str, PathLike]):
        if is_file(path_name):
            self.from_path(path_name)
            self.path_name = str(path_name).replace("\\", "/")
        elif is_str(path_name):
            self.path_name = str(path_name).replace("\\", "/")
            if not self.path_name.endswith((".json")):
                self.path_name += ".json"

    def reset_settings(self):
        for s_name, setting in self._default_settings.items():
            if s_name in self._forbidden_list:
                continue
            updateDict(self, {s_name: setting})

    def save_config(
        self,
        path_name: Union[PathLike, str],
    ):
        assert is_pathlike(
            path_name, True
        ), f"path_name should be a non-empty string or pathlike object! received instead: {path_name}"
        self._setup_path_name(path_name)
        base = {k: y for k, y in self.__dict__.items() if k not in self._forbidden_list}
        save_json(self.path_name, base, indent=2)

    def to_dict(self):
        return {k: y for k, y in self.__dict__.items() if k not in self._forbidden_list}

    def set_value(self, var_name: str, value: str) -> None:
        updateDict(self, {var_name: value})

    def get_value(self, var_name: str) -> Any:
        return self.__dict__.get(var_name)

    @classmethod
    def from_dict(
        cls, dictionary: Dict[str, Any], path: Optional[Union[str, PathLike]] = None
    ) -> "ModelConfig":
        assert is_dict(dictionary)
        return ModelConfig(dictionary, path)

    @classmethod
    def from_path(cls, path_name: PathLike) -> "ModelConfig":
        assert is_file(path_name) or is_dir(path_name)
        settings = {}

        if is_file(path_name):
            settings.update(load_json(path_name, {}, errors="ignore"))
        else:
            files = FileScan.files(
                path_name,
                [
                    "*_config.json",
                    "config_*.json",
                    "*_config.json",
                    "cfg_*.json",
                    "*_cfg.json",
                    "cfg.json",
                    "config.json",
                    "settings.json",
                    "settings_*.json",
                    "*_settings.json",
                ],
            )
            assert files, "No config file found in the provided directory!"
            settings.update(load_json(files[-1], {}, errors="ignore"))
        return ModelConfig(settings, path_name)
