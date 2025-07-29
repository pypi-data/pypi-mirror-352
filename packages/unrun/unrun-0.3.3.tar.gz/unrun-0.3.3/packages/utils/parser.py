from utils.console import error
from typing import Optional, Union
import os, yaml


def parse_command(key: Optional[str], config: Union[dict, list, str]) -> Optional[Union[dict, list, str]]:
    if key is None:
        return config

    if isinstance(config, str):
        if key is None:
            return config
        else:
            return f"{config} {key}"

    if isinstance(config, list):
        return config

    keys = key.split(".")
    results = []
    command = config
    length = len(keys)

    def fn(tar: Union[dict, list, str], i: int):
        if i == length:
            results.append(tar)
        if isinstance(tar, dict):
            for j in range(i, length):
                key = ".".join(keys[i:j + 1])
                if key in tar:
                    fn(tar[key], j + 1)
    fn(command, 0)

    if not results:
        error(f"Key '{key}' not found in the object.")
        return None

    if len(results) == 1:
        results = results[0]

    return results


def parse_filename(file: Optional[str]) -> str:
    filename = file if file else os.getenv("UNRUN_FILE")
    if not filename:
        local_f = os.path.join(os.getcwd(), "unrun.config.yaml")
        global_f = os.path.expanduser("~/unrun.config.yaml")
        if os.path.exists(local_f) and os.path.isfile(local_f):
            f = local_f
        elif os.path.exists(global_f) and os.path.isfile(global_f):
            f = global_f
        else:
            f = None
        if f is not None:
            with open(f, "r") as file:
                try:
                    config = yaml.safe_load(file)
                    filename = config.get("file", "unrun.yaml")
                except yaml.YAMLError:
                    filename = "unrun.yaml"
        else:
            filename = "unrun.yaml"
    if not filename.endswith(".yaml"):
        filename += ".yaml"
    return filename


def parse_extra(extra: list, unknown: list) -> Optional[str]:
    result = []
    if extra and unknown:
        result = extra + unknown
    elif extra:
        result = extra
    elif unknown:
        result = unknown
    if not result:
        return None
    return " ".join(result)
