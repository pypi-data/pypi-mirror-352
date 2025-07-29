import yaml
from utils.console import error
from typing import Union, Optional


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


def norm_config(config) -> Union[dict, list, str]:
    if isinstance(config, list):
        return [norm_config(item) for item in config]
    elif isinstance(config, dict):
        return {key: norm_config(value) for key, value in config.items()}
    return str(config)


def load_config(file: str) -> Optional[Union[dict, list, str]]:
    add_constructors()
    try:
        with open(file, "r") as f:
            config = yaml.safe_load(f)
        if config is None:
            config = {}
        return norm_config(config)
    except FileNotFoundError:
        error(f"`{file}` not found in the current directory.")
        config = None
    except yaml.YAMLError as e:
        error(f"Error parsing `{file}`:\n{e}")
        config = None
    return config
