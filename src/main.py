from src import R, render

__author__ = 'Emily'


import pygame as pg



class Game():
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.game_over = False
        self.background = pg.Surface((1024, 768))
        self.background.fill((33,100,117))


    def main(self):
        clock = pg.time.Clock()
        self.screen.blit(self.background,(0,0))

        while not self.game_over:
            # self.sprites.clear(self.screen, self.background) #test
            # self.handle_
            self.controls()
            self.handle_events()
            clock.tick(15)
            pg.display.update()

    def controls(self):
        #keys = pg.key.get_pressed()

        def pressed(key):
            return self.pressed_key == key #or keys[key]

        def m_pressed(mouse):
            return self.mouse_pressed == mouse

    def handle_events(self):
        for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.game_over = True

if __name__ == "__main__":

    R.TILE_CACHE = render.TileCache()
    pg.init()
    pg.display.set_mode((1024,768))
    pg.display.set_caption('space trader tycoon')

    #gamefont =

    Game().main()