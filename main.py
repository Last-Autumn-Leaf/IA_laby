from IA_controller.Fuzzy_logic import FuzzPlayer
from IA_controller.Helper_fun import getMazeFromFile
from IA_controller.Plannification_search import Plannificator
from IA_controller.PrologCom import PrologCom
from IA_controller.visualizer import App_2

if __name__ == '__main__':

    map_file_name = 'assets/MazeLarge_3'
    maze = getMazeFromFile(map_file_name)
    plannificator = Plannificator(PrologCom(maze))

    theAPP = App_2(mazefile=map_file_name, plannificator=plannificator)

    ### Integration de fuzzy ###
    tile_size = (theAPP.maze.tile_size_x, theAPP.maze.tile_size_y)
    fuzz_ctrl = FuzzPlayer(tile_size)
    theAPP.setFuzzCtrl(fuzz_ctrl)
    ### --- ###

    theAPP.on_execute()
