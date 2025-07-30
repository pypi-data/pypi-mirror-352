import pytest
from puzzle15.puzzle import Puzzle

def test_puzzle_initialization():
    # Test valid puzzle initialization
    try:
        grid = [[1, 2, 3], [4, 5, 6], [7, 8, -1]]
        Puzzle(grid)
    except ValueError:
        pytest.fail("Puzzle initialization failed with valid grid")

    # Test invalid puzzle with duplicates
    with pytest.raises(ValueError):
        Puzzle([[1, 1, 3], [4, 5, 6], [7, 8, -1]])

    # Test invalid puzzle with missing blank
    with pytest.raises(ValueError):
        Puzzle([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

def test_puzzle_from_dimensions():
    # Test 3x3 puzzle generation
    puzzle = Puzzle.from_dimensions(3, 3)
    assert_grid(puzzle.grid(), 3, 3)

    # Test 4x4 puzzle generation
    puzzle = Puzzle.from_dimensions(4, 4)
    assert_grid(puzzle.grid(), 4, 4)

def assert_grid(grid, width, height):
    assert len(grid) == width

    for row in grid:
        assert len(row) == height

def test_puzzle_from_string():
    # Test valid puzzle string
    puzzle_str = "1 2 3|4 5 6|7 8 -1"
    puzzle = Puzzle.from_string(puzzle_str)

    expected_grid = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, -1]
    ]
    assert puzzle.grid() == expected_grid

def test_possible_moves():
    # Test moves in center position
    grid = [[1, 2, 3], [4, -1, 6], [7, 8, 5]]
    puzzle = Puzzle(grid)
    moves = puzzle.possible_moves()
    assert set(moves) == {'up', 'down', 'left', 'right'}

    # Test moves in corner position
    grid = [[-1, 2, 3], [4, 5, 6], [7, 8, 1]]
    puzzle = Puzzle(grid)
    moves = puzzle.possible_moves()
    assert set(moves) == {'down', 'right'}

def test_move():
    # Test valid move
    grid = [[1, 2, 3], [4, -1, 6], [7, 8, 5]]
    puzzle = Puzzle(grid)
    puzzle.move('right')
    assert puzzle.grid()[1][2] == -1
    assert puzzle.grid()[1][1] == 6

    # Test invalid move
    grid = [[-1, 2, 3], [4, 1, 6], [7, 8, 5]]
    puzzle = Puzzle(grid)
    with pytest.raises(ValueError):
        puzzle.move('up')

def test_grid():
    initial_grid = [
        [1, 2, 3],
        [4, -1, 5],
        [6, 7, 8]
    ]
    puzzle = Puzzle(initial_grid)

    grid_copy = puzzle.grid()
    
    assert grid_copy is not puzzle.grid()
    assert grid_copy == initial_grid

    # Ensure changes in copy does not affect the original grid
    grid_copy[0][0] = 999
    assert puzzle.grid() == initial_grid

def test_is_solved():
    solved_grid = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, -1]
    ]
    puzzle = Puzzle(solved_grid)
    assert puzzle.is_solved()

    unsolved_grid = [
        [1, 2, 3],
        [4, -1, 5],
        [6, 7, 8]
    ]
    puzzle = Puzzle(unsolved_grid)
    assert not puzzle.is_solved()