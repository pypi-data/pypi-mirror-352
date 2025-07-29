import yaml
from utils.config import config
from utils.console import error
from typing import Union, Optional
from fnmatch import fnmatch


def join_constructor(
    loader: yaml.Loader,
    node: yaml.nodes.SequenceNode,
    sym: str,
) -> str:
    return sym.join(loader.construct_sequence(node))


def add_constructors() -> None:
    yaml.add_constructor(
        '!and',
        lambda loader, node: join_constructor(loader, node, ' && '),
        Loader=yaml.SafeLoader
    )
    yaml.add_constructor(
        '!or',
        lambda loader, node: join_constructor(loader, node, ' || '),
        Loader=yaml.SafeLoader
    )
    yaml.add_constructor(
        '!;',
        lambda loader, node: join_constructor(loader, node, ' ; '),
        Loader=yaml.SafeLoader
    )
    yaml.add_constructor(
        '!join',
        lambda loader, node: join_constructor(loader, node, ' '),
        Loader=yaml.SafeLoader
    )
    yaml.add_multi_constructor(
        '!:',
        lambda loader, tag_suffix, node: join_constructor(loader, node, tag_suffix),
        Loader=yaml.SafeLoader
    )


def norm_scripts(scripts) -> Union[dict, list, str]:
    if isinstance(scripts, list):
        return [norm_scripts(item) for item in scripts]
    elif isinstance(scripts, dict):
        return {key: norm_scripts(value) for key, value in scripts.items()}
    return str(scripts)


def match(key: str) -> bool:
    if not any(fnmatch(key, pat) for pat in config["include"]):
        return False
    if any(fnmatch(key, pat) for pat in config["exclude"]):
        return False
    return True


def filter_scripts(scripts) -> Union[dict, list, str]:
    if isinstance(scripts, dict):
        return {key: filter_scripts(value) for key, value in scripts.items() if match(key)}
    return scripts


def load_scripts(file: str) -> Optional[Union[dict, list, str]]:
    add_constructors()
    try:
        with open(file, "r") as f:
            config = yaml.safe_load(f)
        if config is None:
            config = {}
        return filter_scripts(norm_scripts(config))
    except FileNotFoundError:
        error(f"`{file}` not found in the current directory.")
        config = None
    except yaml.YAMLError as e:
        error(f"Error parsing `{file}`:\n{e}")
        config = None
    return config
