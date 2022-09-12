import pygame

from Constants import GAME_CLOCK
from Games2D import App
from IA_controller.Helper_fun import draw_rect_alpha


class App_2 (App):
    def __init__(self,mazefile):
        super().__init__(mazefile)
        self.visited_cases=[]
        self.IA_controller_X=None
        self.IA_controller_Y=None

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

    def setIA_controller(self,controllerXfun,controllerYfun):
        self.IA_controller_X=controllerXfun
        self.IA_controller_Y=controllerYfun


    def doForce_Y(self,force):
        for i in range(abs(int(force ))):

            if force > 0:
                self.on_AI_input('DOWN')
            else:
                self.on_AI_input('UP')


    def doForce_X(self,force):
        for i in range(abs(int(force ))):
            if force > 0:
                self.on_AI_input('RIGHT')
            else:
                self.on_AI_input('LEFT')
    def on_execute(self):
        self.on_init()

        while self._running:
            self._clock.tick(GAME_CLOCK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                if event.type == pygame.USEREVENT:
                    self.timer += 0.01
            pygame.event.pump()
            keys = pygame.key.get_pressed()
            self.on_keyboard_input(keys)

            #
            if self.IA_controller_X is not None:

                dG_y=self.maze.coinList[0].centery -self.player.y
                dG_x=self.maze.coinList[0].centerx -self.player.x
                dO_y=self.maze.obstacleList[0].centery - self.player.y
                dO_x=self.maze.obstacleList[0].centerx -self.player.x

                print(dG_x,dG_y)
                force_Y=self.IA_controller_Y(dG_y,dO_y)
                force_X=self.IA_controller_X(dG_x,dO_x)
                print('forceX = {} | forceY = {}'.format(force_X,force_Y))
                self.doForce_X(force_X)
                self.doForce_Y(force_Y)

            # self.on_AI_input(instruction)
            #

            if self.on_coin_collision():
                self.score += 1
            if self.on_treasure_collision():
                self.score += 10
            monster = self.on_monster_collision()
            if monster:
                if monster.fight(self.player):
                    self.maze.monsterList.remove(monster)
                else:
                    self._running = False
                    self._dead = True
            if self.on_exit():
                self._running = False
                self._win = True
            self.on_render()

        while self._win:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._win = False
            self.on_win_render()

        while self._dead:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._dead = False
            self.on_death_render()

        self.on_cleanup()
