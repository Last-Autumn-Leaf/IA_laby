from Games2D import *

if __name__ == '__main__':


    theAPP = App('assets/test_Map')

    maze=theAPP.maze.maze
    prologfile_name='prolog/map'
    prolog_file=open(prologfile_name,'w')
    for i in range(len(maze)):
        for j in range(len(maze[i])):
            current=maze[i][j]
            prolog_file.write('{}({},{}).\t\t'.format(prolog_dict[current],i,j))
        prolog_file.write('\n')
    prolog_file.close()
    #['prolog/map'].

    theAPP.on_execute()

