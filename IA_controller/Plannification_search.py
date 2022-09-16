from queue import Queue

from Constants import *
from IA_controller.Helper_fun import setCorrectCHWD, getMazeFromFile
from IA_controller.PrologCom import PrologCom
from IA_controller.visualizer import App_2
from Fuzzy_logic import FuzzPlayer


class Plannificator:

    def __init__(self,prolog_com):

        self.prolog_com=prolog_com
        self.neighborMap=prolog_com.getNeighborsMap()
        self.removedFromGoal=set()
        self.blocked_node=set()
        self.default_plan_fun=self.naivePlanification

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
                if neigh not in visited and neigh not in self.blocked_node:
                    q.put((neigh,current_path+[neigh]))

        return False, []

    def naivePlanification(self,playerPos,goal_type=['coin', 'treasure']):
        ok, path = self.bfs(playerPos, self.getGoalFun(goal_type))
        return path

    def updateBlockedList(self,remove_from_blocked):
        for node in remove_from_blocked :
            if node in self.blocked_node :
                self.blocked_node.remove(node)

if __name__ == '__main__':
    setCorrectCHWD()

    map_file_name='assets/MazeLarge_3'
    maze=getMazeFromFile(map_file_name)
    plannificator = Plannificator(PrologCom(maze))

    theAPP = App_2(mazefile=map_file_name,plannificator=plannificator)


    ### Integration de fuzzy ###
    tile_size = (theAPP.maze.tile_size_x, theAPP.maze.tile_size_y)
    fuzz_ctrl = FuzzPlayer(tile_size)
    theAPP.setFuzzCtrl(fuzz_ctrl)
    ### --- ###

    theAPP.on_execute()

