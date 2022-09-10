import os
from queue import Queue
import pathlib

from IA_controller.Helper_fun import setCorrectCHWD
from IA_controller.PrologCom import PrologCom
from IA_controller.visualizer import App_2
from  Constants import  *


def bfs(depart,goal,neighborMap):
    q = Queue()  # current_node,path,cost
    path=[depart]
    q.put((depart,path))
    visited = set()

    while (not q.empty()):
        current,current_path = q.get()
        visited.add(current)
        if current == goal:
            return True, current_path

        for neigh in neighborMap[current]:
            if neigh not in visited:
                q.put((neigh,current_path+[neigh]))

    return False, None

def planification_result():

    depart = prolog_com.getCoordFromType(START_CASE)[0]
    goal = prolog_com.getCoordFromType(EXIT)[0]
    neighbor_map = prolog_com.getNeighborsMap()

    ok, path = bfs(depart, goal, neighbor_map)

    if ok:
        theAPP.set_visited(path)
    print(path)

if __name__ == '__main__':
    setCorrectCHWD()

    map_file_name='assets/test_Map'
    theAPP = App_2(map_file_name)
    maze=theAPP.maze.maze
    prolog_com=PrologCom(maze)

    planification_result()

    theAPP.on_execute()










