import numpy as np
import pygame

from Constants import GAME_CLOCK, WHITE, GREEN
from Games2D import App
from IA_controller.Helper_fun import draw_rect_alpha


class App_2 (App):
    def __init__(self,mazefile):
        super().__init__(mazefile)
        self.visited_cases=[]
        self.IA_controller_X=None
        self.IA_controller_Y=None
        self.Fx=0
        self.Fy=0
        self.vectors_to_show=[]

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
        player_pos=(self.player.x +int(self.player.size_x/2), self.player.y+int(self.player.size_y/2))
        for (x,y) in self.vectors_to_show :
            pygame.draw.line(display_surf, WHITE, player_pos,
                         (x,y))

        pygame.draw.line(display_surf, GREEN, player_pos,(self.player.x +20*self.Fx, self.player.y+20*self.Fy))
    def set_visited(self,v):
        self.visited_cases=v

    def setIA_controller(self,controllerXfun,controllerYfun):
        self.IA_controller_X=controllerXfun
        self.IA_controller_Y=controllerYfun

    getAngle= lambda self,xa,ya,xb,yb:  np.arccos[(xa * xb + ya * yb) / (np.sqrt(xa**2 + ya**2) * np.sqrt(xb**2 + yb**2))]
    def setIA_controller_angles(self,controllerfun):
        self.IA_controller_angle=controllerfun


    def getVectors(self):
        dG_y, dG_x, dO_y, dO_x=0,0,0,0
        if self.maze.coinList :
            dG_y = self.maze.coinList[0].centery - self.player.y
            dG_x = self.maze.coinList[0].centerx - self.player.x
        if self.maze.obstacleList :
            dO_y = self.maze.obstacleList[0].centery - self.player.y
            dO_x = self.maze.obstacleList[0].centerx - self.player.x

        return dG_x,dG_y,dO_x,dO_y

    def cart2Polar(self,x,y):
        r=np.sqrt(x**2 +y**2)
        theta= np.arctan2(y,x)
        return r,theta

    def Polar2Cart(self,r,theta):
        x = r* np.cos(theta)
        y= r* np.sin(theta)

        return x,y
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

                gx= self.maze.coinList[0].centery - self.player.y
                gy= self.maze.coinList[0].centerx - self.player.x
                dO_y=self.maze.obstacleList[0].centery - self.player.y
                dO_x=self.maze.obstacleList[0].centerx -self.player.x

                print(gy, gx)
                force_Y=self.IA_controller_Y(gx, dO_y)
                force_X=self.IA_controller_X(gy, dO_x)
                print('forceX = {} | forceY = {}'.format(force_X,force_Y))
                self.doForce_X(force_X)
                self.doForce_Y(force_Y)

            if self.IA_controller_angle is not None:
                # Let's try to get the obstacles :
                # the 4 lists are [wall_list, obstacle_list, item_list, monster_list]
                percept=self.maze.make_perception_list(self.player, self._display_surf)

                self.vectors_to_show =[]
                allObs=[]
                for walls in percept[0] :
                    allObs.append((walls.centerx,walls.centery))
                for obs in percept[1] :
                    allObs.append((obs.centerx,obs.centery))

                #Should avoid monster too
                for mons in percept[3] :
                    allObs.append((mons.centerx,mons.centery))

                if len(percept[2]) ==0 :
                    #get goal from coin List or Treasure List or exit
                    if len(self.maze.coinList) >0 :
                        gx = self.maze.coinList[0].centerx
                        gy = self.maze.coinList[0].centery
                    elif len(self.maze.treasureList) >0 :
                        gx = self.maze.treasureList[0].centerx
                        gy = self.maze.treasureList[0].centery
                    else :
                        gx=self.maze.exit.centerx
                        gy=self.maze.exit.centery

                else :
                    goal = percept[2][0]
                    gy = goal.centery
                    gx = goal.centerx

                self.vectors_to_show.append((gx,gy))
                gx-= self.player.x
                gy-= self.player.y
                theta_prime=0
                rG, thethaG = self.cart2Polar(gx, gy)
                minR=np.sqrt((self.player.size_x/2)**2 +(self.player.size_y/2)**2)
                moy=0
                for (ox,oy) in allObs :
                    self.vectors_to_show.append((ox,oy))
                    ox-= self.player.x
                    oy-= self.player.y

                    rO, thethaO = self.cart2Polar(ox, oy)
                    if rO >minR :
                        theta_prime+= 3*np.pi * np.exp(-rO/1000) * self.IA_controller_angle(thethaO-thethaG)
                        moy+=1
                thethaG -= theta_prime/moy
                R = 10
                self.Fx, self.Fy = self.Polar2Cart(R, thethaG)
                self.doForce_X(self.Fx)
                self.doForce_Y(self.Fy)


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
