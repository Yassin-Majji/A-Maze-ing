import curses
from typing import List, Tuple, Dict, Any
import mazegen_pkg.generator as generator


def draw_cell(
    screen: curses.window,
    start_x: int,
    start_y: int,
    width: int,
    height: int,
    cell: int,
    attr: int = 0
) -> None:
    """
    Draw a single maze cell using curses characters.

    Args:
        screen: curses window object.
        start_x: X position of the cell.
        start_y: Y position of the cell.
        width: Cell width in characters.
        height: Cell height in characters.
        cell: Bitmask representing walls (N, E, S, W).
        attr: curses attribute (color, style).
    """
    top = cell >> 0 & 1
    right = cell >> 1 & 1
    bottom = cell >> 2 & 1
    left = cell >> 3 & 1

    for y in range(start_y, start_y + height):
        for x in range(start_x, start_x + width):
            if y == start_y and x == start_x and top and left:
                screen.addch(y, x, '┌', attr)
            elif y == start_y and x == start_x + width - 1 and top and right:
                screen.addch(y, x, '┐', attr)
            elif y == start_y + height - 1 and x == start_x and bottom and left:
                screen.addch(y, x, '└', attr)
            elif y == start_y + height - 1 and x == start_x + width - 1 and bottom and right:
                screen.addch(y, x, '┘', attr)
            elif (y == start_y and top) or (y == start_y + height - 1 and bottom):
                screen.addch(y, x, '─', attr)
            elif (x == start_x and left) or (x == start_x + width - 1 and right):
                screen.addch(y, x, '│', attr)

    if cell == 15:
        for y in range(start_y + 1, start_y + height - 1):
            for x in range(start_x + 1, start_x + width - 1):
                screen.addch(y, x, '█', curses.color_pair(1))


def draw_path(
    screen: curses.window,
    path: List[Tuple[int, int]],
    width: int,
    height: int,
    attr: int = 0
) -> None:
    """
    Draw the solution path on the maze.

    Args:
        screen: curses window object.
        path: List of (x, y) coordinates.
        width: Cell width.
        height: Cell height.
        attr: curses attribute.
    """
    for cell_x, cell_y in path:
        y = cell_y * (height - 1) + 1
        x = cell_x * (width - 1) + 1
        screen.addch(y, x, '•', attr)


def draw_entry_exit(
    screen: curses.window,
    entry: Tuple[int, int],
    exit_pos: Tuple[int, int],
    width: int,
    height: int,
    entry_attr: int = 0,
    exit_attr: int = 0
) -> None:
    """
    Draw entry (S) and exit (E) points.

    Args:
        screen: curses window object.
        entry: Entry coordinates (x, y).
        exit_pos: Exit coordinates (x, y).
        width: Cell width.
        height: Cell height.
        entry_attr: curses style for entry.
        exit_attr: curses style for exit.
    """
    entry_x, entry_y = entry
    exit_x, exit_y = exit_pos

    cell_y = entry_y * (height - 1) + 1
    cell_x = entry_x * (width - 1) + 1
    screen.addch(cell_y, cell_x, 'S', entry_attr)

    cell_y = exit_y * (height - 1) + 1
    cell_x = exit_x * (width - 1) + 1
    screen.addch(cell_y, cell_x, 'E', exit_attr)


def draw(
    screen: curses.window,
    maze: Any,
    config_data: Dict[str, Any]
) -> None:
    """
    Main curses rendering loop for the maze.

    Handles:
    - Rendering maze grid
    - Displaying path
    - Entry/exit
    - User interaction (color, regenerate, toggle path)

    Args:
        screen: curses window object.
        maze: Maze object containing grid, width, height, path, entry, exit.
        config_data: Configuration dictionary used for regeneration.
    """
    curses.curs_set(0)
    screen.keypad(True)

    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_WHITE, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_CYAN, -1)
    curses.init_pair(4, curses.COLOR_YELLOW, -1)
    curses.init_pair(5, curses.COLOR_RED, -1)
    curses.init_pair(6, curses.COLOR_MAGENTA, -1)

    width = 4
    height = 3

    current_color = 1
    show_path = False

    while True:
        screen.clear()

        start_y = 0
        for y in range(maze.height):
            start_x = 0
            for x in range(maze.width):
                cell = maze.grid[y][x]
                draw_cell(
                    screen,
                    start_x,
                    start_y,
                    width,
                    height,
                    cell,
                    curses.color_pair(current_color)
                )
                start_x += width - 1
            start_y += height - 1

        if show_path:
            draw_path(
                screen,
                maze.path,
                width,
                height,
                curses.color_pair(5) | curses.A_BOLD
            )

        draw_entry_exit(
            screen,
            maze.entry,
            maze.exit,
            width,
            height,
            curses.color_pair(2) | curses.A_BOLD,
            curses.color_pair(6) | curses.A_BOLD
        )

        info_y = maze.height * (height - 1) + 2

        screen.addstr(
            info_y,
            0,
            "1: change color   2: show/hide path   3: regenerate maze   q: quit"
        )

        screen.addstr(info_y + 2, 0, "Enter action key:")

        screen.refresh()
        key = screen.getch()

        if key == ord('1'):
            current_color += 1
            if current_color > 4:
                current_color = 1

        elif key == ord('2'):
            show_path = not show_path

        elif key == ord('3'):
            maze = generator.algo(config_data)

        elif key in (ord('q'), ord('Q')):
            break