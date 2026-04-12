"""Configuration file parser for the maze generator."""

from typing import Dict, Optional, Tuple, Any
import sys


def parse_config(filename: str) -> Optional[Dict[str, Any]]:
    """
    Parse a configuration file for the maze generator.

    Args:
        filename: Path to the config file.

    Returns:
        Parsed configuration dictionary or None if error occurs.
    """
    required_keys = {
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
    }

    optional_keys = {"SEED", "ALGORITHM"}

    config: Dict[str, Any] = {}

    try:
        with open(filename, "r") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    raise ValueError(f"[Line {line_number}] Missing '=' sign")

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                if key not in required_keys and key not in optional_keys:
                    raise ValueError(
                        f"[Line {line_number}] Unknown key: '{key}'"
                    )

                if key in config:
                    raise ValueError(
                        f"[Line {line_number}] Duplicate key: '{key}'"
                    )

                # ---------- WIDTH / HEIGHT ----------
                if key in ("WIDTH", "HEIGHT"):
                    try:
                        value = int(value)
                    except ValueError:
                        raise ValueError(
                            f"[Line {line_number}] {key} must be an integer"
                        )
                    if value <= 0:
                        raise ValueError(
                            f"[Line {line_number}] {key} must be > 0"
                        )

                # ---------- ENTRY / EXIT ----------
                elif key in ("ENTRY", "EXIT"):
                    parts = value.split(",")
                    if len(parts) != 2:
                        raise ValueError(
                            f"[Line {line_number}] {key} must be x,y format"
                        )
                    try:
                        x = int(parts[0].strip())
                        y = int(parts[1].strip())
                    except ValueError:
                        raise ValueError(
                            f"[Line {line_number}] {key} must contain integers"
                        )
                    value = (x, y)

                # ---------- PERFECT ----------
                elif key == "PERFECT":
                    val = value.lower()
                    if val == "true":
                        value = True
                    elif val == "false":
                        value = False
                    else:
                        raise ValueError(
                            f"[Line {line_number}] PERFECT must be True or False"
                        )

                # ---------- SEED ----------
                elif key == "SEED":
                    try:
                        value = int(value)
                    except ValueError:
                        raise ValueError(
                            f"[Line {line_number}] SEED must be an integer"
                        )

                # ---------- OUTPUT FILE ----------
                elif key == "OUTPUT_FILE":
                    if not value:
                        raise ValueError(
                            f"[Line {line_number}] OUTPUT_FILE cannot be empty"
                        )

                config[key] = value

        # ---------- REQUIRED KEYS CHECK ----------
        missing = required_keys - config.keys()
        if missing:
            raise ValueError(
                f"Missing required keys: {', '.join(missing)}"
            )

        # ---------- FINAL VALIDATION ----------
        width = int(config["WIDTH"])
        height = int(config["HEIGHT"])

        ex, ey = config["ENTRY"]
        tx, ty = config["EXIT"]

        if not (0 <= ex < width and 0 <= ey < height):
            raise ValueError("ENTRY is out of maze bounds")

        if not (0 <= tx < width and 0 <= ty < height):
            raise ValueError("EXIT is out of maze bounds")

        if (ex, ey) == (tx, ty):
            raise ValueError("ENTRY and EXIT cannot be the same cell")

        return config

    except FileNotFoundError:
        print(
            f"[CONFIG ERROR] File not found: '{filename}'. "
            "Check if the file path is correct.",
            file=sys.stderr,
        )

    except PermissionError:
        print(
            f"[CONFIG ERROR] Permission denied: '{filename}'. "
            "You don't have permission to read this file.",
            file=sys.stderr,
        )

    except ValueError as error:
        print(
            f"[CONFIG ERROR] Invalid configuration:\n→ {error}\n"
            "Please fix the config file and try again.",
            file=sys.stderr,
        )

    return None