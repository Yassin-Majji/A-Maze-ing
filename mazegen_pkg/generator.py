import random
import sys
from typing import Dict, List, Optional, Set, Tuple
from collections import deque

DIRS: List[Tuple[int, int, int, int]] = [
    (0, -1, 0, 2),
    (1,  0, 1, 3),
    (0,  1, 2, 0),
    (-1, 0, 3, 1),
]

DIGIT_4 = [
    [True, False, True, False],
    [True, False, True, False],
    [True, True, True, True],
    [False, False, True, False],
    [False, False, True, False],
]

DIGIT_2 = [
    [True, True, True, False],
    [False, False, True, False],
    [True, True, True, False],
    [True, False, False, False],
    [True, True, True, False],
]

PATTERN_42 = [DIGIT_4[r] + [False] + DIGIT_2[r] for r in range(5)]
PATTERN_ROWS = 5
PATTERN_COLS = 9


class MazeGenerator:
    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit_pos: Tuple[int, int],
        perfect: bool = True,
        seed: Optional[int] = None,
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit_pos
        self.perfect = perfect
        self.path: List[Tuple[int, int]] = []

        if seed is not None:
            random.seed(seed)

        self.grid: List[List[int]] = [[15] * width for _ in range(height)]
        self.visited: Set[Tuple[int, int]] = set()
        self._pattern_cells: Set[Tuple[int, int]] = set()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _has_full_open_area(self, x: int, y: int) -> bool:
        if x < 0 or y < 0 or x + 2 >= self.width or y + 2 >= self.height:
            return False
        for dy in range(3):
            for dx in range(3):
                if self.grid[y + dy][x + dx] != 0:
                    return False
        return True

    def _carve(
        self, x1: int, y1: int, x2: int, y2: int, direction: Tuple[int, int, int, int]
    ) -> bool:
        _, _, wall, opp = direction

        # remove walls
        self.grid[y1][x1] &= ~(1 << wall)
        self.grid[y2][x2] &= ~(1 << opp)

        # 🚨 prevent fully open cell (IMPORTANT FIX)
        if self.grid[y1][x1] == 0 or self.grid[y2][x2] == 0:
            self.grid[y1][x1] |= (1 << wall)
            self.grid[y2][x2] |= (1 << opp)
            return False

        # prevent 3x3 empty area
        for cy in range(max(0, min(y1, y2) - 2), min(self.height - 2, max(y1, y2) + 2) + 1):
            for cx in range(max(0, min(x1, x2) - 2), min(self.width - 2, max(x1, x2) + 2) + 1):
                if self._has_full_open_area(cx, cy):
                    self.grid[y1][x1] |= (1 << wall)
                    self.grid[y2][x2] |= (1 << opp)
                    return False

        return True

    # ------------------------------------------------------------------
    # 42 pattern
    # ------------------------------------------------------------------
    def _compute_42_cells(self) -> bool:
        if self.height < PATTERN_ROWS + 2 or self.width < PATTERN_COLS + 2:
            return False

        offset_x = (self.width - PATTERN_COLS) // 2
        offset_y = (self.height - PATTERN_ROWS) // 2

        reserved: Set[Tuple[int, int]] = set()

        for r in range(PATTERN_ROWS):
            for c in range(PATTERN_COLS):
                if PATTERN_42[r][c]:
                    reserved.add((offset_x + c, offset_y + r))

        if self.entry in reserved or self.exit in reserved:
            print("Error: ENTRY or EXIT inside '42' pattern.", file=sys.stderr)
            sys.exit(1)

        self._pattern_cells = reserved
        return True

    def _apply_42_pattern(self) -> None:
        for (x, y) in self._pattern_cells:
            self.grid[y][x] = 15
            for dx, dy, _, opp in DIRS:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in self._pattern_cells:
                        self.grid[ny][nx] |= (1 << opp)

    # ------------------------------------------------------------------
    # Borders
    # ------------------------------------------------------------------
    def _enforce_borders(self) -> None:
        for x in range(self.width):
            self.grid[0][x] |= 1
            self.grid[self.height - 1][x] |= 4

        for y in range(self.height):
            self.grid[y][0] |= 8
            self.grid[y][self.width - 1] |= 2

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------
    def _dfs(self, x: int, y: int) -> None:
        self.visited.add((x, y))
        dirs = DIRS[:]
        random.shuffle(dirs)

        for direction in dirs:
            dx, dy, _, _ = direction
            nx, ny = x + dx, y + dy

            if not (0 <= nx < self.width and 0 <= ny < self.height):
                continue
            if (nx, ny) in self.visited or (nx, ny) in self._pattern_cells:
                continue

            if self._carve(x, y, nx, ny, direction):
                self._dfs(nx, ny)

    def generate(self) -> None:
        if not self._compute_42_cells():
            print("Error: Maze too small.", file=sys.stderr)
            sys.exit(1)

        self.visited = set(self._pattern_cells)
        self._dfs(*self.entry)

        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in self.visited and (x, y) not in self._pattern_cells:
                    self._dfs(x, y)

        if not self.perfect:
            self._add_loops()

        self._apply_42_pattern()
        self._enforce_borders()

    def _add_loops(self) -> None:
        for _ in range((self.width * self.height) // 5):
            x = random.randint(0, self.width - 2)
            y = random.randint(0, self.height - 2)
            dx, dy, wall, opp = random.choice(DIRS)
            nx, ny = x + dx, y + dy

            if 0 <= nx < self.width and 0 <= ny < self.height:
                if (x, y) not in self._pattern_cells and (nx, ny) not in self._pattern_cells:
                    self._carve(x, y, nx, ny, (dx, dy, wall, opp))

    # ------------------------------------------------------------------
    # Solver
    # ------------------------------------------------------------------
    def solve(self) -> None:
        q = deque([self.entry])
        parent = {self.entry: None}

        while q:
            x, y = q.popleft()
            if (x, y) == self.exit:
                break

            for dx, dy, wall, _ in DIRS:
                nx, ny = x + dx, y + dy
                if (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and not (self.grid[y][x] & (1 << wall))
                    and (nx, ny) not in parent
                ):
                    parent[(nx, ny)] = (x, y)
                    q.append((nx, ny))

        path = []
        cur = self.exit
        while cur is not None:
            path.append(cur)
            cur = parent.get(cur)

        self.path = path[::-1]


# --------------------------------------------------------------------------
# Export
# --------------------------------------------------------------------------
def export_maze(maze: MazeGenerator, filename: str) -> None:
    try:
        with open(filename, "w") as f:
            for row in maze.grid:
                f.write("".join(format(c, "X") for c in row) + "\n")

            f.write("\n")
            f.write(f"{maze.entry[0]},{maze.entry[1]}\n")
            f.write(f"{maze.exit[0]},{maze.exit[1]}\n")

            path_str = ""
            for i in range(1, len(maze.path)):
                x1, y1 = maze.path[i - 1]
                x2, y2 = maze.path[i]

                if x2 == x1 + 1:
                    path_str += "E"
                elif x2 == x1 - 1:
                    path_str += "W"
                elif y2 == y1 + 1:
                    path_str += "S"
                elif y2 == y1 - 1:
                    path_str += "N"

            f.write(path_str + "\n")

    except OSError as e:
        print(f"Error writing file: {e}", file=sys.stderr)
        sys.exit(1)


# --------------------------------------------------------------------------
# API
# --------------------------------------------------------------------------
def algo(config: Dict[str, object]) -> MazeGenerator:
    maze = MazeGenerator(
        int(config["WIDTH"]),
        int(config["HEIGHT"]),
        config["ENTRY"],
        config["EXIT"],
        bool(config["PERFECT"]),
        config.get("SEED"),
    )

    maze.generate()
    maze.solve()
    export_maze(maze, str(config["OUTPUT_FILE"]))

    return maze