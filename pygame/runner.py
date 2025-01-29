import pygame
import sys
from main import *

DEPTH = 4

buttons = []
pygame.font.init()
my_font = pygame.font.SysFont('Arial', 70)
class Button:
    def __init__(self, x, y, width, height, buttonText='Button', onclickFunction=None, onePress=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.onclickFunction = onclickFunction
        self.onePress = onePress

        self.fillColors = {
            'normal': '#ffffff',
            'hover': '#666666',
            'pressed': '#333333',
        }

        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.buttonSurf = my_font.render(buttonText, True, (20, 20, 20))

        self.alreadyPressed = False

        buttons.append(self)

    def process(self):

        mousePos = pygame.mouse.get_pos()
        
        self.buttonSurface.fill(self.fillColors['normal'])
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])

            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])

                if self.onePress:
                    self.onclickFunction()

                elif not self.alreadyPressed:
                    self.onclickFunction()
                    self.alreadyPressed = True

            else:
                self.alreadyPressed = False

        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width/2 - self.buttonSurf.get_rect().width/2,
            self.buttonRect.height/2 - self.buttonSurf.get_rect().height/2
        ])
        screen.blit(self.buttonSurface, self.buttonRect)


class Piece:
    def __init__(self, color, x, y, piece_type):
        self.color = color
        self.x = x
        self.y = y
        self.type = piece_type

    def draw(self, surface):
        img = pygame.image.load(f"images/pieces/{self.color}_{self.type}.png")
        surface.blit(img, (self.x*75, self.y*75))

class Hint:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type

    def draw(self, screen):
        if self.type == "move":
            pygame.draw.circle(screen, (200, 200, 200, 2), (self.x*75+58, self.y*75+58), 10)
        elif self.type == "capture":
            pygame.draw.circle(screen, (200, 200, 200, 2), (self.x*75+58, self.y*75+58), 37, 7)
        # img = pygame.image.load(f"images/hints/{self.type}.png")
        # surface.blit(img, (self.x*75, self.y*75))

class Highlight:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), (self.x*75+20, self.y*75+20, 75, 75)) # or board

hints = []
# set up the pieces
pieces = []
for i in range(8):
    pieces.append(Piece("b", i, 1, "pawn"))
    pieces.append(Piece("w", i, 6, "pawn"))

pieces.append(Piece("b", 0, 0, "rook"))
pieces.append(Piece("w", 0, 7, "rook"))
pieces.append(Piece("b", 7, 0, "rook"))
pieces.append(Piece("w", 7, 7, "rook"))

pieces.append(Piece("b", 1, 0, "knight"))
pieces.append(Piece("w", 1, 7, "knight"))
pieces.append(Piece("b", 6, 0, "knight"))
pieces.append(Piece("w", 6, 7, "knight"))

pieces.append(Piece("b", 2, 0, "bishop"))
pieces.append(Piece("w", 2, 7, "bishop"))
pieces.append(Piece("b", 5, 0, "bishop"))
pieces.append(Piece("w", 5, 7, "bishop"))

pieces.append(Piece("b", 3, 0, "queen"))
pieces.append(Piece("w", 3, 7, "queen"))

pieces.append(Piece("b", 4, 0, "king"))
pieces.append(Piece("w", 4, 7, "king"))

pygame.init()

# set up the window
size = (840, 640)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Chess")

# set up the board
board = pygame.Surface((600, 600), pygame.SRCALPHA)
board.fill((133, 104, 80))

# draw the board
for x in range(0, 8, 2):
    for y in range(0, 8, 2):
        pygame.draw.rect(board, (193, 171, 140), (x*75, y*75, 75, 75))
        pygame.draw.rect(board, (193, 171, 140), ((x+1)*75, (y+1)*75, 75, 75))

# draw the pieces
for piece in pieces:
    piece.draw(board)

# add the board to the screen
screen.blit(board, (20, 20))

pygame.display.flip()

second = False
fr = None
to = None
x_fr = None
y_fr = None

b = initial_state()
highlights = []

move_stack = []
def prev():
    if len(b.move_stack) != 0:
        print("test")
        move_stack.append(b.pop())

def next():
    if len(move_stack) != 0:
        b.push(move_stack.pop())

back_button = Button(630, 20, 95, 100, '<', prev)
next_button = Button(735, 20, 95, 100, '>', next)

