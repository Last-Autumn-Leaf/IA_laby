from Games2D import *
from PrologCom import PrologCom

if __name__ == '__main__':


    theAPP = App('assets/test_Map')

    maze=theAPP.maze.maze
    prolog_com=PrologCom(maze)
    print(prolog_com.getAction(1,1))
    theAPP.on_execute()

