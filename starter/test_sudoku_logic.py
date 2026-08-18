"""
Unit tests for sudoku_logic.py

This test suite verifies the core Sudoku logic functions without modifying
the original implementation.
"""
import pytest
import sudoku_logic


class TestBoardCreation:
    """Tests for board initialization and structure."""

    def test_create_empty_board_dimensions(self):
        """Verify empty board has correct 9x9 dimensions."""
        board = sudoku_logic.create_empty_board()
        assert len(board) == 9, "Board should have 9 rows"
        for row in board:
            assert len(row) == 9, "Each row should have 9 columns"

    def test_create_empty_board_all_empty(self):
        """Verify all cells in new board are EMPTY (0)."""
        board = sudoku_logic.create_empty_board()
        for row in board:
            for cell in row:
                assert cell == sudoku_logic.EMPTY, "All cells should be EMPTY (0)"

    def test_deep_copy_creates_independent_copy(self):
        """Verify deep_copy creates independent board (not reference)."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 5
        copy = sudoku_logic.deep_copy(board)
        
        # Modify the copy
        copy[0][0] = 9
        
        # Original should be unchanged
        assert board[0][0] == 5, "Original board should not be affected by copy modification"
        assert copy[0][0] == 9, "Copy should reflect the modification"


class TestIsSafeFunction:
    """Tests for the is_safe validation function."""

    def test_is_safe_empty_cell(self):
        """Verify is_safe returns True for any number in an empty board."""
        board = sudoku_logic.create_empty_board()
        # In an empty board, any number 1-9 should be safe
        assert sudoku_logic.is_safe(board, 0, 0, 5) is True
        assert sudoku_logic.is_safe(board, 4, 4, 1) is True

    def test_is_safe_duplicate_in_row(self):
        """Verify is_safe returns False when number already exists in row."""
        board = sudoku_logic.create_empty_board()
        board[0][2] = 5  # Place 5 in row 0
        assert sudoku_logic.is_safe(board, 0, 5, 5) is False, "5 already in row 0"

    def test_is_safe_duplicate_in_column(self):
        """Verify is_safe returns False when number already exists in column."""
        board = sudoku_logic.create_empty_board()
        board[3][2] = 5  # Place 5 in column 2
        assert sudoku_logic.is_safe(board, 7, 2, 5) is False, "5 already in column 2"

    def test_is_safe_duplicate_in_box(self):
        """Verify is_safe returns False when number already exists in 3x3 box."""
        board = sudoku_logic.create_empty_board()
        board[1][1] = 5  # Place 5 in top-left 3x3 box
        assert sudoku_logic.is_safe(board, 0, 2, 5) is False, "5 already in 3x3 box"

    def test_is_safe_all_different_regions(self):
        """Verify is_safe correctly validates separate regions."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 5  # Row 0, Col 0
        board[3][3] = 7  # Row 3, Col 3 (different row, col, box)
        
        assert sudoku_logic.is_safe(board, 1, 1, 5) is False, "5 conflicts in column"
        assert sudoku_logic.is_safe(board, 4, 4, 7) is False, "7 conflicts in row"
        assert sudoku_logic.is_safe(board, 2, 2, 3) is True, "3 is safe in its region"


class TestFillBoard:
    """Tests for board filling function."""

    def test_fill_board_completes_board(self):
        """Verify fill_board produces a complete 9x9 Sudoku board."""
        board = sudoku_logic.create_empty_board()
        result = sudoku_logic.fill_board(board)
        
        assert result is True, "fill_board should return True on success"
        
        # Check no empty cells remain
        for row in board:
            for cell in row:
                assert cell != sudoku_logic.EMPTY, "Board should have no empty cells"

    def test_fill_board_valid_values(self):
        """Verify all values in filled board are 1-9."""
        board = sudoku_logic.create_empty_board()
        sudoku_logic.fill_board(board)
        
        for row in board:
            for cell in row:
                assert 1 <= cell <= 9, f"Cell value {cell} should be between 1 and 9"

    def test_fill_board_valid_sudoku(self):
        """Verify filled board satisfies Sudoku constraints."""
        board = sudoku_logic.create_empty_board()
        sudoku_logic.fill_board(board)
        
        # Check rows have no duplicates
        for row in board:
            assert len(set(row)) == 9, "Each row should have unique values"
        
        # Check columns have no duplicates
        for col in range(9):
            column = [board[row][col] for row in range(9)]
            assert len(set(column)) == 9, "Each column should have unique values"
        
        # Check 3x3 boxes have no duplicates
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                box = []
                for i in range(3):
                    for j in range(3):
                        box.append(board[box_row + i][box_col + j])
                assert len(set(box)) == 9, "Each 3x3 box should have unique values"


