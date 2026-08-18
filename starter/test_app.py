"""
Integration tests for the Flask Sudoku application.

This test suite verifies the Flask routes and their integration with
the sudoku_logic module.
"""
import pytest
import json
import sudoku_logic


class TestIndexRoute:
    """Tests for the index route."""

    def test_index_returns_200(self, client):
        """Verify index route returns HTTP 200."""
        response = client.get('/')
        assert response.status_code == 200, "Index should return 200 OK"

    def test_index_returns_html(self, client):
        """Verify index route returns HTML content."""
        response = client.get('/')
        assert response.content_type is not None
        assert 'text/html' in response.content_type, "Index should return HTML"


class TestNewGameRoute:
    """Tests for the /new route (puzzle generation)."""

    def test_new_game_default_returns_puzzle(self, client):
        """Verify /new returns a valid puzzle structure."""
        response = client.get('/new')
        assert response.status_code == 200, "/new should return 200"
        
        data = response.get_json()
        assert data is not None, "Response should be JSON"
        assert 'puzzle' in data, "Response should contain 'puzzle' key"
        assert isinstance(data['puzzle'], list), "Puzzle should be a list"

    def test_new_game_puzzle_dimensions(self, client):
        """Verify puzzle has correct 9x9 dimensions."""
        response = client.get('/new')
        data = response.get_json()
        puzzle = data['puzzle']
        
        assert len(puzzle) == 9, "Puzzle should have 9 rows"
        for row in puzzle:
            assert len(row) == 9, "Each row should have 9 columns"

    def test_new_game_puzzle_contains_clues(self, client):
        """Verify puzzle contains non-empty cells (clues)."""
        response = client.get('/new')
        data = response.get_json()
        puzzle = data['puzzle']
        
        clue_count = sum(1 for row in puzzle for cell in row if cell != 0)
        assert clue_count > 0, "Puzzle should contain at least some clues"
        # Default should be 35 clues
        assert clue_count == 35, f"Default puzzle should have 35 clues, got {clue_count}"

    def test_new_game_custom_clues(self, client):
        """Verify custom clues parameter is respected."""
        response = client.get('/new?clues=40')
        data = response.get_json()
        puzzle = data['puzzle']
        
        clue_count = sum(1 for row in puzzle for cell in row if cell != 0)
        assert clue_count == 40, f"Should have 40 clues, got {clue_count}"

    def test_new_game_different_puzzles(self, client):
        """Verify each call to /new generates a different puzzle."""
        response1 = client.get('/new')
        puzzle1 = response1.get_json()['puzzle']
        
        response2 = client.get('/new')
        puzzle2 = response2.get_json()['puzzle']
        
        assert puzzle1 != puzzle2, "Different calls should generate different puzzles"

    def test_new_game_stores_in_current(self, client, flask_app):
        """Verify new game stores puzzle and solution in CURRENT."""
        client.get('/new')
        
        with flask_app.app_context():
            from app import CURRENT
            assert CURRENT['puzzle'] is not None, "Puzzle should be stored"
            assert CURRENT['solution'] is not None, "Solution should be stored"
            assert isinstance(CURRENT['puzzle'], list), "Stored puzzle should be a list"
            assert isinstance(CURRENT['solution'], list), "Stored solution should be a list"

    def test_new_game_valid_clues_parameter_types(self, client):
        """Verify new game handles various clues parameter values."""
        for clues in [20, 30, 35, 40, 50]:
            response = client.get(f'/new?clues={clues}')
            assert response.status_code == 200, f"Should handle clues={clues}"
            data = response.get_json()
            clue_count = sum(1 for row in data['puzzle'] for cell in row if cell != 0)
            assert clue_count == clues, f"Should create puzzle with {clues} clues"


