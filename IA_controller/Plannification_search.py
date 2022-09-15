from queue import Queue

from Constants import *
from IA_controller.Helper_fun import setCorrectCHWD
from IA_controller.PrologCom import PrologCom
from IA_controller.visualizer import App_2
from Fuzzy_logic import FuzzPlayer


class Plannificator:

    def __init__(self,prolog_com):

        self.prolog_com=prolog_com
        self.neighborMap=prolog_com.getNeighborsMap()
        self.removedFromGoal=set()

    def getGoalFun(self,goal_type=['coin', 'treasure']):
        if type(goal_type) == list:
            return lambda coord: self.prolog_com.GetType(coord) in goal_type
        else:
            return lambda coord: self.prolog_com.GetType(coord) == goal_type

    def bfs(self,depart,goal_function):
        q = Queue()  # current_node,path,cost
        path=[depart]
        q.put((depart,path))
        visited = set()

        while (not q.empty()):
            current,current_path = q.get()
            visited.add(current)
            if current not in self.removedFromGoal and goal_function(current) :
                return True, current_path

            for neigh in self.neighborMap[current]:
                if neigh not in visited:
                    q.put((neigh,current_path+[neigh]))

        return False, []

    def naivePlanification(self,playerPos,goal_type=['coin', 'treasure']):
        ok, path = self.bfs(playerPos, self.getGoalFun(goal_type))
        return path


if __name__ == '__main__':
    setCorrectCHWD()

    map_file_name='assets/MazeLarge_2'
    theAPP = App_2(map_file_name)
    maze=theAPP.maze.maze

    plannificator = Plannificator(PrologCom(maze))
    #theAPP.setGoalTypes(['coin','treasure','exit'])
    theAPP.setPlanFun(plannificator.naivePlanification)
    theAPP.setPlannificator(plannificator)

    ### Integration de fuzzy ###
    tile_size = (theAPP.maze.tile_size_x, theAPP.maze.tile_size_y)
    fuzz_ctrl = FuzzPlayer(tile_size)
    theAPP.setFuzzCtrl(fuzz_ctrl)
    ### --- ###

    theAPP.on_execute()










