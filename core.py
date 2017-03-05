import chess
import chess.pgn
import chess.polyglot
import PIL.Image
import ImageTk
import Tkinter
import random
import functools

class Core():

    myCanvas = None
    trueBoard = None
    w,h = 600,600
    border = 5
    border_width = 20
    pieces = [] # images for pieces
    piece_image_labels = ["b","k","n","p","q","r"]
    piece_names = ["b","k","n","p","q","r","B","K","N","P","Q","R"]

    coord = [2.5*border,2.5*border]
    size = (600.0-38)/8
    timer = 5
    move_timer = 20
    max_depth = 2

    def canvas_coordinates(self,i,j):
        return i+self.coord[0]+self.size/2+(self.size-1)*i,j+self.coord[1]+self.size/2+(self.size-1)*j

    def draw_board(self):

        self.myCanvas.delete("all")
        self.myCanvas.create_rectangle(self.border_width-2.5*self.border, self.border_width-2.5*self.border, 600-self.border_width, 600-self.border_width, fill="black")

        colors = ["#ba8146","#eec59b"]
        for g in range(64):
            self.myCanvas.create_rectangle(self.coord[0]+self.size*(g%8),self.coord[1]+self.size*(g/8),self.coord[0]+self.size*(g%8+1),self.coord[1]+self.size*(g/8+1),fill=colors[(g%8+g/8) % 2])

        position = self.trueBoard.board_fen()
        k = 0
        for i,p in enumerate(position):
            if p != "/" and not p.isdigit():
                self.myCanvas.create_image(*self.canvas_coordinates(k % 8,k / 8),image=self.pieces[self.piece_names.index(p)])
                k += 1
            else:
                if p.isdigit():
                    k += int(p)
                continue
        self.myCanvas.after(self.timer,self.draw_board)

    def value(self,piece_type):
        if piece_type == 1:
            return 1
        if piece_type < 4:
            return 3
        if piece_type < 5:
            return 5
        return 9

    value_type = [0, 1, 3, 3, 5, 9]
    piece_types = [1, 2, 3, 4, 5]
    def play(self, someBoard, depth = 0,alpha = -2000,beta = +2000): # Returns ((move eval, move),alpha, beta)
        turn = someBoard.turn
        legal_moves = someBoard.legal_moves
        my_moves = list(legal_moves)
        random.shuffle(my_moves)

        # If this is the first move we are asked to make, use the book
        if depth == 0:
            weight_max = None
            move = None
            with chess.polyglot.open_reader("./gm2001.bin") as reader:
                for entry in reader.find_all(someBoard):
                    if weight_max == None:
                        weight_max = entry.weight
                        move=entry.move()
                    elif entry.weight > weight_max:
                        weight_max = entry.weight
                        move = entry.move
                if move != None:
                    return ((0,move),alpha,beta)

        # If this condition hits, we can end the game
        cond = someBoard.can_claim_threefold_repetition() or someBoard.can_claim_fifty_moves() or someBoard.is_stalemate() or someBoard.is_insufficient_material()
        if cond:
            return ((0, None), alpha, beta)
        elif someBoard.is_game_over():
            if turn:
                return ((-1000, None), alpha, beta)
            return ((1000, None), alpha, beta)

        possible_moves = []
        if depth == self.max_depth:
            if turn:
                for move in my_moves:
                    if alpha >= beta:
                        return ((1000,None),alpha,beta)
                    someBoard.push_uci(str(move))
                    value = sum([(len(someBoard.pieces(piece_type,True))-len(someBoard.pieces(piece_type,False)))*self.value_type[piece_type] for piece_type in self.piece_types])
                    someBoard.pop()
                    if value > alpha:
                        alpha = value
                    possible_moves.append((value,move))
                best_move = max(possible_moves)
            else:
                for move in my_moves:
                    if alpha >= beta:
                        return ((-1000,None),alpha,beta)
                    someBoard.push_uci(str(move))
                    value = sum([(len(someBoard.pieces(piece_type,True))-len(someBoard.pieces(piece_type,False)))*self.value_type[piece_type] for piece_type in self.piece_types])
                    someBoard.pop()
                    if value < beta:
                        beta = value
                    possible_moves.append((value,move))
                best_move = min(possible_moves)
            return (best_move,alpha,beta)
        else:
            for move in my_moves:
                someBoard.push_uci(str(move))
                next_move = self.play(someBoard,depth+1,alpha,beta)

                value = next_move[0][0]
                if turn:
                    if value > alpha:
                        alpha = value
                else:
                    if value < beta:
                        beta = value

                if turn:
                    if alpha >= beta:
                        someBoard.pop()
                        return ((1000, None), alpha, beta)
                else:
                    if alpha >= beta:
                        someBoard.pop()
                        return ((-1000, None), alpha, beta)

                possible_moves.append((value,move))
                someBoard.pop()

            if turn:
                return (max(possible_moves),alpha,beta)
            return (min(possible_moves),alpha,beta)

    def play_move(self,initBoard):

        cond = initBoard.can_claim_threefold_repetition() or initBoard.can_claim_fifty_moves() or initBoard.is_stalemate() or initBoard.is_insufficient_material()
        if cond:
            print "DRAW"
        move = self.play(initBoard)[0]
        if cond:
            print "DRAW"
        elif initBoard.is_game_over():
            if initBoard.turn:
                print "WHITE WAS CHECKMATED"
            else:
                print "BLACK WAS CHECKMATED"
        else:
            initBoard.push_uci(str(move[1]))
            self.myCanvas.after(self.move_timer, self.play_move, initBoard)

    def pause(self, event):
        import time
        time.sleep(10000)
    def main(self):

        random.seed(116)
        aboard = chess.Board()
        self.trueBoard = aboard
        # Initialize pieces

        master = Tkinter.Tk()
        frame = Tkinter.Frame(master, width=self.w, height=self.h,bd=self.border, relief=Tkinter.RAISED)
        frame.pack()

        for color in ["black","white"]:
            for name in self.piece_image_labels:
                img = PIL.Image.open("./img/"+color+name+".png")
                self.pieces.append(ImageTk.PhotoImage(img))

        self.myCanvas = Tkinter.Canvas(frame, width=self.w,height=self.h)
        self.myCanvas.pack()
        self.myCanvas.after(self.timer,self.draw_board)
        self.myCanvas.bind("<Button-1>", self.pause)

        # get screen width and height
        ws = master.winfo_screenwidth() # width of the screen
        hs = master.winfo_screenheight() # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (self.w/2)
        y = (hs/2) - (self.h/2)

        # set the dimensions of the screen
        # and where it is placed
        master.geometry('%dx%d+%d+%d' % (self.w, self.h, x, y))

        move_length = len(aboard.legal_moves)
        self.myCanvas.after(self.move_timer,self.play_move,self.trueBoard)

        master.mainloop()

Core().main()