class TestCheckRoute:
    """Tests for the /check route (solution validation)."""

    def test_check_requires_post(self, client):
        """Verify /check requires POST method."""
        response = client.get('/check')
        # GET requests to POST-only routes should fail
        assert response.status_code != 200, "/check should not accept GET"

    def test_check_without_active_game_returns_error(self, client):
        """Verify /check returns error when no game is in progress."""
        response = client.post('/check', json={'board': [[0]*9 for _ in range(9)]})
        assert response.status_code == 400, "Should return 400 for no active game"
        
        data = response.get_json()
        assert 'error' in data, "Error response should contain error message"

    def test_check_correct_solution_returns_empty_incorrect(self, client, flask_app):
        """Verify /check returns empty incorrect list for correct solution."""
        # Start a new game
        client.get('/new')
        
        with flask_app.app_context():
            from app import CURRENT
            correct_solution = CURRENT['solution']
        
        # Submit the correct solution
        response = client.post('/check', json={'board': correct_solution})
        assert response.status_code == 200, "Should return 200"
        
        data = response.get_json()
        assert 'incorrect' in data, "Response should contain 'incorrect' key"
        assert isinstance(data['incorrect'], list), "Incorrect should be a list"
        assert len(data['incorrect']) == 0, "Correct solution should have no incorrect cells"

    def test_check_incorrect_solution_identifies_wrong_cells(self, client, flask_app):
        """Verify /check identifies cells that don't match solution."""
        # Start a new game
        client.get('/new')
        
        with flask_app.app_context():
            from app import CURRENT
            correct_solution = CURRENT['solution']
        
        # Create incorrect board by changing one cell
        incorrect_board = [row[:] for row in correct_solution]
        incorrect_board[0][0] = (incorrect_board[0][0] % 9) + 1  # Change first cell
        
        response = client.post('/check', json={'board': incorrect_board})
        data = response.get_json()
        
        assert len(data['incorrect']) > 0, "Should identify at least one incorrect cell"
        assert [0, 0] in data['incorrect'], "Should identify position [0][0] as incorrect"

    def test_check_multiple_incorrect_cells(self, client, flask_app):
        """Verify /check identifies multiple incorrect cells."""
        # Start a new game
        client.get('/new')
        
        with flask_app.app_context():
            from app import CURRENT
            correct_solution = CURRENT['solution']
        
        # Create board with multiple changes
        incorrect_board = [row[:] for row in correct_solution]
        incorrect_board[0][0] = (incorrect_board[0][0] % 9) + 1
        incorrect_board[5][5] = (incorrect_board[5][5] % 9) + 1
        incorrect_board[8][8] = (incorrect_board[8][8] % 9) + 1
        
        response = client.post('/check', json={'board': incorrect_board})
        data = response.get_json()
        
        assert len(data['incorrect']) >= 3, "Should identify at least 3 incorrect cells"
        assert [0, 0] in data['incorrect'], "Should identify [0][0]"
        assert [5, 5] in data['incorrect'], "Should identify [5][5]"
        assert [8, 8] in data['incorrect'], "Should identify [8][8]"

    def test_check_with_partial_board_filled(self, client, flask_app):
        """Verify /check handles partially filled boards."""
        # Start a new game
        client.get('/new')
        
        with flask_app.app_context():
            from app import CURRENT
            correct_solution = CURRENT['solution']
        
        # Create partially filled board matching solution
        partial_board = [[0]*9 for _ in range(9)]
        for i in range(3):  # Fill first 3 rows
            for j in range(9):
                partial_board[i][j] = correct_solution[i][j]
        
        response = client.post('/check', json={'board': partial_board})
        data = response.get_json()
        
        # Partial board should have incorrect cells where it's 0 and solution has numbers
        incorrect_count = sum(1 for i in range(9) for j in range(9) 
                              if partial_board[i][j] != correct_solution[i][j])
        assert len(data['incorrect']) == incorrect_count, \
            "Should identify all mismatched cells"

    def test_check_response_format(self, client):
        """Verify /check response always includes 'incorrect' field."""
        # Even with an error, check response format
        response = client.post('/check', json={'board': [[0]*9 for _ in range(9)]})
        
        data = response.get_json()
        # Should have either 'error' (400) or 'incorrect' (200)
        assert 'error' in data or 'incorrect' in data, "Response should contain relevant field"


class TestGameStateManagement:
    """Tests for game state persistence across requests."""

    def test_puzzle_persists_across_requests(self, client, flask_app):
        """Verify puzzle stored after /new is available for /check."""
        # Generate a puzzle
        response1 = client.get('/new')
        puzzle_data = response1.get_json()
        
        with flask_app.app_context():
            from app import CURRENT
            stored_puzzle = CURRENT['puzzle']
        
        # Puzzle from response should match stored state
        assert puzzle_data['puzzle'] == stored_puzzle, \
            "Puzzle in response should match stored puzzle"

    def test_solution_available_for_checking(self, client, flask_app):
        """Verify solution is available after /new for use in /check."""
        # Generate a puzzle
        client.get('/new')
        
        with flask_app.app_context():
            from app import CURRENT
            solution = CURRENT['solution']
            assert solution is not None, "Solution should be stored after /new"
            assert len(solution) == 9, "Solution should have valid structure"

    def test_new_game_overwrites_previous_state(self, client, flask_app):
        """Verify calling /new multiple times updates the state."""
        # Generate first puzzle
        client.get('/new')
        with flask_app.app_context():
            from app import CURRENT
            first_solution = CURRENT['solution']
        
        # Generate second puzzle
        client.get('/new')
        with flask_app.app_context():
            from app import CURRENT
            second_solution = CURRENT['solution']
        
        # Solutions should be different (with high probability)
        assert first_solution != second_solution, \
            "New game should overwrite previous state"
