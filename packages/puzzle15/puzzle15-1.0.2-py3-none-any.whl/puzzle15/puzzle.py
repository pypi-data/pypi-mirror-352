import random
from typing import List, Tuple

class Puzzle:
    def __init__(self, grid: List[List[int]]):
        self._grid = [row.copy() for row in grid]
        self._height = len(grid)
        self._width = len(grid[0])
        self._blank_pos = self._find_blank()
        self._validate_puzzle()

    @classmethod
    def from_dimensions(cls, height: int, width: int):
        numbers = list(range(1, height * width)) + [-1]  # -1 denotes the blank
        random.shuffle(numbers)
        grid = [numbers[i * width:(i + 1) * width] for i in range(height)]
        puzzle = cls(grid)
        if not puzzle._is_solvable():
            puzzle._make_solvable()
        return puzzle

    @classmethod
    def from_string(cls, puzzle_str: str):
        rows = puzzle_str.strip().split('|')
        grid = [[int(cell.strip()) for cell in row.strip().split()] for row in rows]
        puzzle = cls(grid)
        if not puzzle._is_solvable():
            raise ValueError("The provided puzzle configuration is not solvable.")
        return puzzle

    def _find_blank(self) -> Tuple[int, int]:
        for y, row in enumerate(self._grid):
            for x, val in enumerate(row):
                if val == -1:
                    return y, x
        raise ValueError("No blank space (-1) found in the puzzle.")

    def _validate_puzzle(self):
        flat_list = [num for row in self._grid for num in row]
        expected_numbers = set(range(1, self._width * self._height)) | {-1}
        if set(flat_list) != expected_numbers:
            raise ValueError("Puzzle contains duplicates or incorrect numbers.")

    def _is_solvable(self) -> bool:
        flat_list = [num for row in self._grid for num in row if num != -1]
        inversions = sum(
            1
            for i in range(len(flat_list))
            for j in range(i + 1, len(flat_list))
            if flat_list[i] > flat_list[j]
        )
        blank_row_from_bottom = self._height - self._blank_pos[1]

        if self._width % 2 == 1:
            return inversions % 2 == 0
        else:
            return (inversions + blank_row_from_bottom) % 2 == 1

    def _make_solvable(self):
        tiles = [(y, x) for y in range(self._height) for x in range(self._width) if self._grid[y][x] != -1]
        if len(tiles) < 2:
            raise ValueError("Not enough non-blank tiles to adjust solvability.")

        (y1, x1), (y2, x2) = tiles[0], tiles[1]
        self._grid[y1][x1], self._grid[y2][x2] = self._grid[y2][x2], self._grid[y1][x1]

    def possible_moves(self) -> List[str]:
        moves = []
        y, x = self._blank_pos
        if x > 0:
            moves.append('left')
        if x < self._width - 1:
            moves.append('right')
        if y > 0:
            moves.append('up')
        if y < self._height - 1:
            moves.append('down')
        return moves

    def move(self, direction: str):
        if self.is_solved():
            raise ValueError("Puzzle is already solved.")
        if direction not in self.possible_moves():
            raise ValueError("Invalid move direction.")

        dy, dx = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }[direction]

        y, x = self._blank_pos
        ny, nx = y + dy, x + dx

        self._grid[y][x], self._grid[ny][nx] = self._grid[ny][nx], self._grid[y][x]
        self._blank_pos = (ny, nx)

    def grid(self) -> List[List[int]]:
        """
        Return a copy of the grid.
        """
        return [row.copy() for row in self._grid]

    def is_solved(self) -> bool:
        """
        Check if the puzzle is in the solved state.
        """
        expected = [[i * self._width + j + 1 for j in range(self._width)] for i in range(self._height)]
        expected[self._height - 1][self._width - 1] = -1
        return self._grid == expected

    def __str__(self):
        return '\n'.join(' '.join(f"{val:2}" if val != -1 else '  ' for val in row) for row in self._grid)