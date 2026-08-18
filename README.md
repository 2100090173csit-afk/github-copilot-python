# Refactor a Sudoku Game written in Python Flask

Use this simple Sudoku game as a starting point to practice your skills with GitHub Copilot. The goal is to refactor the code, add new features, improve maintainability, and enhance the overall user experience.

## Getting Started

Follow these instructions to run the Sudoku game locally.

### Dependencies

- Python 3
- Modern web browser (Chrome, Firefox, Edge, etc.)

### Installation

1. Clone the repository:

```bash
git clone <your-repository-url>
cd github-copilot-python
```

2. Create a Python virtual environment (recommended):

```bash
python -m venv .venv
```

3. Activate the virtual environment.

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

4. Install the required packages:

```bash
pip install -r starter/requirements.txt
```

### Run the Application

From the project root, run:

```bash
python starter/app.py
```

Open the application in your browser:

```text
http://127.0.0.1:5000
```

## Testing

The project includes an automated test suite covering Sudoku logic and Flask application behavior.

Run all tests from the project root:

```bash
pytest -q
```

The current test suite contains **45 tests** covering:

- Sudoku board creation and validation
- Sudoku solution generation
- Solution counting
- Unique puzzle generation
- Different clue counts
- Puzzle generation performance
- Flask routes
- New game functionality
- Puzzle state management
- Solution checking
- Invalid input handling

Current test result:

```text
45 passed
```

For detailed test documentation, see [TEST_DOCUMENTATION.md](starter/TEST_DOCUMENTATION.md).

## Project Instructions

Use GitHub Copilot to refactor the code for this game to add more advanced features. The goal is to create a more modern and maintainable codebase and add additional functionality to the final product. You can use any combination of code completion and chat features, like Ask, Edit, or Agent modes.

- Errors should be handled gracefully with appropriate messages to the user.
- Implement a Sudoku board generator that creates a valid Sudoku puzzle with a unique solution.
- Add a timer to track how long it takes to solve the puzzle.
- Implement a solution checker that verifies if the user's solution is correct using event delegation.
- Add a difficulty selector to allow users to choose between easy, medium, and hard puzzles.
- Add a hint feature that provides clues for the user that are noted with unique colors.
- Add a check puzzle button that checks the current state of the board against the solution.
- User should get immediate feedback on their input, such as highlighting invalid entries.
- Top 10 scores should be saved in local storage and displayed on the page with the user's name, time taken, hints used, and difficulty level.
- The game should be responsive and work well on both desktop and mobile devices.
- UI colors should be visually appealing and accessible.
- Completed and correct puzzles should display a congratulatory message with the time taken and hints used and ask for the user's name for Top 10 times.