let board;
let game = new Chess();
var whiteSquareGrey = "#a9a9a9";
var blackSquareGrey = "#696969";
let pendingPromotion = null;
let isChess960 = false;

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function initBoard() {
    var config = {
        draggable: true,
        position: "start",
        onDragStart: onDragStart,
        onDrop: handleMove,
        onMouseoutSquare: onMouseoutSquare,
        onMouseoverSquare: onMouseoverSquare,
        onSnapEnd: onSnapEnd,
        pieceTheme: "/static/img/pieces/{piece}.png"
    };
    board = ChessBoard("board", config);
}

$("#eloSlider").on("input", function() {
    const elo = $(this).val();
    $("#eloValue").text(elo);
    
    $.ajax({
        url: "/set_elo",
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify({ elo: parseInt(elo) })
    });
});

function removeGreySquares () {
    $("#board .square-55d63").css("background", "");
}
  
function greySquare (square) {
    var $square = $("#board .square-" + square);
  
    var background = whiteSquareGrey;
    if ($square.hasClass("black-3c85d")) {
        background = blackSquareGrey;
    }
  
    $square.css("background", background);
}
  
function onDragStart (source, piece) {
    // do not pick up pieces if the game is over
    if (game.game_over()) return false;
  
    // or if it's not that side's turn
    if ((game.turn() === "w" && piece.search(/^b/) !== -1) ||
        (game.turn() === "b" && piece.search(/^w/) !== -1)) {
        return false;
    }
}
  
function onMouseoverSquare (square, piece) {
    // get list of possible moves for this square
    var moves = game.moves({
        square: square,
        verbose: true
    });
  
    // exit if there are no moves available for this square
    if (moves.length === 0) return;
  
    // highlight the square they moused over
    greySquare(square);
  
    // highlight the possible squares for this piece
    for (var i = 0; i < moves.length; i++) {
        greySquare(moves[i].to);
    }
}
  
function onMouseoutSquare (square, piece) {
    removeGreySquares();
}
  
function onSnapEnd () {
    board.position(game.fen());
    if (pendingPromotion) {
        showPromotionModal(pendingPromotion.source, pendingPromotion.target);
    }
}

function showLoading() {
    const loader = document.getElementById('loading-container');
    loader.style.display = 'flex';
}

function hideLoading() {
    const loader = document.getElementById('loading-container');
    loader.style.display = 'none';
}

async function submitMove(move) {
    showLoading();

    try {
        let uci = move.from + move.to;
        if (move.promotion) {
            uci += move.promotion.toLowerCase();
        }

        const response = await $.ajax({
            url: "/make_move",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ move: uci })
        });
        console.log(response);

        hideLoading();
        
        game.load(response.fen);
        board.position(response.fen);
        updateMoves(response.moves);

        if (response.top_3_moves) {
            top3Moves = response.top_3_moves
            let top3Html = "<h3>Top 3 moves:</h3>";
            for (let i = 0; i < top3Moves.length; i += 1) {
                top3Html += `<div>${top3Moves[i][0]} | ${top3Moves[i][1]}</div>`;
            }
            $("#bestDiv").html(top3Html);
        }

        if (response.eval_text) {
            evalText = response.eval_text
            let evalHtml = `<h3>Evaluation:</h3><div>${evalText}</div>`;
            $("#evalDiv").html(evalHtml);
        }
        
        if (response.status === "end") {
            await sleep(200);
            if (response.winner === false) {
                alert("You LOSE!");
            } else if (response.winner === true) {
                alert("You WIN!");
            } else {
                alert("DRAW!");
            }
        }
    } catch (error) {
        console.error("Error:", error);
    }
}

async function handleMove(source, target) {
    removeGreySquares();
    
    let move = game.move({
        from: source,
        to: target,
        promotion: "q"
    });
    console.log(move);
    if (move === null) return "snapback";
    if (move.flags.includes("p")) {
        pendingPromotion = { source, target, color: move.color };
        game.undo();
        return "snapback";
    }
    
    submitMove(move);
}

async function showPromotionModal(source, target) {
    $("#promotionModal").show();
    const color = pendingPromotion.color === 'w' ? 'w' : 'b';

    $(".promotion-piece").each(function() {
        const piece = $(this).data("piece");
        $(this).text(color === 'w' ? piece.toUpperCase() : piece.toLowerCase());
    });
    
    return new Promise((resolve) => {
        $(".promotion-piece").off("click").on("click", function() {
            const piece = $(this).data("piece");
            $("#promotionModal").hide();
            
            // make the promoted move
            let move = game.move({
                from: source,
                to: target,
                promotion: piece
            });
            console.log(move, source, target, piece);
            console.log(game);
            // board.position(game.fen());
            pendingPromotion = null;
            
            submitMove(move);
            resolve();
        });
    });
}

$(".close").click(function() {
    $("#promotionModal").hide();
    pendingPromotion = null;
});

function updateMoves(moves) {
    let movesHtml = "<b>Moves:</b>";
    for (let i = 0; i < moves.length; i += 2) {
        movesHtml += `<div>${(i/2 + 1)}. ${moves[i]} ${moves[i+1] || ""}</div>`;
    }
    $("#moves").html(movesHtml);
    $("#moves").scrollTop(function() { return this.scrollHeight; });
}

async function undoMove() {
    try {
        const response = await $.ajax({
            url: "/undo",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({})
        });
        
        if (response.status === "ok") {
            game.load(response.fen);
            board.position(response.fen);
            updateMoves(response.moves);
        } else {
            alert(response.message || "Couldn't undo move");
        }
    } catch (error) {
        console.error("Undo error:", error);
        alert(error.responseJSON?.message || "Error processing undo");
    }
}

async function redoMove() {
    try {
        const response = await $.ajax({
            url: "/redo",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({})
        });
        
        if (response.status === "ok") {
            game.load(response.fen);
            board.position(response.fen);
            updateMoves(response.moves);
        } else {
            alert(response.message || "Couldn't redo move");
        }
    } catch (error) {
        console.error("Redo error:", error);
        alert(error.responseJSON?.message || "Error processing redo");
    }
}

function showBestMoves() {
    let element = document.getElementById("bestDiv");
    element.style.display = element.style.display === "none" ? "block" : "none";

    let button = document.getElementById("bestButton");
    button.textContent = `${button.textContent === "Show Best Moves" ? "Hide Best Moves" : "Show Best Moves"}`;
}

function showEval() {
    let element = document.getElementById("evalDiv");
    element.style.display = element.style.display === "none" ? "block" : "none";

    let button = document.getElementById("evalButton");
    button.textContent = `${button.textContent === "Show Evaluation" ? "Hide Evaluation" : "Show Evaluation"}`;
}

function toggleMode() {
    isChess960 = !isChess960;
    updateModeButtonAndHeader();
}

function updateModeButtonAndHeader() {
    const button = document.getElementById("modeToggle");
    button.textContent = `${isChess960 ? "Switch to Standard Chess" : "Switch to Chess960"}`;

    const header = document.getElementById("mode");
    header.innerText = `${isChess960 ? "Chess960" : "Standard Chess"}`;

    newGame();
}

async function newGame() {
    const response = await $.get(`/new_game?chess960=${isChess960}`);
    game = new Chess(response.initial_fen);
    board.position(response.initial_fen);
    $("#moves").html("<b>Moves:</b>");
}

$(document).ready(function () {
    initBoard();
    newGame();
    updateModeButtonAndHeader();
});