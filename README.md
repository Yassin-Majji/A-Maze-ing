*This project has been created as part of the 42 curriculum by ikoubaz.*

# A-Maze-ing

## Description

A-Maze-ing is a Python maze generator and visualiser. It generates mazes from a configuration file, writes the result to a hex-encoded output file, and renders the maze interactively in the terminal using curses. The generator supports both perfect mazes (unique path between entry and exit) and non-perfect mazes (with loops). Every generated maze embeds a visible **"42"** pattern made of fully-closed cells, as required by the subject.

## Instructions

### Requirements

- Python 3.10 or later
- No external dependencies for the core program (curses is part of the standard library)
- `flake8` and `mypy` for linting (installed via `make install`)

### Installation

```bash
make install
```

### Run

```bash
python3 a_maze_ing.py config.txt
# or
make run
```

### Debug

```bash
make debug
```

### Lint

```bash
make lint
```

### Clean

```bash
make clean
```

## Configuration file format

The config file uses `KEY=VALUE` pairs, one per line. Lines starting with `#` are comments and are ignored.

| Key         | Required | Description                                  | Example           |
|-------------|----------|----------------------------------------------|-------------------|
| WIDTH       | Yes      | Number of columns (integer > 0)              | `WIDTH=20`        |
| HEIGHT      | Yes      | Number of rows (integer > 0)                 | `HEIGHT=15`       |
| ENTRY       | Yes      | Entry cell as `x,y` (0-indexed)              | `ENTRY=0,0`       |
| EXIT        | Yes      | Exit cell as `x,y` (must differ from ENTRY)  | `EXIT=19,14`      |
| OUTPUT_FILE | Yes      | Path of the output file to write             | `OUTPUT_FILE=maze_output.txt` |
| PERFECT     | Yes      | `True` = unique path, `False` = loops        | `PERFECT=True`    |
| SEED        | No       | Integer seed for reproducible generation     | `SEED=42`         |

### Example config.txt

```
# A-Maze-ing default configuration
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze_output.txt
PERFECT=True
SEED=42
```

## Output file format

```
<hex grid: one row per line, one hex digit per cell>

<entry_x>,<entry_y>
<exit_x>,<exit_y>
<path as sequence of N/E/S/W characters>
```

Wall encoding per hex digit (4-bit bitmask):

| Bit | Direction | Value |
|-----|-----------|-------|
| 0   | North     | 0x1   |
| 1   | East      | 0x2   |
| 2   | South     | 0x4   |
| 3   | West      | 0x8   |

Bit = 1 means the wall is **closed**.

## Visual representation (terminal controls)

| Key | Action                          |
|-----|---------------------------------|
| `c` | Cycle wall colour               |
| `p` | Toggle solution path visibility |
| `r` | Re-generate a new maze          |
| `q` | Quit                            |

## Maze generation algorithm

The project uses the **DFS Recursive Backtracker** (also called randomised depth-first search).

**How it works:**
1. Start from the entry cell.
2. Mark the current cell as visited.
3. Randomly shuffle the four cardinal directions.
4. For each direction, if the neighbour is unvisited and carving the wall would not create a 3×3 open area, remove the shared wall and recurse into the neighbour.
5. When no unvisited neighbours remain, backtrack.

**Why this algorithm?**
- It produces mazes with long, winding corridors which are aesthetically pleasing and challenging to solve.
- It is straightforward to implement and easy to extend (e.g., to add loops for non-perfect mazes).
- It integrates naturally with a seed for reproducibility.
- It guarantees full connectivity (every cell is reachable) when used correctly.

## "42" pattern

A pixel-art **42** is embedded into every maze large enough to contain it (minimum ~11 columns × 7 rows). The pattern is placed in the upper-right area of the maze. Pattern cells are fully closed (wall value = 15 = `F` in hex), making them visually distinct as solid blocks. If the maze is too small, a warning is printed to stderr.

## Code reusability

The file `class_maze.py` contains the standalone `MazeGenerator` class which can be imported into any project independently of the rest of the maze program.

The `mazegen_pkg/` directory contains a pip-installable package (`mazegen-1.0.0-py3-none-any.whl` once built) that exposes this class.

### Using the reusable module

```python
from class_maze import MazeGenerator

# Instantiate
gen = MazeGenerator(width=20, height=15, entry=(0, 0), exit_pos=(19, 14), seed=42)

# Generate
gen.generate()

# Solve (find shortest path)
gen.solve()

# Access the grid (list of lists of ints, hex bitmask per cell)
grid = gen.grid

# Access solution path (list of (x, y) tuples)
path = gen.path

# Export to file
gen.export("my_maze.txt")
```

### Custom parameters

```python
# Non-perfect maze with loops, no fixed seed
gen = MazeGenerator(width=30, height=20, perfect=False)
gen.generate().solve()

# Reproducible maze
gen = MazeGenerator(width=10, height=10, seed=1234)
gen.generate().solve()
```

### Building the pip package

```bash
cd mazegen_pkg
pip install build
python -m build
# Produces dist/mazegen-1.0.0-py3-none-any.whl
```

## Team and project management

### Roles

| Member  | Role                                                             |
|---------|------------------------------------------------------------------|
| ikoubaz | Maze algorithm, file I/O, parser, visual renderer, package setup |

### Planning

**Anticipated plan:**
1. Parser and config validation
2. Core DFS generation algorithm
3. Output file format
4. Terminal visualisation with curses
5. "42" pattern and border wall enforcement
6. Reusable module and pip package
7. README and final polish

**How it evolved:**
The core generation and display were implemented first. The "42" pattern and strict border wall enforcement were added in a second pass after testing revealed that walls near the border were sometimes incoherent. The reusable module was extracted from the algorithm file into a clean standalone class.

**What worked well:**
- DFS backtracker is simple and produces good mazes.
- Using a bitmask per cell made wall operations efficient.
- The curses display loop is clean and extensible.

**What could be improved:**
- Support multiple algorithms (Kruskal's, Prim's) for bonus.
- Add animated generation mode.
- Improve the "42" placement to be configurable (position, scale).

### Tools used

- Python 3 standard library (curses, collections, random, typing)
- flake8, mypy for code quality
- Git for version control

## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive Backtracker — Jamis Buck's blog](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
- [Python curses documentation](https://docs.python.org/3/library/curses.html)
- [Python typing module](https://docs.python.org/3/library/typing.html)
- [PEP 257 — Docstring conventions](https://peps.python.org/pep-0257/)
- [Packaging Python projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)

### AI usage

AI (Claude) was used for:
- Reviewing code structure and suggesting type hint improvements.
- Helping design the "42" pixel bitmap pattern layout.
- Generating docstrings and README template sections.
- Suggesting the BFS solver structure.

All AI-generated content was reviewed, tested, and adapted by the team member before inclusion.
