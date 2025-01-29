from flask import Flask, render_template, request, session, jsonify
import chess
from stockfish import Stockfish
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

stockfish = Stockfish(path="stockfish-ubuntu-x86-64-vnni512")
stockfish.set_depth(10)
stockfish.set_elo_rating(1500)

def get_board():
    if "board" not in session:
        session["board"] = chess.Board().fen()
    return chess.Board(session["board"])

def save_board(board):
    session["board"] = board.fen()
    if "moves" not in session:
        session["moves"] = []
        
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/new_game")
def new_game():
    board = chess.Board()
    save_board(board)
    session["moves"] = []
    return jsonify(status="ok")

@app.route("/make_move", methods=["POST"])
def make_move():
    try:
        board = get_board()
        data = request.json
        move = data["move"]

        if "=" in move:
            move = move.replace("=", "")
        
        try:
            print(move)
            chess_move = board.parse_san(move)
            # print("good")
        except Exception as e:
            print(e)
            return jsonify(status="error", message="Invalid move format")
            
        if chess_move not in board.legal_moves:
            return jsonify(status="error", message="Illegal move")

        board.push(chess_move)
        session["moves"].append(move)

        if board.outcome():
            print(board.outcome().termination)
            return jsonify(status="end",
                           fen=board.fen(),
                           moves=session["moves"],
                           winner=board.outcome().winner)

        # get stockfish move
        # print(stockfish.get_parameters())
        stockfish.set_fen_position(board.fen())
        engine_move = stockfish.get_best_move()
        engine_move_san = board.san(chess.Move.from_uci(engine_move))
        board.push_uci(engine_move)
        session["moves"].append(engine_move_san)
        # print(session)
        if board.outcome():
            return jsonify(status="end",
                           fen=board.fen(),
                           last_move=engine_move_san,
                           moves=session["moves"],
                           winner=board.outcome().winner)
        
        save_board(board)
        return jsonify(status="ok",
                       fen=board.fen(),
                       last_move=engine_move_san,
                       moves=session["moves"])

    except Exception as e:
        return jsonify(status="error", message=str(e))

@app.route("/set_elo", methods=["POST"])
def set_elo():
    elo = int(request.json["elo"])
    stockfish.set_elo_rating(elo)
    return jsonify(status="ok")

if __name__ == "__main__":
    app.run(debug=True)