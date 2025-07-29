from utils.parser import parse_settings

config = {}

default_config = {
    "file": {
        "safety": "unrun.yaml",
        "after": lambda x: x if x.endswith(".yaml") else f"{x}.yaml",
    },
    "include": {
        "safety": ["*"],
        "after": None,
    },
    "exclude": {
        "safety": [],
        "after": None,
    }
}


def setup_config(args):
    for key, value in default_config.items():
        config[key] = parse_settings(
            key=key,
            default=getattr(args, key, None),
            safety=value["safety"],
            after=value["after"],
        )
    return config
