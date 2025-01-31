from flask import Flask, render_template, request, session, jsonify
import chess
from stockfish import Stockfish
import os
import random

app = Flask(__name__)
app.secret_key = os.urandom(24)

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
    chess960 = request.args.get("chess960", "true") == "true"
    session["chess960"] = chess960
    if chess960:
        position_id = random.randint(0, 959)
        board = chess.Board.from_chess960_pos(position_id)
    else:
        board = chess.Board()
    save_board(board)
    session["initial_fen"] = board.fen()
    session["moves"] = []
    session["undone_moves"] = []
    session["elo"] = 1500

    return jsonify(
        status="ok",
        initial_fen=board.fen()
    )

@app.route("/make_move", methods=["POST"])
def make_move():
    try:
        if "undone_moves" in session:
            session["undone_moves"] = []
            
        board = get_board()
        data = request.json
        move = data["move"]

        try:
            chess_move = chess.Move.from_uci(move)
        except ValueError:
            return jsonify(status="error", message="Invalid UCI format")
            
        if chess_move not in board.legal_moves:
            return jsonify(status="error", message="Illegal move")

        move_san = board.san(chess_move)
        board.push(chess_move)
        session["moves"].append(move_san)

        print(chess_move)
        if board.outcome():
            print(board.outcome().termination)
            return jsonify(status="end",
                           fen=board.fen(),
                           moves=session["moves"],
                           winner=board.outcome().winner)

        # get stockfish move
        stockfish = Stockfish(path="./stockfish-ubuntu-x86-64-vnni512", parameters={
            "UCI_LimitStrength": "true",
            "UCI_Chess960": "true" if session.get("chess960", True) else "false"
        })
        stockfish.set_depth(10)
        stockfish.set_elo_rating(session["elo"])

        stockfish.set_fen_position(board.fen())
        engine_move = stockfish.get_best_move_time(50)
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

        # get top 3 moves by stockfish + evaluation
        new_board = get_board()
        stockfish.set_fen_position(new_board.fen())
        stockfish.update_engine_parameters({"Hash": 256, "Skill Level": 20, "UCI_LimitStrength": "false"})
        top_3_moves = stockfish.get_top_moves(3)
        evaluation = stockfish.get_evaluation()
        print(top_3_moves, evaluation)

        top_3_moves_list = []
        eval_text = ""

        for move in top_3_moves:
            move_san = new_board.san(chess.Move.from_uci(move["Move"]))
            text = ""
            if move["Centipawn"]:
                centipawn = round(move["Centipawn"]/100, 1)
                if centipawn > 0:
                    text = f"+{centipawn} for White"
                elif centipawn < 0:
                    text = f"{centipawn} for Black"
                else:
                    text = f"{centipawn} (Balanced)"
            elif move["Mate"]:
                mate = move["Mate"]
                if mate > 0:
                    text = f"Mate in {mate} for White"
                else:
                    text = f"Mate in {-mate} for Black"
            
            top_3_moves_list.append((move_san, text))
        
        if evaluation["type"] == "cp":
            centipawn = round(evaluation["value"]/100, 1)
            if centipawn > 0:
                eval_text = f"+{centipawn} for White"
            elif centipawn < 0:
                eval_text = f"{centipawn} for Black"
            else:
                eval_text = f"{centipawn} (Balanced)"
        elif evaluation["type"] == "mate":
            mate = evaluation["value"]
            if mate > 0:
                eval_text = f"Mate in {mate} for White"
            else:
                eval_text = f"Mate in {-mate} for Black"
        
        return jsonify(status="ok",
                       fen=board.fen(),
                       last_move=engine_move_san,
                       moves=session["moves"],
                       top_3_moves=top_3_moves_list,
                       eval_text=eval_text)

    except Exception as e:
        print(e)
        return jsonify(status="error", message=str(e))

@app.route("/set_elo", methods=["POST"])
def set_elo():
    elo = int(request.json["elo"])
    session["elo"] = elo
    return jsonify(status="ok")

@app.route("/undo", methods=["POST"])
def undo_move():
    try:
        if "moves" not in session or len(session["moves"]) < 2:
            return jsonify(status="error", message="No moves to undo")

        undone_moves = session.get("undone_moves", [])
        undone_moves.append(session["moves"][-2:])
        session["undone_moves"] = undone_moves

        new_moves = session["moves"][:-2]
        board = rebuild_board_from_moves(new_moves)
        
        session["board"] = board.fen()
        session["moves"] = new_moves
        
        return jsonify(
            status="ok",
            fen=board.fen(),
            moves=new_moves
        )

    except Exception as e:
        return jsonify(status="error", message=str(e))

@app.route("/redo", methods=["POST"])
def redo_move():
    try:
        if "undone_moves" not in session or len(session["undone_moves"]) == 0:
            return jsonify(status="error", message="No moves to redo")

        move_pair = session["undone_moves"].pop()
        new_moves = session["moves"] + move_pair
        
        board = rebuild_board_from_moves(new_moves)
        
        session["board"] = board.fen()
        session["moves"] = new_moves
        session["undone_moves"] = session["undone_moves"]
        
        return jsonify(
            status="ok",
            fen=board.fen(),
            moves=new_moves
        )

    except Exception as e:
        return jsonify(status="error", message=str(e))

def rebuild_board_from_moves(moves):
    board = chess.Board(fen=session["initial_fen"])
    for move_san in moves:
        if "=" in move_san:
            move_san = move_san.replace("=", "")
        move = board.parse_san(move_san)
        board.push(move)
    return board

if __name__ == "__main__":
    app.run(debug=True)

def create_app():
    return app