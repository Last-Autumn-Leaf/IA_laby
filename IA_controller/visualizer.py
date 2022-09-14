import numpy as np
import pygame

from Constants import GAME_CLOCK, WHITE, GREEN, BLUE, PERCEPTION_RADIUS
from Games2D import App
from IA_controller.Helper_fun import draw_rect_alpha


class App_2 (App):
    def __init__(self,mazefile):
        super().__init__(mazefile)
        self.visited_cases=[]
        self.IA_controller_X=None
        self.IA_controller_Y=None
        self.IA_controller_angle=None
        self.Fx=0
        self.Fy=0
        self.vectors_to_show=[]
        self.path_to_show=None
        self.path_to_cross = None
        self.goalTypes=['coin','treasure','exit']
        self.old_pos=(0,0)
        self.new_pos=(0,0)
        self.old_theta_prime=0
        self.FOLLOW_MOUSE=False
        self.on_init()
        self.current_player_case = self.getPlayerCoord()


    def on_render(self):
        self.maze_render()
        self.color_test()
        self.color_render()
        self._display_surf.blit(self._image_surf, (self.player.x, self.player.y))
        pygame.display.flip()

    def color_render(self,color=(0,255,0,70)):
        display_surf=self._display_surf
        player_pos=self.player.get_rect().center
        for (x,y) in self.vectors_to_show :
            pygame.draw.line(display_surf, WHITE, player_pos,
                         (x,y))

        pygame.draw.rect(display_surf,GREEN,(self.player.x,self.player.y, self.player.size_x,self.player.size_y),width=3)
        # draw dmin not usefull
        #pygame.draw.circle(display_surf,GREEN,player_pos,self.dmin,width=3)
        #Draw current dirrection
        pygame.draw.line(display_surf, GREEN, player_pos,(player_pos[0] + int(50*self.Fx), player_pos[1] + int(50*self.Fy)))

    def color_test(self,color=(0,255,0,70)):
        display_surf = self._display_surf
        tile_size_x = self.maze.tile_size_x
        tile_size_y = self.maze.tile_size_y
        if self.path_to_cross is not None :
            for coord in self.path_to_cross:
                i=coord[0]
                j=coord[1]
                #pygame.draw.rect(display_surf, GREEN,(j * tile_size_x, i * tile_size_y, tile_size_x, tile_size_y))
                draw_rect_alpha(display_surf, color, (j * tile_size_x, i * tile_size_y, tile_size_x, tile_size_y))

    def getPlayerCoord(self):
        # coordonates are reversed !!!
        x,y = self.player.get_rect().center
        x=int(x / self.maze.tile_size_x)
        y=int(y / self.maze.tile_size_y)
        return (y,x)


    def setShowPathFun(self,getPathFun):
        self.path_to_show=getPathFun
    def setGoalTypes(self,goalTypes):
        self.goalTypes=goalTypes

    def setIA_controller(self,controllerXfun,controllerYfun):
        self.IA_controller_X=controllerXfun
        self.IA_controller_Y=controllerYfun

    getRadius = lambda self,size : np.sqrt(  size[0]**2 + size[1]**2  )
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
        force = force / 100
        if force <0 :
            force =np.floor(force)
        else :
            force=np.ceil(force)
        force=int(force)
        for i in range(abs(force )):

            if force > 0:
                self.on_AI_input('DOWN')
            else:
                self.on_AI_input('UP')
    def doForce_X(self,force):
        force = force/100
        if force <0 :
            force = np.floor(force)
        else :
            force= np.ceil(force)
        force=int(force)
        for i in range(abs(force)):
            if force > 0:
                self.on_AI_input('RIGHT')
            else:
                self.on_AI_input('LEFT')

    getVitesse = lambda self : np.sqrt((self.new_pos[0]-self.old_pos[0])**2+ (self.new_pos[1]-self.old_pos[1])**2)

    def ChangeCaseDetector(self):

        if self.current_player_case != self.getPlayerCoord():
            self.current_player_case = self.getPlayerCoord()
            return True
        else:
            return False


    def getSmallest_distance_rects(self,rect1,rect2):
        dist = lambda p1,p2 : np.sqrt((p1[0]-p2[0])**2+ (p1[1]-p2[1])**2)

        if rect1 is None :
            return PERCEPTION_RADIUS * self.getRadius((self.maze.tile_size_x, self.maze.tile_size_y))

        (x1, y1)=rect1.topleft
        (x1b, y1b)=rect1.bottomright
        (x2, y2)=rect2.topleft
        (x2b, y2b)=rect2.bottomright

        left = x2b < x1
        right = x1b < x2
        bottom = y2b < y1
        top = y1b < y2
        if top and left:
            return dist((x1, y1b), (x2b, y2))
        elif left and bottom:
            return dist((x1, y1), (x2b, y2b))
        elif bottom and right:
            return dist((x1b, y1), (x2, y2b))
        elif right and top:
            return dist((x1b, y1b), (x2, y2))
        elif left:
            return x1 - x2b
        elif right:
            return x2 - x1b
        elif bottom:
            return y1 - y2b
        elif top:
            return y2 - y1b
        else:  # rectangles intersect
            return 0.




    def on_execute(self):

        #self.path_to_cross = self.path_to_show(self.getPlayerCoord(), self.goalTypes)

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
                    allObs.append((walls.centerx,walls.centery,walls))
                for obs in percept[1] :
                    allObs.append((obs.centerx,obs.centery,obs))

                #Should avoid monster too
                for mons in percept[3] :
                    allObs.append((mons.centerx,mons.centery,mons))

                if len(percept[2]) ==0 :
                    #get goal from coin List or Treasure List or exit
                    if len(self.maze.coinList) >0 :
                        gx = self.maze.coinList[0].centerx
                        gy = self.maze.coinList[0].centery

                        # case_goal = self.path_to_cross[self.path_to_cross.index(self.getPlayerCoord())+1]
                        # gx = (case_goal[1] + 0.5) * self.maze.tile_size_x
                        # gy = (case_goal[0] + 0.5) * self.maze.tile_size_y
                        # print('x_goal = {} | y_goal = {}'.format(gx,gy))
                    elif len(self.maze.treasureList) >0 :
                        gx = self.maze.treasureList[0].centerx
                        gy = self.maze.treasureList[0].centery

                        # case_goal = self.path_to_cross[self.path_to_cross.index(self.getPlayerCoord()) + 1]
                        # gx = (case_goal[1] + 0.5) * self.maze.tile_size_x
                        # gy = (case_goal[0] + 0.5) * self.maze.tile_size_y
                    elif self.maze.exit :
                        gx=self.maze.exit.centerx
                        gy=self.maze.exit.centery

                    if self.FOLLOW_MOUSE:
                        gx, gy = pygame.mouse.get_pos()

                else :
                    goal = percept[2][0]
                    gy = goal.centery
                    gx = goal.centerx

                self.vectors_to_show.append((gx,gy))
                player_pos=self.player.get_rect().center
                gx-= player_pos[0]
                gy-= player_pos[1]
                theta_prime=0.0


                rG, thethaG = self.cart2Polar(gx, gy)

                if not allObs :
                    allObs.append((-gx,-gy,None))
                alldev=[]
                for (ox,oy,oObject) in allObs :
                    self.vectors_to_show.append((ox,oy))
                    #vecteur obstacle joueur
                    ox-= player_pos[0]
                    oy-= player_pos[1]
                    rO, thethaO = self.cart2Polar(ox, oy)

                    rO=self.getSmallest_distance_rects(oObject,self.player.get_rect())

                    theta_prime=self.IA_controller_angle(thethaO-thethaG,rO)

                    alldev.append(theta_prime)


                def getAbsMax(a):
                    abs_max=a[0]
                    for i in a  :
                        if abs(abs_max) < abs(i) :
                            abs_max=i
                    return abs_max

                theta_prime =getAbsMax(alldev)
                thethaG += theta_prime

                R = 2
                self.Fx, self.Fy = self.Polar2Cart(R, thethaG)
                self.doForce_X(self.Fx)
                self.doForce_Y(self.Fy)


                self.new_pos=self.player.get_position()


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

            '''if self.ChangeCaseDetector():
                self.path_to_cross = self.path_to_show(self.getPlayerCoord(), self.goalTypes)
                self.color_test()'''
            self.on_render()
            #pygame.time.wait(100)

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
