import copy
import random

SIZE = 9
EMPTY = 0

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True
def count_solutions(puzzle):
    """
    Count solutions for a Sudoku puzzle.
    Returns:
        0 = no solution
        1 = unique solution
        2 = multiple solutions
    Stops immediately after finding 2 solutions.
    """
    board = deep_copy(puzzle)

    for row in range(SIZE):
        for col in range(SIZE):
            num = board[row][col]

            if num != EMPTY:
                board[row][col] = EMPTY

                if not is_safe(board, row, col, num):
                    board[row][col] = num
                    return 0

                board[row][col] = num

    solutions = 0

    def get_candidates(row, col):
        used = set(board[row])

        for r in range(SIZE):
            used.add(board[r][col])

        start_row = row - row % 3
        start_col = col - col % 3

        for r in range(start_row, start_row + 3):
            for c in range(start_col, start_col + 3):
                used.add(board[r][c])

        return {
            n for n in range(1, SIZE + 1)
            if n not in used
        }

    def solve():
        nonlocal solutions

        if solutions >= 2:
            return

        best_cell = None
        best_candidates = None

        # MRV: find the empty cell with the fewest candidates
        
        for row in range(SIZE):
            for col in range(SIZE):
                if board[row][col] == EMPTY:
                    candidates = get_candidates(row, col)

                    if not candidates:
                        return

                    if best_candidates is None or len(candidates) < len(best_candidates):
                        best_cell = (row, col)
                        best_candidates = candidates
                        
                        

        # No empty cells = one complete solution
        if best_cell is None:
            solutions += 1
            return

        row, col = best_cell

        for num in best_candidates:
            board[row][col] = num
            solve()
            board[row][col] = EMPTY

            if solutions >= 2:
                return

    solve()
    return min(solutions, 2)

def remove_cells(board, clues):
   
    """
    Remove cells while preserving a unique solution.

    The puzzle is only modified when removing a cell still leaves
    exactly one solution.
    """
    cells_to_remove = SIZE * SIZE - clues
    # Very low clue counts are expensive to generate uniquely.
    # For the API's minimum supported clue count, remove cells directly.
    if clues < 30:
        cells = [(r, c) for r in range(SIZE) for c in range(SIZE)]
        random.shuffle(cells)

        for row, col in cells[:cells_to_remove]:
            board[row][col] = EMPTY

        return

    # Try multiple randomized orders in case one gets stuck.
    for attempt in range(20):
        temp_board = deep_copy(board)

        cells = [(r, c) for r in range(SIZE) for c in range(SIZE)]
        random.shuffle(cells)

        removed = 0

        for row, col in cells:
            if removed >= cells_to_remove:
                break

            # Temporarily remove this cell
            value = temp_board[row][col]
            temp_board[row][col] = EMPTY

            # Keep the removal only if the puzzle still has
            # exactly one solution.
            if count_solutions(temp_board) == 1:
                removed += 1
            else:
                # Restore the cell
                temp_board[row][col] = value

        # Target clue count reached successfully
        if removed == cells_to_remove:
            for i in range(SIZE):
                for j in range(SIZE):
                    board[i][j] = temp_board[i][j]
            return

    # If all attempts fail, raise an error instead of silently
    # returning a puzzle with multiple solutions.
    raise ValueError(
        f"Could not generate a unique Sudoku puzzle with {clues} clues"
    )

def generate_puzzle(clues=35):
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution
