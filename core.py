import chess
import chess.pgn
import chess.polyglot
import PIL.Image
import ImageTk
import Tkinter
import random
import time
import math
import functools
import chess.syzygy

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
    timer = 100
    move_timer = 1 # Unneeded now
    plies = 4
    max_depth = plies - 1 # The maximum depth already produces all possible moves for the last player before evaluating so it adds another ply.
    # If ply = 1, then max_depth is 0 and there is move generation and evaluation only for the first move

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
        self.myCanvas.\
            after(self.timer,self.draw_board)

    def value(self,piece_type):
        if piece_type == 1:
            return 1
        if piece_type < 4:
            return 3
        if piece_type < 5:
            return 5
        return 9

    value_type = [1, 3, 3, 5, 9]
    value_type_2 = [0,1, 3, 3, 5, 9]
    piece_types = [1, 2, 3, 4, 5]

    add0 = 0
    add1 = 0
    add2 = 0
    add3 = 0
    add33 = 0
    add4 = 0
    addadd = 0

    value_dict = {"p":-1,"P":1,None:0,"r":-5,"R":5,"b":-3,"B":3,"n":-3,"N":3,"q":-9,"Q":9,"k":0,"K":0}

    def evaluate_complex(self,someBoard):
        return ((bin(someBoard.pieces(1,True)).count("1")-bin(someBoard.pieces(1,False)).count("1"))*self.value_type[0]+
        (bin(someBoard.pieces(2,True)).count("1")-bin(someBoard.pieces(2,False)).count("1"))*self.value_type[1]+
        (bin(someBoard.pieces(3,True)).count("1")-bin(someBoard.pieces(3,False)).count("1"))*self.value_type[2]+
        (bin(someBoard.pieces(4,True)).count("1")-bin(someBoard.pieces(4,False)).count("1"))*self.value_type[3]+
        (bin(someBoard.pieces(5,True)).count("1")-bin(someBoard.pieces(5,False)).count("1"))*self.value_type[4])

    def evaluate(self,someBoard):
        return sum([(len(someBoard.pieces(piece_type,True))-len(someBoard.pieces(piece_type,False)))*self.value_type_2[piece_type] for piece_type in self.piece_types])

    def value_of(self,square,aboard):

        a = aboard.piece_at(square)
        if a != None:
            return self.value_dict[a.symbol()]
        return 0

    def eval_move(self,move,aboard):

        value_of_attacker = self.value_of(move.from_square,aboard)
        value_of_defender = self.value_of(move.to_square,aboard)
        #print move, value_of_attacker, value_of_defender

        c = 0
        if not aboard.turn:
            return value_of_attacker-value_of_defender+random.randint(-c,c)
        else:
            return -value_of_attacker+value_of_defender+random.randint(-c,c)

        return random.random()
        #return +value_of_attacker-value_of_defender

    def play(self, someBoard, depth = 0,alpha = -2000,beta = +2000,evaluator=None): # Returns ((move eval, move),alpha, beta)

        a = time.time()
        turn = someBoard.turn
        legal_moves = someBoard.generate_legal_moves()
        self.add0 += time.time()-a

        # If this is the first move we are asked to make, use the book
        a = time.time()
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
                    self.add1 += time.time()-a
                    return ((0,move),alpha,beta)
        self.add1 += time.time()-a
        a = time.time()

        # If this condition hits, we can end the game
        if someBoard.is_game_over():
            if turn:
                self.add2 += time.time()-a
                return ((-1000, None), alpha, beta)
            self.add2 += time.time()-a
            return ((1000, None), alpha, beta)
        if someBoard.is_stalemate():
            self.add2 += time.time()-a
            return ((0, None), alpha, beta)
        if someBoard.is_seventyfive_moves():

            self.add2 += time.time()-a
            return ((0, None), alpha, beta)
        if someBoard.is_insufficient_material():
            self.add2 += time.time()-a
            return ((0, None), alpha, beta)
        if someBoard.is_fivefold_repetition():
            self.add2 += time.time()-a
            return ((0, None), alpha, beta)
        self.add2 += time.time()-a
        a = time.time()

        if turn:
            best_move = (-3001,None)
            if depth == self.max_depth:
                for move in legal_moves:
                    if alpha >= beta:
                        self.add3 += time.time()-a
                        return ((1000,None),alpha,beta)
                    someBoard.push_uci(str(move))
                    value = evaluator(someBoard)
                    someBoard.pop()
                    if value > alpha:
                        alpha = value
                    if value > best_move[0]:
                        best_move = (value,move)
                self.add33 += time.time()-a
                return (best_move,alpha,beta)
            else:
                for move in legal_moves:
                    someBoard.push_uci(str(move))
                    next_move = self.play(someBoard,depth+1,alpha,beta,evaluator)
                    a = time.time()

                    value = next_move[0][0]
                    if value > alpha:
                        alpha = value

                    if alpha >= beta:
                        someBoard.pop()
                        self.add4 += time.time()-a
                        return ((1000, None), alpha, beta)

                    if value > best_move[0]:
                        best_move = (value,move)

                    someBoard.pop()
                self.add4 += time.time()-a
                return (best_move,alpha,beta)
        else:
            best_move = (3001,None)
            if depth == self.max_depth:
                for move in legal_moves:
                    if alpha >= beta:
                        self.add3 += time.time()-a
                        return ((-1000,None),alpha,beta)
                    someBoard.push_uci(str(move))
                    value = evaluator(someBoard)
                    someBoard.pop()
                    if value < beta:
                        beta = value
                    if value < best_move[0]:
                        best_move = (value,move)
                self.add3 += time.time()-a
                return (best_move,alpha,beta)
            else:
                for move in legal_moves:
                    someBoard.push_uci(str(move))
                    next_move = self.play(someBoard,depth+1,alpha,beta,evaluator=evaluator)
                    a = time.time()

                    value = next_move[0][0]
                    if value < beta:
                        beta = value

                    if alpha >= beta:
                        someBoard.pop()
                        self.add4 += time.time()-a
                        return ((-1000, None), alpha, beta)
                    if value < best_move[0]:
                        best_move = (value,move)

                    someBoard.pop()

                self.add4 += time.time()-a
                return (best_move,alpha,beta)

    # MONTRE CARLO TREE SEARCH
    def expand_node(self,node,someBoard):
        # given a node, expand a random child
        # the Board is already in the given position, push the child move
        child = [None,[],0,0,node]
        node[1].append(child)

        legal_moves =list(someBoard.legal_moves)
        random.shuffle(legal_moves)

        my_move = legal_moves[0]
        child[0] = my_move
        someBoard.push(my_move)

        return child

    def simulate(self,node,someBoard):
        # update node statistics based on a random playout on someBoard

        # Assume playout has happened
        # we have someBoard, do a minimax with depth 2 on it to get the value of the position

        #true_depth = 1
        #value = self.play(someBoard,depth=self.max_depth-true_depth,evaluator=self.evaluate_complex)[0][0]
        move_counter = 0
        while True:
            moves = list(someBoard.generate_legal_moves())
            random.shuffle(moves)

            if random.random() > 0.9:
                value = self.evaluate_complex(someBoard=someBoard)
                for i in range(move_counter):
                    someBoard.pop()

                #value = self.evaluate_complex(someBoard)

                if value < -100:
                    return 0
                if value > 100:
                    return 1
                return 1/(1.0+math.exp(-value)) # fixes the range to [0,1]'''


            cond = someBoard.is_seventyfive_moves() or someBoard.is_fivefold_repetition() or someBoard.is_stalemate() or someBoard.is_insufficient_material()
            if cond:
                for i in range(move_counter):
                    someBoard.pop()
                return 0.5

            if someBoard.is_game_over():
                if someBoard.turn: #white was checkmated
                    for i in range(move_counter):
                        someBoard.pop()
                    return 0
                else:
                    for i in range(move_counter):
                        someBoard.pop()
                    return 1

            someBoard.push_uci(str(moves[0]))
            move_counter += 1

        '''value = self.evaluate_complex(someBoard=someBoard)
        for i in range(move_counter):
            someBoard.pop()

        #value = self.evaluate_complex(someBoard)

        if value < -100:
            return 0
        if value > 100:
            return 1
        return 1/(1.0+math.exp(-value)) # fixes the range to [0,1]'''

    # things to do

    # A) Create a printing function for the entire tree, maybe import some python module for it
    # B) Create a random simulation
    # C) Using A and B, fix all bugs and make sure the algorithm works
    # D) Make sure the algorith gives a reasonable response after 10 seconds
    # E) Fix the simulation, by augmenting it.
    # F) Deal with trap states, from the paper that you will read

    def print_tree(self,tree_root):
        print tree_root
        for child in tree_root[1]:
            print "\t",
            if child != None and child != []:
                self.print_tree(child)


    def select_node(self,someBoard,node,jpop=0):
        if node[3] == 0:
            return node
        for child in node[1]:
            if child[3] == 0:
                return child
        score = 0
        result = node
        for child in node[1]:
                new_score = child[2]+math.sqrt(2*math.log(child[3])/(1.0*node[3]))
                if new_score > score:
                    score = new_score
                    result = child
        return self.select_node(someBoard,result)


    def NOTFULLYEXPANDED(self,node,someBoard):
        if len(node[5]) == 0:
            return False
        return True

    def NONTERMINAL(self,someBoard):
        cond = someBoard.is_seventyfive_moves() or someBoard.is_fivefold_repetition() or someBoard.is_stalemate() or someBoard.is_insufficient_material()
        if cond:
            return False

        if someBoard.is_game_over():
            return False
        return True

    def EXPAND(self,node,someBoard):
        action = random.choice(node[5])
        node[5].remove(action)
        child = [action,[],0,0,node,list(someBoard.generate_legal_moves())]
        node[1].append(child)

        return child


    def BESTCHILD(self,node,c):
        children = [(child[2]-c*math.sqrt(2*math.log(child[3])/(1.0*node[3])),child) for child in node[1]]
        return max(children)[1]

    def DEFAULTPOLICY(self,someBoard,maximizer=True): # Most simulations end up at 0.5
        # Let's fix that
        counter = 0
        '''while self.NONTERMINAL(someBoard):
            actions = list(someBoard.generate_legal_moves())
            action = random.choice(actions)
            someBoard.push_uci(str(action))
            counter += 1'''

        j_choice = random.randint(5,30) # 5/10, 2/4
        value_add = 0
        for j in range(j_choice):
            for i in range(random.randint(2,4)):
                actions = list(someBoard.generate_legal_moves())
                if actions != []:
                    action = random.choice(actions)
                    someBoard.push_uci(str(action))
                    counter += 1
            if maximizer:
                value_add += self.evaluate_complex(someBoard)
            else:
                value_add -= self.evaluate_complex(someBoard)
            for k in range(counter):
                someBoard.pop()
            counter = 0
        value_add /= j_choice


        '''if not maximizer:
            value_add *= -1'''
        if value_add > 100:
            return 1,counter
        if value_add < -100:
            return 0,counter
        return 1/(1.0+math.exp(-value_add)),counter

        cond = someBoard.is_seventyfive_moves() or someBoard.is_fivefold_repetition() or someBoard.is_stalemate() or someBoard.is_insufficient_material()
        if cond:
            return 0.5, counter

        if someBoard.is_game_over():
            if someBoard.turn: #white was checkmated
                return 0, counter
            else:
                return 1, counter

    def BACKUP(self,node,D):
        while node is not None:
            node[3] += 1
            node[2] += D
            node = node[4]


    def debug(self,object):
        print str(object)
    def TREEPOLICY(self,node,someBoard):

        move_counter = 0
        while self.NONTERMINAL(someBoard):
            if self.NOTFULLYEXPANDED(node,someBoard):
                node = self.EXPAND(node,someBoard)
                someBoard.push_uci(str(node[0]))
                move_counter += 1
                return node, move_counter
            else:
                node = self.BESTCHILD(node,math.sqrt(2))
        return node, move_counter


    def count_tree(self,node):
        print 1,
        if len(node[1]) > 0:
            print "[",
        for n in node[1]:
            self.count_tree(n)
        if len(node[1]) > 0:
            print "]",
    def play_mc(self, someBoard):
        turn = someBoard.turn
        starting_node = [None,[],0,0,None,list(someBoard.generate_legal_moves())] # move, children, successes, tries, parent, untried_actions
        # CREATE A NODE IN THE TREE - this can be repeated many times
        time_start = time.time()
        simulate = 0

        maximizer = someBoard.turn
        while time_start - time.time() > -3:

            simulate += 1
            node, counter = self.TREEPOLICY(starting_node,someBoard)
            D, counter2 = self.DEFAULTPOLICY(someBoard,maximizer=maximizer)
            self.BACKUP(node,D)
            for i in range(counter+counter2):
                someBoard.pop()

        self.count_tree(starting_node)

        return self.BESTCHILD(starting_node,0)[0]

    '''
            # Print tree for this experiment
            self.print_tree(self.monte_carlo_tree_root[0])

            node = self.select_node(someBoard,self.monte_carlo_tree_root[0])
            node = self.expand_node(node,someBoard)
            value = self.simulate(node,someBoard)
            # These statistics are backpropagated
            print value

            while node[4] != None:
                node[2] += value
                node[3] += 1
                node = node[4]
            print "MYNODE",node
            node[2] += value
            node[3] += 1
            print "MYNODE",node

            # After statistics have been updated, pop the number of moves used
            someBoard.pop() # you pushed a move to expand the node, pop it
            while j_pop > 0:
                j_pop -= 1
                someBoard.pop() # pop all the moves in children

        self.print_tree(self.monte_carlo_tree_root[0])
        children_top = []
        print "Simulations",simulate
        print self.monte_carlo_tree_root[0]
        for child in self.monte_carlo_tree_root[0][1]:
            print self.monte_carlo_tree_root[0][3]

            children_top.append((child[2]-math.sqrt(2*math.log(child[3])/(1.0*self.monte_carlo_tree_root[0][3])),child[0]))
        print children_top
        # return most secure child (lowest UCB bound is highest)

        return max(children_top)[1]'''


    def play_move(self,initBoard):

        cond = initBoard.is_seventyfive_moves() or initBoard.is_fivefold_repetition() or initBoard.is_stalemate() or initBoard.is_insufficient_material()
        if cond:
            print "DRAW"
        move = self.play(initBoard, evaluator=self.evaluate_complex)[0]
        if cond:
            print "DRAW"
        elif initBoard.is_game_over():
            if initBoard.turn:
                print "WHITE WAS CHECKMATED"
            else:
                print "BLACK WAS CHECKMATED"
        else:
            initBoard.push_uci(str(move[1]))
            #self.myCanvas.after(self.move_timer, self.play_move, initBoard)


    monte_carlo_tree_root = None
    def play_move_mc(self,initBoard):

        cond = initBoard.is_seventyfive_moves() or initBoard.is_fivefold_repetition() or initBoard.is_stalemate() or initBoard.is_insufficient_material()
        if cond:
            print "DRAW"
        move = self.play_mc(initBoard)
        if cond:
            print "DRAW"
        elif initBoard.is_game_over():
            if initBoard.turn:
                print "WHITE WAS CHECKMATED"
            else:
                print "BLACK WAS CHECKMATED"
        else:
            initBoard.push_uci(str(move))
            #self.myCanvas.after(self.move_timer, self.play_move, initBoard)


    def mm1(self):
        aboard = self.trueBoard
        atime = time.time()
        self.add0 = 0
        self.add1 = 0
        self.add2 = 0
        self.add3 = 0
        self.add33 = 0
        self.add4 = 0
        self.addadd = 0
        self.play_move(aboard)
        print self.add0," ____ ",self.add1," ____ ",self.add2," ____ ",self.add3," and ", self.add33," ____ ",self.add4," add: ",self.addadd, sum((self.add0,self.add1,self.add2,self.add3,self.add4))
        print "Time for minimax move:",time.time()-atime

    def mc1(self):
        aboard = self.trueBoard
        atime = time.time()
        self.play_move_mc(aboard)
        print "Time for mcts move:",time.time()-atime

    endgame_database = None
    def main(self):

        #self.endgame_database = chess.syzygy.open_tablebases(directory="./endgame.md5", load_wdl=True)
        random.seed(116)
        aboard = chess.Board()
        self.trueBoard = aboard
        # Initialize pieces

        master = Tkinter.Tk()
        frame = Tkinter.Frame(master, width=self.w, height=self.h,bd=self.border, relief=Tkinter.RAISED)
        frame.grid()
        frame2 = Tkinter.Frame(master, width=self.w+15, height=100,bd=self.border, relief=Tkinter.RAISED)
        frame2.grid()
        frame2.grid_propagate(False)

        label = Tkinter.Button(frame2,text="MinMax",command=self.mm1,width=8,height=3)
        label.grid(column=0,row=0,padx=5,pady=5)
        label = Tkinter.Button(frame2,text="MCTS",command=self.mc1,width=8,height=3)
        label.grid(column=1,row=0,padx=5,pady=5)
        for color in ["black","white"]:
            for name in self.piece_image_labels:
                img = PIL.Image.open("./img/"+color+name+".png")
                self.pieces.append(ImageTk.PhotoImage(img))

        self.myCanvas = Tkinter.Canvas(frame, width=self.w,height=self.h)
        self.myCanvas.pack()
        self.myCanvas.after(self.timer,self.draw_board)
        #self.myCanvas.bind("<Button-1>", self.pause)

        # get screen width and height
        ws = master.winfo_screenwidth() # width of the screen
        hs = master.winfo_screenheight() # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (self.w/2)
        y = (hs/2) - ((self.h+85)/2)

        # set the dimensions of the screen
        # and where it is placed
        master.geometry('%dx%d+%d+%d' % (self.w, self.h+85, x, y))

        for i in range(30):
            self.play_move(aboard)
        move_length = len(aboard.legal_moves)
        #self.myCanvas.after(self.move_timer,self.play_move,self.trueBoard)

        master.mainloop()

Core().main()
