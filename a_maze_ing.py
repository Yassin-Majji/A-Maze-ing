import sys
import curses
from typing import Dict, Any

import parsing
import mazegen_pkg.generator as generator
import draw_maze


def main() -> None:
    """
    Main entry point of the program.

    - Parses command line arguments
    - Loads configuration file
    - Generates maze
    - Launches curses visualisation
    """
    if len(sys.argv) != 2:
        print(
            "Usage: python3 a_maze_ing.py <config_file>",
            file=sys.stderr,
        )
        sys.exit(1)

    config_file: str = sys.argv[1]

    config_data: Dict[str, Any] | None = parsing.parse_config(config_file)

    if config_data is None:
        sys.exit(1)

    maze = generator.algo(config_data)

    curses.wrapper(draw_maze.draw, maze, config_data)


if __name__ == "__main__":
    try:
        main()

    except (KeyboardInterrupt, Exception):
        sys.exit(0)