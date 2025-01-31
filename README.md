# Chess with Stockfish

![demo](https://cloud-3i8kiyekj-hack-club-bot.vercel.app/0demo.png)

---

## Overview

This project is a web-based chess platform where you can play against the powerful Stockfish engine in both standard chess and Chess960 (Fischer Random) modes. Customise the engine's strength, undo/redo moves, view top engine suggestions, and analyse positions in real time. It's perfect for honing your skills or experimenting with unconventional starting positions.

Key features include adjustable Stockfish ELO (1350–3000), move history tracking, promotion handling, and evaluation displays. Whether you're a beginner or an advanced player, this tool adapts to your skill level while providing deep strategic insights.

## Features

### 1. **Play Against Stockfish**
Challenge the renowned Stockfish engine with adjustable difficulty. Choose between **Standard Chess** or **Chess960** for varied gameplay.

### 2. **Customisable Engine Strength**
Adjust Stockfish's skill level using a slider (1350–3000 ELO) to match your proficiency.

### 3. **Undo/Redo Moves**
Correct mistakes or explore alternate lines with unlimited undo/redo functionality.

### 4. **Best Moves & Evaluation**
View Stockfish's top three recommended moves and real-time position evaluations.

### 5. **Chess960 Mode**
Play Fischer Random chess with randomised starting positions to test your adaptability.

### 6. **Move List**
Track all moves in a scrollable history.

## Future Improvements

### 1. **Multiplayer Mode**
Add support for human vs. human matches locally or online.

### 2. **Analysis Mode**
Allow users to analyse past games with engine feedback, displaying accuracy scores and move evaluations.

### 3. **Opening Book Integration**
Include an opening explorer for educational insights.

### 4. **Mobile Optimisation**
Improve responsiveness for seamless play on smartphones and tablets.

## Demo

Check out the live demo: [Chess Demo](https://chess.mengshin.me)

## Running the Website

1. Clone this repository and navigate to the project directory.

2. Install the required dependencies:
   ```bash
   pip install Flask chess stockfish
   ```

3. Start the Flask application:
   ```bash
   flask run
   ```

4. Visit `http://localhost:5000` to play!

## Technologies Used

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python with Flask
- **Libraries:** `python-chess`, `stockfish`, `chessboard.js`, `chess.js`

## Credits

1. **python-chess Documentation**
2. **Stockfish Documentation**
3. **chessboard.js Documentation**
4. **chess.js Documentation**
5. **Stack Overflow**
6. **ChatGPT**

(Note: Some parts of this project were adapted from the aforementioned documentation, and ChatGPT was used for structuring and refining this README.)