from src import R

__author__ = 'Emily'


import pygame as pg


class TileCache:

    def __init__(self, width=R.tile_size, height=None):
        self.width = width
        self.height = height or width
        self.cache = {}


    def __getitem__(self, filename):
        """Return a table of files, load it from disk if needed"""

        key = (filename, self.width, self.height)
        try:
            return self.cache[key]
        except KeyError:
            tile_table = self._load_tile_table(filename, self.width, self.height)

            self.cache[key] = tile_table
            return tile_table


    def _load_tile_table(self, filename, width, height):
        """Load an image and split it into tiles."""
        image = pg.image.load(filename).convert_alpha()
        # image.
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_x in range(0, image_width / width):
            line = []
            tile_table.append(line)
            for tile_y in range(0, image_height / height):
                rect = (tile_x * width, tile_y * height, width, height)
                line.append(image.subsurface(rect))
        return tile_table

class Sprite(pg.sprite.Sprite):
    def __init__(self, pos=(0,0),frames=None, sprite_pos=[0, 0], t_size=R.MAP_TILE_WIDTH):
        super(Sprite, self).__init__()
        self.frames = frames
        if (self.frames != None):
            self.image = frames[sprite_pos[0]][sprite_pos[1]]
        else:
            self.image = pg.Surface([t_size, t_size])
            self.image.fill((100, 20, 20))
        self.rect = self.image.get_rect()
        self.animation = None  # self.stand_animation()
        self.tile_size = t_size
        self.pos = pos
        self.depth = 0


    def update(self, *args):
        # if self.animation is not None:
        #             self.animation.next()
        pass

    def move(self, dx, dy):
        """Change the position of the sprite on screen."""

        self.rect.move_ip(dx, dy)
        self.depth = self.rect.midbottom[1]


    def _get_tile_pos(self):
        """returns as TILE position, """
        return ( self.rect.x / (self.tile_size), self.rect.y / self.tile_size)

    def _set_tile_pos(self, pos):
        """Stores the position of the PIXEL POSITION X,Y with INCLUDED padding AND offset FROM the given TILE position. """
        self.rect.topleft = (pos[0] * (self.tile_size),  # x
                             pos[1] * (self.tile_size))  # y

    tile_pos = property(_get_tile_pos, _set_tile_pos)

    def _get_pix_pos(self):
        """check current pos of sprite on map, returns as PIXEL position"""
        # return (self.offset + self.rect.x/(R.MAP_TILE_WIDTH+self.padding), self.offset + self.rect.y/(R.MAP_TILE_WIDTH + self.padding))
        #return ( (self.rect.x - self.offsetX )/(R.MAP_TILE_WIDTH+self.padding), (self.rect.y - self.offsetY)/(R.MAP_TILE_WIDTH + self.padding))
        return (self.rect.x, self.rect.y )

    def _set_pix_pos(self, pos):
        """Set the position by the PIXEL POSITION X,Y with INCLUDED padding AND offset FROM the given PIXEL position. """
        self.rect.topleft = (pos[0] * (self.tile_size),  # x
                             pos[1] * (self.tile_size))  # y

        self.depth = 0  # self.rect.midbottom[1] # not used

    pos = property(_get_pix_pos, _set_pix_pos)