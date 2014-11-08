import math
from pygame.constants import MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from pygame.rect import Rect
from pygame.sprite import RenderUpdates
from src import R
from src.map import SolarSystem, Galaxy
from src.render import Sprite, SortedUpdates, SortedUpdatesCamera, ParallaxSprite, TileCache, Camera, simple_camera
from src.ship import Ship

import pygame.gfxdraw as gfxdraw

__author__ = 'Emily'

import pygame as pg

from vec2d import  *


class Game():
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.game_over = False
        self.background = pg.Surface((1440, 768))
        self.background.fill((0, 60, 77))

        self.ui_background_right = pg.Surface((R.UI_LEFTBAR, R.WINDOW_HEIGHT))
        self.ui_background_right.fill((0, 0, 0))

        self.ui_background_bottom =  pg.Surface((R.WINDOW_WIDTH, R.UI_BOTTOMBAR))
        self.ui_background_bottom.fill((0, 0, 0))

        self.ui_background = pg.Surface((R.WINDOW_WIDTH, R.WINDOW_HEIGHT))
        self.ui_background.fill((100,200,100))
        self.ui_background.set_colorkey((100,200,100))

        self.ui_background.blit(self.ui_background_bottom, (0,R.UI_DOWN))
        self.ui_background.blit(self.ui_background_right, (R.UI_LEFT,0))

        self.camera = Camera(simple_camera, R.MAP_WINDOW_WIDTH, R.MAP_WINDOW_HEIGHT)
        self.sprites = SortedUpdates()
        self.ui_overlay = RenderUpdates()




        self.galaxy = Galaxy()#1024,768,R.tile_size, group=self.sprites)
        print "finished generating"
        self.layer = self.galaxy.active_sector
        self.zoom = "sector" # galaxy, sector, solar system, planet
        self.selected = None
        self.selector = None #Sprite((-10, -10), R.TILE_CACHE["data/selection_anim.png"])


        ##test sprites.
        thing3 = Sprite((200, 200), R.TILE_CACHE["data/planet_1.png"], scaling=2, ticks=8, depth=2)
        thing4 = Sprite((500, 350), R.TILE_CACHE["data/planet_1.png"], scaling=2, ticks=8, depth=2, row=1)
        # thing = Sprite((100, 100), R.TILE_CACHE["data/planet_1.png"], scaling=3, ticks=4)
        # thing2 = ParallaxSprite((100, 100), R.TILE_CACHE["data/two.png"], sprite_pos=[1,0])
        # self.sprites.add( thing2, thing3, thing4)  # , self.world)
        # thing2 = ParallaxSprite((500, 500), R.TILE_CACHE["data/two.png"], sprite_pos=[1,0], offset=0.1)
        # self.sprites.add(thing2)
        # thing2 = ParallaxSprite((800, 200), R.TILE_CACHE["data/two.png"], sprite_pos=[1,0])
        # self.sprites.add(thing2)


        self.ship = Ship(group=self.sprites)

        self.sprites.add(self.ship)


        # control
        self.pressed_key = None
        self.mouse_pressed = False
        self.cam_pos = Rect(0,0,self.screen.get_rect().width, self.screen.get_rect().height)
        self.drag = False

    def render(self, dt):
        dirties = []
        # if self.zoom == "galaxy":
        if self.zoom == "solar" or "sector":
            self.layer.sprites.clear(self.screen, self.background)
            if self.zoom == "sector":
                for connection in self.layer.connections.values():
                    points = self.layer.get_connections(connection, self.camera)
                    gfxdraw.bezier(self.screen, points, 10, (255,0,0))
            self.layer.sprites.update(self.camera, dt)
            dirties.append(self.layer.sprites.draw(self.screen))
        else:
            self.sprites.clear(self.screen, self.background)
            self.sprites.update(self.camera, dt)

        self.sprites.update(self.camera, dt)
        self.ui_overlay.update(self.camera,dt)
        return dirties


    def main(self):
        clock = pg.time.Clock()
        self.screen.blit(self.background, (0, 0))
        pg.display.flip()

        while not self.game_over:
            dt = 1/float(clock.tick(30))

            ###temp
            self.screen.blit(self.background, (0,0))
            ####



            self.controls()

            dirties = self.render(dt)

            # self.sprites.clear(self.screen, self.background)
            # self.sprites.update(self.camera, dt)

            # self.ui_overlay.clear(self.screen, self.background)
            # self.ui_overlay.update()
            #
            # for connection in self.galaxy.connections.values():
            #     points = self.galaxy.get_connections(connection, self.camera)
            #
            #     gfxdraw.bezier(self.screen, points, 10, (255,0,0))

            # dirties = self.sprites.draw(self.screen)
            dirties.append(self.ui_overlay.draw(self.screen))

            # pg.draw.lines(self.screen, (0, 0, 255), False, [(100, 100), (150, 200), (200, 100)], 4)
            # control_points = [Vec2d(100,100), Vec2d(150,500), Vec2d(450, 500), Vec2d(500,150)]
            # for x in range(0,len(control_points)-1,3):
            #     points = calculate_bezier(control_points[x:x+4])
            #     pg.draw.aalines(self.screen, (0, 0, 255), False, points )    #[(40, 100), (150, 566), (400, 100), (500, 300)]))


            # for sprite in self.sprites:
            #     points = (sprite.rect.topleft, sprite.rect.topright, sprite.rect.bottomright, sprite.rect.bottomleft)
            #     pg.draw.aalines(self.screen, (0, 0, 255), True, points)


            self.update_ui()

            pg.display.update()
            # pg.display.flip()

            self.handle_events()

    def controls(self):
        # keys = pg.key.get_pressed()

        def pressed(key):
            return self.pressed_key == key  #or keys[key]

        def m_pressed(mouse):
            return self.mouse_pressed == mouse

        if pressed(pg.K_d):
            self.camera.state.topleft = (0,0)
            self.pressed_key = None

        if pressed(pg.K_x):
            if hasattr(self.selected, "sprites"):
                self.switch_zoom(self.selected.zoom, self.selected)
            self.pressed_key = None

        if pressed(pg.K_z):
            if self.layer.parent != None:
                self.switch_zoom(self.layer.parent.zoom, self.layer.parent)
            self.pressed_key = None


    def update_ui(self):
        if self.selected != None and self.selector == None:

            if hasattr(self.selected, "sprite"):
                sprite = self.selected.sprite
            else:
                sprite = self.selected


            self.selector = Sprite(sprite.rect.center, R.TILE_CACHE["data/selection_anim.png"], depth=10)

            size = max(sprite.rect.w, sprite.rect.w)

            self.selector.scale_to(size,size)
            self.selector.x_y = (sprite.x_y[0], sprite.x_y[1])
            self.ui_overlay.add(self.selector)
        elif self.selected == None and self.selector != None:
            self.selector.kill()
            self.selector = None

        self.screen.blit(self.ui_background,(0,0))


    def mouse_clicked(self, (x, y), button):
        #check if inside map first?
        # if button == 1:
        if 0 < x < R.UI_LEFT and 0 < y < R.UI_DOWN:
            if button == 1:
                if self.zoom == "galaxy":
                    self.selected = self.galaxy.check_mouse_pos((x,y), self.camera.state.topleft)
                elif self.zoom == "solar" or "sector":
                    self.selected = self.layer.check_mouse_pos((x,y), self.camera.state.topleft)
                else:
                    self.selected = None

                if self.selected != None:
                    print "picked object: " + self.selected.name + "  ", self.selected.x_y
                    if self.selector != None:
                        # self.selected.rect.center = self.picked.sprite.rect.center
                        self.selector.x_y = (self.selected.x_y[0], self.selected.x_y[1])
                            # .center = (self.picked.sprite.x_y[0] + self.camera.state.topleft[0], self.picked.sprite.x_y[1] + self.camera.state.topleft[1])
                else:
                    for sprite in self.sprites.sprites():
                        if sprite.rect.collidepoint((x,y)):
                            self.selected = sprite
        else:
            #do menu click things here.
            pass

    def handle_events(self):
        for event in pg.event.get():
            # print event
            if event.type == pg.QUIT:
                self.game_over = True

            if event.type == pg.KEYDOWN:
                self.pressed_key = event.key

            if event.type == MOUSEBUTTONDOWN:  # mouse button down
                # if event.button == 4:  # scrollwheel up
                #     self.actual_zoom = self.actual_zoom + 1
                #     if self.actual_zoom > self.zoom_limit[1]:
                #         self.actual_zoom = self.zoom_limit[1]
                #
                # if event.button == 5:  # scrollwheel down
                #     self.actual_zoom = self.actual_zoom - 1
                #     if self.actual_zoom < self.zoom_limit[0]:
                #         self.actual_zoom = self.zoom_limit[0]

                # if event.button == 1:  # left button
                if event.button == 2:  # middle button
                    self.drag = True

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1: #left
                    self.mouse_clicked(event.pos, event.button)
                if event.button == 2: #middle
                    self.drag = False
                if event.button == 3: #right
                    self.mouse_clicked(event.pos, event.button)

            elif event.type == MOUSEMOTION and self.drag:  # drag the map
                if event.rel <> (0, 0):
                    (dmx, dmy) = event.rel
                    # dy = 360.0 * dmx / (256.0 * (2 ** self.actual_zoom))
                    # dx = 2.0 * math.degrees(math.atan(math.sinh(math.pi))) * dmy / (256.0 * (2 ** self.actual_zoom))
                    # print "drag (%d,%d) > %.4f,%.4f" % (dmx,dmy,dx,dy)
                    self.camera.state.center = (self.camera.state.center[0] + dmx, self.camera.state.center[1] + dmy)
                    self.camera.bound(self.layer)
                    # self.camera.state.center = (self.cam_pos.center[0] + dmx, self.cam_pos.center[1] + dmy)
                    # self.redraw = True

            elif event.type == R.UIEVENT:
                if hasattr(event, "button"):
                    print "do something"


    def switch_zoom(self, zoom, layer):
        self.ui_overlay.clear(self.screen, self.background)
        self.camera.state.topleft = 0,0
        self.zoom = zoom

        if self.selector != None:
            self.selector.kill()
            self.selector = None

        self.selected = None


        self.layer = layer
        # #TODO: each of these layers might hold the sprites different. make it so it displays the right ones properly.
        # if zoom == "galaxy":
        #     #do something special
        #     pass
        # else:
        #     self.sprites = layer.sprites



if __name__ == "__main__":
    R.TILE_CACHE = TileCache(24, 24)
    pg.init()
    pg.display.set_mode((1440, 768))
    pg.display.set_caption('space trader tycoon')

    # gamefont =

    Game().main()