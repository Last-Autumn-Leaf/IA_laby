from Constants import MONSTER

def getMonsterCoord(maze):
    result=[]
    for i in range(len(maze)):
        for j in range(len(maze[i])):
            if maze[i][j] == MONSTER:
                result.append((i,j))
    return result