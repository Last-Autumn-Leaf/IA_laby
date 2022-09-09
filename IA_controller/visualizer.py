import pygame

from Games2D import App
from IA_controller.Helper_fun import draw_rect_alpha


class App_2 (App):
    def __init__(self,mazefile):
        super().__init__(mazefile)

    def on_render(self):
        self.maze_render()
        self.color_visited()
        self._display_surf.blit(self._image_surf, (self.player.x, self.player.y))
        pygame.display.flip()


    def color_visited(self,color=(0,255,0,70)):
        display_surf=self._display_surf
        tile_size_x = self.maze.tile_size_x
        tile_size_y = self.maze.tile_size_y
        for coord in self.visited_cases :
            i=coord[0]
            j=coord[1]
            #pygame.draw.rect(display_surf, GREEN,(j * tile_size_x, i * tile_size_y, tile_size_x, tile_size_y))
            draw_rect_alpha(display_surf, color, (j * tile_size_x, i * tile_size_y, tile_size_x, tile_size_y))

    def set_visited(self,v):
        self.visited_cases=v
