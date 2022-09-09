import csv
import os
import pathlib
import pygame
from Constants import MONSTER

def setCorrectCHWD():
    if pathlib.Path.cwd().name=="IA_controller" :
        parent_path=pathlib.Path.cwd().parents[0]
        print("setting chwd to:",parent_path)
        os.chdir(parent_path)
def getMazeFromFile(filename='assets/mazeMedium_0'):
    maze = []
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            maze.append(row)
    return maze


def getMonsterCoord(maze):
    result=[]
    for i in range(len(maze)):
        for j in range(len(maze[i])):
            if maze[i][j] == MONSTER:
                result.append((i,j))
    return result


def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)

#For contouring
#pygame.draw.rect(display_surf, WHITE, (j * tile_size_x, i * tile_size_y, tile_size_x, tile_size_y), 1)

if __name__ == '__main__':
    setCorrectCHWD()


