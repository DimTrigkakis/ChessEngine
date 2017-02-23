import chess
import chess.pgn
import PIL.Image
import TkImage
import Tkinter

class Core():

    myCanvas = None
    w,h = 600,600
    border = 5

    def draw_board(self,board):
        border_width = 20
        self.myCanvas.create_rectangle(border_width-2.5*self.border, border_width-2.5*self.border, 600-border_width, 600-border_width, fill="black")

        coord = [2.5*self.border,2.5*self.border]
        size = (600.0-38)/8
        color1 ="#ba8146"
        color2 ="#eec59b"
        for i in range(8):
            for j in range(8):
                    color = color1
                    if (i+j) % 2 == 0:
                        color = color2
                    self.myCanvas.create_rectangle(coord[0]+size*i,coord[1]+size*j,coord[0]+size*(i+1),coord[1]+size*(j+1),fill=color)


        img = PIL.Image.open("./img/blackr.png")
        tk_img = ImageTk.PhotoImage(img)
        self.myCanvas.create_image(250, 250,image=tk_img)


    def main(self):

        aboard = chess.Board()

        master = Tkinter.Tk()
        frame = Tkinter.Frame(master, width=self.w, height=self.h,bd=self.border, relief=Tkinter.RAISED)
        frame.pack()

        self.myCanvas = Tkinter.Canvas(frame, width=self.w,height=self.h)
        self.myCanvas.pack()
        self.draw_board(aboard)

        # get screen width and height
        ws = master.winfo_screenwidth() # width of the screen
        hs = master.winfo_screenheight() # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (self.w/2)
        y = (hs/2) - (self.h/2)

        # set the dimensions of the screen
        # and where it is placed
        master.geometry('%dx%d+%d+%d' % (self.w, self.h, x, y))

        master.mainloop()

Core().main()
