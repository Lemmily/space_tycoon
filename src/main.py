import math
from pygame.constants import MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from pygame.rect import Rect
from pygame.sprite import RenderUpdates
from src import R
from src.map import WorldMap
from src.render import Sprite, SortedUpdates, SortedUpdatesCamera, ParallaxSprite, TileCache, Camera, simple_camera
from src.ship import Ship

__author__ = 'Emily'

import pygame as pg

from vec2d import  *


class Game():
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.game_over = False
        self.background = pg.Surface((1024, 768))
        self.background.fill((33, 100, 117))

        self.camera = Camera(simple_camera, 768, 512)
        self.sprites = SortedUpdates()
        self.ui_overlay = RenderUpdates()


        self.world = WorldMap(1024,768,R.tile_size, group=self.sprites)
        self.picked = None
        self.selected = None #Sprite((-10, -10), R.TILE_CACHE["data/selection_anim.png"])

        # self.ui_overlay.add(self.selected)

        thing = Sprite((100, 100), R.TILE_CACHE["data/planet_1.png"], scaling=3)
        thing2 = ParallaxSprite((100, 100), R.TILE_CACHE["data/two.png"], sprite_pos=[1,0])
        self.sprites.add(thing, thing2)  # , self.world)
        thing2 = ParallaxSprite((500, 500), R.TILE_CACHE["data/two.png"], sprite_pos=[1,0], offset=0.1)
        self.sprites.add(thing2)
        thing2 = ParallaxSprite((800, 200), R.TILE_CACHE["data/two.png"], sprite_pos=[1,0])
        self.sprites.add(thing2)
        thing2 = Sprite((50, 500), R.TILE_CACHE["data/two.png"], sprite_pos=[0,0], scaling=2)
        self.sprites.add(thing2)


        self.ship = Ship(group=self.sprites)
        self.sprites.add(self.ship)
        # control
        self.pressed_key = None
        self.mouse_pressed = False
        self.cam_pos = Rect(0,0,self.screen.get_rect().width, self.screen.get_rect().height)
        self.drag = False


    def main(self):
        clock = pg.time.Clock()
        self.screen.blit(self.background, (0, 0))
        pg.display.flip()

        while not self.game_over:
            dt = 1/float(clock.tick(30))

            self.controls()

            self.sprites.clear(self.screen, self.background)
            self.sprites.update(self.camera, dt)

            self.ui_overlay.clear(self.screen, self.background)
            self.ui_overlay.update()

            dirties = self.sprites.draw(self.screen)
            dirties.append(self.ui_overlay.draw(self.screen))

            # pg.draw.lines(self.screen, (0, 0, 255), False, [(100, 100), (150, 200), (200, 100)], 4)
            # control_points = [Vec2d(100,100), Vec2d(150,500), Vec2d(450, 500), Vec2d(500,150)]
            # for x in range(0,len(control_points)-1,3):
            #     points = calculate_bezier(control_points[x:x+4])
            #     pg.draw.aalines(self.screen, (0, 0, 255), False, points )    #[(40, 100), (150, 566), (400, 100), (500, 300)]))

            if self.picked != None and self.selected == None:
                self.selected = Sprite(self.picked.sprite.rect.center, R.TILE_CACHE["data/selection_anim.png"])
                self.sprites.add(self.selected)
            elif self.picked == None and self.selected != None:
                self.selected.kill()
                self.selected = None


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



    def update_ui(self):
        if self.picked != None:
            self.selected.rect.topleft = self.picked.rect.topleft


    def mouse_clicked(self, x, y, button):
        #check if inside map first?
        if 0 < x < 750 and 0 < y < 500:
            self.picked = self.world.check_mouse_pos((x,y), self.camera.state.topleft)
            if self.picked != None:
                print "picked city: " + self.picked.name + "  ", self.picked.sprite.x_y
                if self.selected != None:
                    self.selected.rect.center = self.picked.sprite.rect.center
                    self.selected.x_y = (self.picked.sprite.x_y[0], self.picked.sprite.x_y[1])
                        # .center = (self.picked.sprite.x_y[0] + self.camera.state.topleft[0], self.picked.sprite.x_y[1] + self.camera.state.topleft[1])
            # else:
            #     self.selected.rect.topleft = (-10,-
        else:
            #do menu things here.
            pass

    def handle_events(self):

        for event in pg.event.get():
            print event
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
                if event.button == 2:  # right button
                    self.drag = True


            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                if event.button == 2:
                    self.drag = False

            elif event.type == MOUSEMOTION and self.drag:  # drag the map
                if event.rel <> (0, 0):
                    (dmx, dmy) = event.rel
                    # dy = 360.0 * dmx / (256.0 * (2 ** self.actual_zoom))
                    # dx = 2.0 * math.degrees(math.atan(math.sinh(math.pi))) * dmy / (256.0 * (2 ** self.actual_zoom))
                    # print "drag (%d,%d) > %.4f,%.4f" % (dmx,dmy,dx,dy)
                    self.camera.state.center = (self.camera.state.center[0] + dmx, self.camera.state.center[1] + dmy)
                    # self.camera.state.center = (self.cam_pos.center[0] + dmx, self.cam_pos.center[1] + dmy)
                    # self.redraw = True

            elif event.type == R.UIEVENT:
                if hasattr(event, "button"):
                    print "do something"
# def calculate_bezier(p, steps = 30):
#     """
#     Calculate a bezier curve from 4 control points and return a
#     list of the resulting points.
#
#     The function uses the forward differencing algorithm described here:
#     http://www.niksula.cs.hut.fi/~hkankaan/Homepages/bezierfast.html
#     """
#
#     t = 1.0 / steps
#     temp = t*t
#
#     f = p[0]
#     fd = 3 * (p[1] - p[0]) * t
#     fdd_per_2 = 3 * (p[0] - 2 * p[1] + p[2]) * temp
#     fddd_per_2 = 3 * (3 * (p[1] - p[2]) + p[3] - p[0]) * temp * t
#
#     fddd = 2 * fddd_per_2
#     fdd = 2 * fdd_per_2
#     fddd_per_6 = fddd_per_2 / 3.0
#
#     points = []
#     for x in range(steps):
#         points.append(f)
#         f += fd + fdd_per_2 + fddd_per_6
#         fd += fdd + fddd_per_2
#         fdd += fddd
#         fdd_per_2 += fddd_per_2
#     points.append(f)
#     return points
#


if __name__ == "__main__":
    R.TILE_CACHE = TileCache(24, 24)
    pg.init()
    pg.display.set_mode((1024, 768))
    pg.display.set_caption('space trader tycoon')

    # gamefont =

    Game().main()