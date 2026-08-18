# Sudoku Project Instructions

## Project Overview

This project is a Sudoku game built with Python Flask, HTML, CSS, and JavaScript.

The goal is to modernize the legacy Sudoku application while keeping the existing functionality stable and improving usability, accessibility, maintainability, and user experience.

## Code Structure

- Flask backend code belongs in `starter/app.py`.
- Sudoku generation and validation logic belongs in `starter/sudoku_logic.py`.
- HTML templates belong in `starter/templates/`.
- JavaScript functionality belongs in `starter/static/main.js`.
- CSS styling belongs in `starter/static/styles.css`.
- Automated tests belong in the `starter/` test files.

## Backend Guidelines

- Use clear and maintainable Python code.
- Keep Sudoku generation and validation logic separate from Flask route handling.
- Sudoku puzzles must be valid and have exactly one solution.
- Handle invalid requests gracefully.
- Preserve existing API behavior unless a change is required by the project specification.
- Avoid unnecessary global state changes.
- Use meaningful function and variable names.

## Sudoku Rules

- The board must contain 9 rows and 9 columns.
- Each row must contain numbers 1 through 9 without duplicates.
- Each column must contain numbers 1 through 9 without duplicates.
- Each 3x3 block must contain numbers 1 through 9 without duplicates.
- Generated puzzles must have exactly one valid solution.
- Puzzle generation must support Easy, Medium, and Hard difficulty levels.

## Frontend Guidelines

- Use semantic HTML where practical.
- Keep JavaScript modular and readable.
- Use event delegation where appropriate for Sudoku board interactions.
- Provide immediate feedback for invalid user input.
- Prevent users from modifying pre-filled puzzle cells.
- Keep the timer accurate and stop it when the puzzle is correctly completed.
- Hints must be clearly distinguishable from normal user-entered values.
- Display the number of hints used.
- Provide clear completion feedback.

## Accessibility and Responsive Design

- The application must work on desktop and mobile screen sizes.
- Buttons and controls must remain usable on small screens.
- Text must remain readable in light and dark modes.
- Use sufficient color contrast.
- Do not rely only on color to communicate important information.
- Avoid layout shifts when users interact with the Sudoku board.
- The 3x3 Sudoku blocks should have alternating visual backgrounds to make the groups easy to distinguish.

## Leaderboard

- Store the Top 10 scores using browser localStorage.
- Each score should include:
  - Player name
  - Time taken
  - Hints used
  - Difficulty
- Keep only the best 10 scores.
- Display the leaderboard clearly.

## Testing

- Preserve existing tests unless they are outdated because of an intentional specification change.
- Run the complete pytest suite after significant changes.
- Do not consider a feature complete until its behavior has been tested.
- When changing functionality, add or update tests where appropriate.

## GitHub Copilot Usage

When using GitHub Copilot:

1. Understand the existing code before modifying it.
2. Ask Copilot for focused changes instead of unnecessary rewrites.
3. Review generated code before accepting it.
4. Verify Copilot suggestions against the project requirements.
5. Modify or reject suggestions when they are incorrect, inefficient, or unsuitable.
6. Run tests after accepting significant changes.
7. Prefer simple, maintainable solutions over unnecessary complexity.

## Change Guidelines

- Do not introduce unnecessary dependencies.
- Do not remove existing functionality without a clear reason.
- Keep changes focused on the project requirements.
- Maintain compatibility with the existing Flask application.
- Use comments only where they provide useful context.