from render import Render
from board import Board
import curses
import pickle, bz2, json

pos_c=1
pos_l=1

r=Render()

def refresh():
    global game, r, pos_c, pos_l
    game.set_active_cell(pos_l, pos_c)
    r.render(game)
    #r.win.addstr(0,0, "Pos " + str(pos_l) + " " + str(pos_c))

def save():
    global game
    savegame = bz2.BZ2File('savegame.bin',mode='wb')
    savegame.write(pickle.dumps(game))
    savegame.close

def load():
    global game
    savegame = bz2.BZ2File('savegame.bin',mode='rb')
    game=pickle.loads(savegame.read())
    savegame.close
    refresh()

def import_game(filename="game.json"):    
    try:
        file=open(filename,"r")
        data=json.load(file)
    except:return
    finally:file.close
    game.clear_board()
    if len(data)==9:
        for l in range(1,10):
            for c in range(1,10):
                game.input_cell_value(l, c, data[l-1][c-1])
    refresh()

def export_game(filename="game.json"):
    data=[]
    for l in range(1,10):
        row=[]
        for c in range(1,10):
            row.append(game.cells[l][c].value)
        data.append(row)
    try:
        file=open(filename,"wt")
        json.dump(data, file)
    except:return
    finally:file.close

def up(i):
    global pos_l
    pos_l -= i
    if pos_l <= 0 : 
        pos_l += 9
        #left(1)
    refresh()

def down(i):
    global pos_l
    pos_l += i
    if pos_l >= 10 : 
        pos_l -=  9
        #right(1)
    refresh()

def left(i):
    global pos_c
    pos_c -= i
    if pos_c <=0 : 
        pos_c += 9
        up(1)
    refresh()

def right(i):
    global pos_c
    pos_c += i
    if pos_c >= 10: 
        pos_c -= 9
        down(1)
    refresh()

def press_number(num):
    global game, pos_l, pos_c, r
    if game.cells[pos_l][pos_c].is_static : return
    
    if not(r.hint_edit):
        game.input_cell_value(pos_l, pos_c, num)
        if num >0 : right(1)
    else:
        game.input_hint_value(pos_l, pos_c, num)
    refresh()

def switch_edit():
    global r
    r.hint_edit = not(r.hint_edit)
    refresh()

def undo():
    game.undo()
    refresh()

def redo():
    game.redo()
    refresh()

def give_hints():
    for l in range(1,10):
        for c in range(1,10):
            if game.cells[l][c].value==0:
                game.input_cell_value(l, c, game.cells[l][c].value)
                return

def parsekey(key):       
    global endgame
    if key=="\033" : endgame=True
    
    if key=="KEY_UP":up(1)
    if key=="KEY_DOWN":down(1)
    if key=="KEY_LEFT":left(1)
    if key=="KEY_RIGHT":right(1)
    if key=="CTL_UP":up(3)
    if key=="CTL_DOWN":down(3)
    if key=="CTL_LEFT":left(3)
    if key=="CTL_RIGHT":right(3)
    if key==" ":right(1)
    if key=="\n":switch_edit()
    if key=="0":press_number(0)
    if key=="1":press_number(1)
    if key=="2":press_number(2)
    if key=="3":press_number(3)
    if key=="4":press_number(4)
    if key=="5":press_number(5)
    if key=="6":press_number(6)
    if key=="7":press_number(7)
    if key=="8":press_number(8)
    if key=="9":press_number(9)
    if key=="KEY_DC":press_number(0)
    if key=="KEY_NPAGE":redo()
    if key=="KEY_PPAGE":undo()
    if key=="+":pass
    if key=="-":press_number(0)
    if key=="KEY_F(5)":save()
    if key=="KEY_F(8)":load()
    if key=="KEY_F(9)":export_game()
    if key=="KEY_F(12)":import_game()
    if key=="h":give_hints()
    #if key=="a":function1()
    #if key=="b":function2()
    #if key=="c":function3()
    #if key=="d":function4()
    #if key=="e":function5()
    #if key=="f":function6()
    #if key=="g":function7()
    #if key=="h":function8()
"""
def function1():
    game.clear_board()
    refresh()

def function2():
    game.fill()
    refresh()

def function3():
    if game.is_board_solved() : r.print_at("Solved",0,0,1)
    else: r.print_at("nope    ",0,0,1)
    refresh()

def function4():
    game.make_puzzle()
    refresh()

def function5():
    #game.convert_static()
    #game.solve()
    game.make_puzzle1()
    refresh()

def function6():
    game.generate()
    refresh()

def function7():
    game.parse_hints3()
    refresh()

def function8():
    game.parse_hints4()
    refresh()
"""

#initialize()    

game = Board()
temp = Board()

r.render(game)
refresh()

r.messagebox("generating solution")

temp.fill()
while not(temp.is_board_solved()):temp.fill()

r.messagebox("computing puzzle")
temp.make_puzzle()
game.copy_cells(temp.cells)

r.messagebox("preparing help")
temp.solve()

refresh()

endgame=False
while not(endgame):
    key=r.win.getkey()
    parsekey(key)
    if game.is_board_solved() : r.messagebox("You won")
    #r.win.addstr(0,0,key)
