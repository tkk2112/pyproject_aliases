#!/usr/bin/env python3
import argparse
import shlex
import subprocess
import sys
import tomllib
from typing import Dict, cast


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Execute aliases defined in pyproject.toml"
    )
    parser.add_argument(
        "--pyproject-toml",
        default="pyproject.toml",
        help="Path to the pyproject.toml file (default: pyproject.toml)",
    )
    parser.add_argument("alias", nargs="?", help="Alias to execute from pyproject.toml")
    parser.add_argument(
        "extra_args",
        nargs=argparse.REMAINDER,
        help="Additional arguments to pass to the alias",
    )
    return parser.parse_args()


def get_all_aliases(config_file: str) -> Dict[str, str]:
    try:
        with open(config_file, "rb") as f:
            config = tomllib.load(f)

        if "tool" in config and "aliases" in config["tool"]:
            return cast(Dict[str, str], config["tool"]["aliases"])
        return {}
    except FileNotFoundError:
        print(f"Config file not found: {config_file}", file=sys.stderr)
        sys.exit(1)  # This exits, so it doesn't return Any
    except tomllib.TOMLDecodeError as e:
        print(f"Error parsing config file: {e}", file=sys.stderr)
        sys.exit(1)  # This exits, so it doesn't return Any
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)  # This exits, so it doesn't return Any


def get_alias_from_config(config_file: str, alias_name: str) -> str:
    try:
        with open(config_file, "rb") as f:
            config = tomllib.load(f)

        if "tool" in config and "aliases" in config["tool"]:
            aliases = config["tool"]["aliases"]
            if alias_name in aliases:
                return cast(str, aliases[alias_name])
    except FileNotFoundError:
        print(f"Config file not found: {config_file}", file=sys.stderr)
        sys.exit(1)  # This exits, so it doesn't return Any
    except tomllib.TOMLDecodeError as e:
        print(f"Error parsing config file: {e}", file=sys.stderr)
        sys.exit(1)  # This exits, so it doesn't return Any
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)  # This exits, so it doesn't return Any

    print(f"alias '{alias_name}' not found in config", file=sys.stderr)
    sys.exit(1)  # This exits, so we never reach the implicit return None


def main() -> None:
    args = parse_args()

    if args.alias is None:
        aliases = get_all_aliases(args.pyproject_toml)
        if aliases:
            print("You must choose one of the available aliases:")
            for cmd_name, cmd_value in aliases.items():
                print(f"  {cmd_name} ({cmd_value})")
        else:
            print("No aliases defined in the configuration file.")
        sys.exit(1)

    alias_to_run = get_alias_from_config(args.pyproject_toml, args.alias)

    if args.extra_args:
        extra_args_str = " ".join(shlex.quote(arg) for arg in args.extra_args)
        command = f"{alias_to_run} {extra_args_str}"
    else:
        command = alias_to_run

    try:
        process = subprocess.run(
            command,
            shell=True,
            text=True,
            check=False,  # Don't raise an exception on non-zero exit
        )
        sys.exit(process.returncode)
    except Exception as e:
        print(f"Error executing alias: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
