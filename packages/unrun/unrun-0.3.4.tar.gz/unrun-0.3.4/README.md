# UnRun

[![PyPI downloads per month](https://img.shields.io/pypi/dm/unrun.svg?color=BD976A)](https://pypi.org/project/unrun/)
[![PyPI version](https://img.shields.io/pypi/v/unrun.svg?color=blue)](https://pypi.org/project/unrun/)
[![GitHub last commit](https://img.shields.io/github/last-commit/howcasperwhat/unrun.svg?color=red)](https://github.com/howcasperwhat/unrun/commits/main)
[![GitHub issues](https://img.shields.io/github/issues/howcasperwhat/unrun.svg?color=63ba83)](https://github.com/howcasperwhat/unrun/issues)

🚀 A simple CLI tool to run commands from a YAML file.

## Installation

```bash
pip install unrun
```

## Usage & Features

Create an `unrun.yaml` file in your project root:

```yaml
hello: echo "Hello, world!"
foo:
    bar: echo "This is foo bar"
baz: !and
    - echo "This is baz item 1"
    - echo "This is baz item 2"
```

### Single Command

You can run a single command by specifying its key:

```bash
unrun hello
```

Run the command:

```bash
echo "Hello, world!"
```

### Nested Command
You can run nested commands by specifying the full path:

```bash
unrun foo.bar
```

Run the command:

```bash
echo "This is foo bar"
```

### List Command
To run all commands under a key that contains a list, you can simply specify the key:

```bash
unrun baz
```

Run the commands:

```bash
echo "This is baz item 1" && echo "This is baz item 2"
```

Supports `!and`, `!or` and `!;` YAML tags to combine commands.

### Configuration

#### Configure Priority
1. CLI arguments
2. Environment variables: `UNRUN_{key}`
3. local `unrun.config.yaml`
4. global `~/unrun.config.yaml`

#### Available keys
- `--file`: Specify a custom YAML file (default is `unrun.yaml`).
- `--include`: Include specified keys from the YAML file.
- `--exclude`: Exclude specified keys from the YAML file.

## License

[MIT License](https://github.com/howcasperwhat/unrun/blob/main/LICENSE)