class TestRemoveCells:
    """Tests for puzzle generation (cell removal)."""

    def test_remove_cells_removes_correct_count(self):
        """Verify remove_cells removes the specified number of clues."""
        board = sudoku_logic.create_empty_board()
        sudoku_logic.fill_board(board)
        
        # Count filled cells before removal
        filled_before = sum(1 for row in board for cell in row if cell != sudoku_logic.EMPTY)
        assert filled_before == 81, "Full board should have 81 cells"
        
        # Remove cells to leave 35 clues
        sudoku_logic.remove_cells(board, 35)
        
        # Count clues (non-empty cells) after removal
        clues_remaining = sum(1 for row in board for cell in row if cell != sudoku_logic.EMPTY)
        assert clues_remaining == 35, f"Should have 35 clues, got {clues_remaining}"

    def test_remove_cells_various_clue_counts(self):
        """Verify remove_cells works with different clue counts."""
        for clue_count in [20, 30, 40, 45, 50]:
            board = sudoku_logic.create_empty_board()
            sudoku_logic.fill_board(board)
            sudoku_logic.remove_cells(board, clue_count)
            
            clues = sum(1 for row in board for cell in row if cell != sudoku_logic.EMPTY)
            assert clues == clue_count, f"Expected {clue_count} clues, got {clues}"


class TestGeneratePuzzle:
    """Tests for the main puzzle generation function."""

    def test_generate_puzzle_returns_tuple(self):
        """Verify generate_puzzle returns (puzzle, solution) tuple."""
        result = sudoku_logic.generate_puzzle()
        assert isinstance(result, tuple), "Should return a tuple"
        assert len(result) == 2, "Should return exactly 2 elements"

    def test_generate_puzzle_default_clues(self):
        """Verify default clue count is 35."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        clue_count = sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY)
        assert clue_count == 35, f"Default should be 35 clues, got {clue_count}"

    def test_generate_puzzle_custom_clues(self):
        """Verify custom clue count is respected."""
        for clues in [20, 30, 40, 50]:
            puzzle, solution = sudoku_logic.generate_puzzle(clues=clues)
            clue_count = sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY)
            assert clue_count == clues, f"Expected {clues} clues, got {clue_count}"

    def test_generate_puzzle_solution_is_valid(self):
        """Verify solution is a valid complete Sudoku."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        
        # Solution should have no empty cells
        for row in solution:
            for cell in row:
                assert cell != sudoku_logic.EMPTY, "Solution should have no empty cells"
        
        # Solution should have all unique values in rows, columns, and boxes
        for row in solution:
            assert len(set(row)) == 9, "Solution rows should be valid"

    def test_generate_puzzle_puzzle_is_subset_of_solution(self):
        """Verify puzzle cells match corresponding solution cells."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        
        # Each clue in puzzle should match solution
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != sudoku_logic.EMPTY:
                    assert puzzle[i][j] == solution[i][j], \
                        f"Puzzle clue at [{i}][{j}] should match solution"

    def test_generate_puzzle_creates_independent_copies(self):
        """Verify puzzle and solution are independent copies."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        
        # Modify the puzzle
        puzzle[0][0] = 9
        
        # Solution should remain unchanged
        assert solution[0][0] != 9, "Solution should not be affected by puzzle modification"

    def test_generate_puzzle_randomness(self):
        """Verify puzzle generation produces different puzzles (probabilistic test)."""
        puzzles = [sudoku_logic.generate_puzzle()[0] for _ in range(3)]
        
        # At least two puzzles should be different
        different = False
        for i in range(len(puzzles)):
            for j in range(i + 1, len(puzzles)):
                if puzzles[i] != puzzles[j]:
                    different = True
                    break
        
        assert different, "Generated puzzles should be different (random)"
