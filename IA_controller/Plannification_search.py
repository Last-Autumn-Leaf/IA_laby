from queue import Queue

from Constants import *
from IA_controller.Helper_fun import setCorrectCHWD
from IA_controller.PrologCom import PrologCom
from IA_controller.visualizer import App_2


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

def bfs_coin(depart,neighborMap, prolog_com):
    q = Queue()  # current_node,path,cost
    path=[depart]
    q.put((depart,path))
    visited = set()

    while (not q.empty()):
        current,current_path = q.get()
        visited.add(current)
        if prolog_com.GetType(coord_case = current) == 'coin':
            return True, current_path

        for neigh in neighborMap[current]:
            if neigh not in visited:
                q.put((neigh,current_path+[neigh]))

    return False, None

def planification_result():

    depart = prolog_com.getCoordFromType(START_CASE)[0]
    goal = prolog_com.getCoordFromType(EXIT)[0]
    if type(depart) ==tuple and type(goal)==tuple :
        neighbor_map = prolog_com.getNeighborsMap()
        ok, path = bfs(depart, goal, neighbor_map)

        if ok:
            theAPP.set_visited(path)
        print(path)

def start_planification_result():
    depart = prolog_com.getCoordFromType(START_CASE)[0]
    # goal = prolog_com.getCoordFromType(COIN)[0]
    if type(depart) == tuple:
        neighbor_map = prolog_com.getNeighborsMap()
        ok, path = bfs_coin(depart, neighbor_map, prolog_com)

        if ok:
            theAPP.set_visited(path)
        print(path)

if __name__ == '__main__':
    setCorrectCHWD()

    map_file_name='assets/mazeMedium_0'
    theAPP = App_2(map_file_name)
    maze=theAPP.maze.maze
    prolog_com=PrologCom(maze)

    start_planification_result()

    theAPP.on_execute()