# main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            # get the position of the click
            pos = pygame.mouse.get_pos()

            # convert the position to board coordinates
            x = (pos[0] - 20) // 75
            y = (pos[1] - 20) // 75

            if 0 <= x <= 7 and 0 <= y <= 7:
                if not second:
                    highlights = []
                    highlights.append(Highlight(x, y))
                    for highlight in highlights:
                        print("answer:", highlight.x, highlight.y)
                    fr = 63 - (y+1)*8 + (x+1)
                    x_fr = x
                    y_fr = y
                    hints = []
                    for move in actions(b):
                        from_sq = chess.parse_square(move.uci()[0:2])
                        from_sq_x = from_sq % 8
                        from_sq_y = 7 - (from_sq // 8)
                        to_sq = chess.parse_square(move.uci()[2:4])
                        to_sq_x = to_sq % 8
                        to_sq_y = 7 - (to_sq // 8)
                        if fr == from_sq:
                            if b.piece_at(to_sq):
                                hints.append(Hint(to_sq_x, to_sq_y, "capture"))
                            else:
                                hints.append(Hint(to_sq_x, to_sq_y, "move"))

                else:
                    hints = []
                    print(x_fr, y_fr, x, y)
                    to = 63 - (y+1)*8 + (x+1)
                    if ((to < 8 and not b.turn) or (to > 55 and b.turn)) and b.piece_at(fr).piece_type == chess.PAWN:
                        my_move = chess.Move(fr, to, chess.QUEEN)
                    else:
                        my_move = chess.Move(fr, to)

                    #from_square = Highlight(x_fr, y_fr)
                    print(my_move)
                    #print(actions(b))
                    if my_move in actions(b):
                        for piece in pieces:
                            if piece.x == x_fr and piece.y == y_fr:
                                piece.x = x
                                piece.y = y
                        b = result(b, my_move)
                        #print(b)
                        if not b.is_game_over():
                            board.fill((133, 104, 80))
                            for x in range(0, 8, 2):
                                for y in range(0, 8, 2):
                                    pygame.draw.rect(board, (193, 171, 140), (x*75, y*75, 75, 75))
                                    pygame.draw.rect(board, (193, 171, 140), ((x+1)*75, (y+1)*75, 75, 75))

                            pieces = []
                            for i in range(64):
                                piece = b.piece_at(i)
                                if piece:
                                    name = chess.piece_name(piece.piece_type)
                                    colour = "bw"[piece.color]
                                    pieces.append(Piece(colour, i % 8, 7 - (i // 8), name))

                            # for highlight in highlights:
                            #     highlight.draw(screen)
                            for piece in pieces:
                                piece.draw(board)
                            screen.blit(board, (20, 20))
                            for hint in hints:
                                hint.draw(screen)
                            for button in buttons:
                                button.process()
                            # update the display
                            pygame.display.flip()
                            minimax_eval, best_move = minimax(b, DEPTH, -math.inf, math.inf)
                            #print("best move:", best_move)
                            b = result(b, best_move)
                            
                            from_sq = chess.parse_square(best_move.uci()[0:2])
                            from_sq_x = from_sq % 8
                            from_sq_y = 7 - (from_sq // 8)
                            to_sq = chess.parse_square(best_move.uci()[2:4])
                            to_sq_x = to_sq % 8
                            to_sq_y = 7 - (to_sq // 8)
                            for piece in pieces:
                                if piece.x == from_sq_x and piece.y == from_sq_y:
                                    piece.x = to_sq_x
                                    piece.y = to_sq_y
                            #print(evaluation(b))
                    # print("best move:", best_move)
                    # print("eval:", minimax_eval)
                second = not second

    # redraw the board and pieces
    board.fill((133, 104, 80))
    for x in range(0, 8, 2):
        for y in range(0, 8, 2):
            pygame.draw.rect(board, (193, 171, 140), (x*75, y*75, 75, 75))
            pygame.draw.rect(board, (193, 171, 140), ((x+1)*75, (y+1)*75, 75, 75))

    pieces = []
    for i in range(64):
        piece = b.piece_at(i)
        if piece:
            name = chess.piece_name(piece.piece_type)
            colour = "bw"[piece.color]
            pieces.append(Piece(colour, i % 8, 7 - (i // 8), name))
    
    # for highlight in highlights:
    #     highlight.draw(screen)
    for piece in pieces:
        piece.draw(board)
    screen.blit(board, (20, 20))
    for hint in hints:
        hint.draw(screen)
    for button in buttons:
        button.process()
    # update the display
    pygame.display.flip()

    if b.is_game_over():
        print(b.outcome())