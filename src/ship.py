from pyglet.sprite import Sprite
from src import resources
from src import constants
__author__ = 'Emily'


class Ship():
    def __init__(self, x=10, y=10, batch=None):
        self.x = x
        self.y = y
        self.sprite = Sprite(resources.ship_img, batch=batch)
        self.destination = (250, 250)
        self.speed = 20
        self.path = []

    def update(self, dt):
        if self.destination[0] != self.x and self.destination[1] != self.y:
            if self.x > self.destination[0]:
                dx = -self.speed * dt
            else:
                dx = self.speed * dt

            if self.y > self.destination[1]:
                dy = -self.speed * dt
            else:
                dy = self.speed * dt

            self.move(dx, dy)
            # if self.x == self.destination[0] and self.y == self.destination

        elif len(self.path) > 0:
            self.path.pop()
            self.destination = self.path.peek()


    def move(self, dx, dy):
        mX = min(dx, self.destination[0] - self.x)
        mY = min(dy, self.destination[1] - self.y)
        self.set_location(self.x + mX, self.y + mY)

    def get_location(self):
        return (self.x, self.y)

    def set_location(self, x, y):
        self.sprite.x  = x
        self.sprite.y  = y
        self.x = x
        self.y = y
        # self.sprite.position = (x / constants.tile_width, y / constants.tile_height)
