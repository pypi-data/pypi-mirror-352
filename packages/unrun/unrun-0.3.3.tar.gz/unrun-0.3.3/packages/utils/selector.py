from InquirerPy import inquirer
from typing import Union, Optional


def select(_choices: Union[dict, list, str, None]) -> Optional[str]:
    if _choices is None or isinstance(_choices, str):
        return _choices

    choices = []
    if isinstance(_choices, list):
        for i, c in enumerate(_choices):
            if isinstance(c, list):
                choices.append({
                    "name": f"[{i}]: [[list]]",
                    "value": c
                })
            elif isinstance(c, dict):
                choices.append({
                    "name": f"[{i}]: [[dict]]",
                    "value": c
                })
            else:
                choices.append({
                    "name": f"[{i}]: {c}",
                    "value": c
                })
    elif isinstance(_choices, dict):
        for key, value in _choices.items():
            if isinstance(value, list):
                choices.append({
                    "name": f"{key}: [[list]]",
                    "value": value
                })
            elif isinstance(value, dict):
                choices.append({
                    "name": f"{key}: [[dict]]",
                    "value": value
                })
            else:
                choices.append({
                    "name": f"{key}: {value}",
                    "value": value
                })

    prompt = inquirer.select(
        message="Ambiguous choices, please select one:",
        choices=choices,
    )

    @prompt.register_kb("q")
    def _(event):
        event.app.exit(result=None)

    return select(prompt.execute())
