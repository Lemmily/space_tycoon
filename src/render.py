import copy
from pygame.rect import Rect
from pygame.sprite import RenderUpdates
from src import R

__author__ = 'Emily'


import pygame as pg


class Camera:
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)


def simple_camera(camera, target_rect):
    l, t, _, _ = target_rect # l = left,  t = top
    _, _, w, h = camera      # w = width, h = height
    return Rect(-l+R.HALF_WIDTH, -t+R.HALF_HEIGHT, w, h)

class TileCache:

    def __init__(self, width=R.tile_size, height=None):
        self.width = width
        self.height = height or width
        self.cache = {}


    def __getitem__(self, filename, tile_width=None, tile_height=None):
        """Return a table of files, load it from disk if needed"""

        if not isinstance(filename, basestring):
            width = filename[1] or self.width
            height = filename[2] or self.height
            filename = filename[0]
        else:
            height = self.height
            width = self.width

        key = (filename, width, height)
        try:
            return self.cache[key]
        except KeyError:
            tile_table = self._load_tile_table(filename, width, height)

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

class SortedUpdates(RenderUpdates):
    """A sprite group that sorts them by depth."""

    def sprites(self):
        """The list of sprites in the group, sorted by depth."""

        returnable = sorted(self.spritedict.keys(), key=lambda sprite: sprite.depth)
        return returnable


class SortedUpdatesCamera(RenderUpdates):
    """A sprite group that sorts them by depth."""

    def __init__(self, camera):
        super(RenderUpdates, self).__init__(self)
        self.camera = camera

    def sprites(self):
        """The list of sprites in the group, sorted by depth."""
        return sorted(self.spritedict.keys(), key=lambda sprite: sprite.depth)




class Sprite(pg.sprite.Sprite):

    def __init__(self, pos=(0, 0), frames=None, sprite_pos=None, scaling=2, tile_size=R.TILE_SIZE, ticks=2, depth=1):
        pg.sprite.Sprite.__init__(self)



        if frames:
            self.frames = copy.deepcopy(frames)
            self.orig_frames = copy.deepcopy(frames)
            # for i in range(len(frames)):
            #     # self.frames.append()
            #     for frame in frames[i]:
            #         self.frames[i].append(frame.copy())
            #         # self.frames[i].append(frames[i][j].copy())
        else:
            self.frames = [[pg.Surface([R.TILE_SIZE, R.TILE_SIZE])]]

        if scaling != None:
            for i in range(len(frames)):
                for j in range(len(frames[i])):
                    image = frames[i][j].copy()
                    t_image = pg.transform.scale(image, (image.get_width() * scaling, image.get_height() * scaling))
                    self.frames[i][j] = t_image
                    self.orig_frames[i][j] = image
        else:
            self.frames = frames


        if sprite_pos != None:
            self.image = self.frames[sprite_pos[0]][sprite_pos[1]]
            self.animation = None
        else:
            self.image = self.frames[0][0]
            self.ticks = ticks
            self.animation = self.stand_animation()

        # self.rect = self.image.get_rect()
        # center = self.rect.center
        # if scaling != None:
        #     self.image = pg.transform.scale(self.image, (R.TILE_SIZE * scaling, R.TILE_SIZE * scaling))
        self.rect = self.image.get_rect()
        # self.rect.center = self.pos

        self.pos = pos
        self.x_y = pos[0],pos[1]
        self.depth = depth

    def _get_pos(self):
        """Check the current position of the sprite on the map."""
        # return self.rect.center[0]/R.TILE_SIZE, self.rect.topleft[1]/R.TILE_SIZE
        return self.rect.center[0], self.rect.center[1]

    def _set_pos(self, pos):
        """Set the position and depth of the sprite on the map."""

        self.rect.center = pos[0], pos[1]
        # self.depth = 0

    pos = property(_get_pos, _set_pos)


    def scale_to(self, w, h):
        center = self.rect.center
        for i in range(len(self.orig_frames)):
            for j in range(len(self.orig_frames[i])):
                image = self.orig_frames[i][j].copy()
                self.frames[i][j] = pg.transform.scale(image, (w, h))
        self.image = self.frames[0][0]
        self.rect = self.image.get_rect()
        self.rect.center = center

    def move(self, dx, dy):
        """Change the position of the sprite on screen."""

        self.rect.move_ip(dx, dy)
        self.depth = self.rect.midbottom[1]

    def stand_animation(self):
        """The default animation."""
        while True:
            # Change to next frame every two ticks
            for frame in self.frames:
                self.image = frame[0]

                for i in range(self.ticks):
                    yield None

    def update(self, *args):
        """Run the current animation."""
        for arg in args:
            if isinstance(arg, Camera):
                cam_pos = arg.state.topleft
                self.rect.center = self.x_y[0] + cam_pos[0], self.x_y[1] + cam_pos[1]

        if self.animation != None:
            self.animation.next()


class ParallaxSprite(Sprite):
    def __init__(self, pos=(0, 0), frames=None, sprite_pos=None, offset=0.1, scaling=None):
        Sprite.__init__(self, pos, frames, sprite_pos, scaling)
        self.offset = offset

    def update(self, *args):
        for arg in args:
            if isinstance(arg, Camera):
                cam_pos = arg.state.topleft
                self.rect.center = self.x_y[0] + cam_pos[0] * self.offset, self.x_y[1] + cam_pos[1] * self.offset

        if self.animation != None:
            self.animation.next()

