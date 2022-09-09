from Games2D import *
from IA_controller.Helper_fun import getMonsterCoord
from IA_controller.PrologCom import PrologCom
from IA_controller.Train_genetic import genetic_train

if __name__ == '__main__':

    map_file_name='assets/test_Map'
    theAPP = App(map_file_name)

    maze=theAPP.maze.maze
    GA=genetic_train(getMonsterCoord(maze))

    prolog_com=PrologCom(maze)
    theAPP.on_execute()


