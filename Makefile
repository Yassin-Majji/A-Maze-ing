NAME        = a_maze_ing.py
CONFIG      = config.txt
REQUIREMENTS = flake8 mypy

run:
	python3 $(NAME) $(CONFIG)

install:
	pip install $(REQUIREMENTS)


debug:
	python3 -m pdb $(NAME) $(CONFIG)

clean:
	find . -type d \( -name "__pycache__" -o -name ".mypy_cache" \) -exec rm -rf {} + 2>/dev/null; true
	find . -name "*.pyc" -delete 2>/dev/null; true

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
	        --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

.PHONY: install run debug clean lint lint-strict
