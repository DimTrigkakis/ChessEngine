import chess
import chess.pgn
import PIL.Image
import ImageTk
import Tkinter
import random
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

        self.myCanvas.after(5,self.draw_board)

    def play(self):
        # one move

        for move in self.trueBoard.legal_moves:
            if random.random() < 0.1:
                self.trueBoard.push_uci(str(move))
                break
        self.myCanvas.after(1,self.play)
    def main(self):

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
        self.draw_board()

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
        self.play()

        master.mainloop()

Core().main()
