from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'difficulty': None,
    'clues': None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    # Get difficulty from query parameter, default to 'medium' for backward compatibility
    difficulty = request.args.get('difficulty', sudoku_logic.DEFAULT_DIFFICULTY)
    
    # Also accept 'clues' parameter for direct clue count specification
    # (for backward compatibility with existing tests/usage)
    if 'clues' in request.args:
        clues = int(request.args.get('clues'))
    else:
        clues = sudoku_logic.get_clues_for_difficulty(difficulty)
    
    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['difficulty'] = difficulty if 'difficulty' in request.args else None
    CURRENT['clues'] = clues
    return jsonify({'puzzle': puzzle})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})

@app.route('/hint')
def get_hint():
    """
    Provide a hint by returning the correct value for one empty cell.
    Returns the row, column, and value.
    Returns 400 if no empty cells are available.
    """
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    
    if puzzle is None or solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    
    # Find the first empty cell in the puzzle
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if puzzle[i][j] == 0:  # Empty cell (EMPTY = 0)
                # Return the correct value from the solution
                correct_value = solution[i][j]
                # Also update the puzzle to mark this cell as no longer empty
                # This prevents the same cell from being hinted twice
                puzzle[i][j] = correct_value
                return jsonify({
                    'row': i,
                    'col': j,
                    'value': correct_value
                })
    
    # No empty cells found
    return jsonify({'error': 'No empty cells to hint'}), 400

if __name__ == '__main__':
    app.run(debug=True)