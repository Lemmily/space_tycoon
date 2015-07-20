import math
from pygame.rect import Rect

__author__ = 'Emily'


class QuadTree:
    def __init__(self, level, bounds, item_limit=5):
        self.bounds = bounds.copy()
        self.level = level
        self.nodes = []
        self.items = []
        self.max_items = item_limit

    def insert(self, item):
        if len(self.nodes) > 0:
            index = self.get_index()
            self.nodes[index].insert(item)
            return

        self.items.append(item)

        if len(self.items) > self.max_items and self.level > 0:
            if len(self.nodes) == 0:
                self.split()

            for object in self.items:
                index = self.get_index(object.rect)
                self.nodes[index].insert(self.items.remove(object))

    def split(self):
        # make four new quadtrees and assign the nodes.

        sub_width =self.bounds.w / 2
        sub_height = self.bounds.h / 2
        x = self.bounds.x
        y = self.bounds.y

        self.nodes.append( QuadTree(self.level-1, Rect(x, y, sub_width, sub_height)) )
        self.nodes.append( QuadTree(self.level-1, Rect(x + sub_width, y, sub_width, sub_height)) )
        self.nodes.append( QuadTree(self.level-1, Rect(x, y + sub_height, sub_width, sub_height)) )
        self.nodes.append( QuadTree(self.level-1, Rect(x + sub_width, y + sub_height, sub_width, sub_height)) )

    def get_index(self, bounds):
        return self.get_index(bounds.x,
                              bounds.y,
                              bounds.w,
                              bounds.h)

    def get_index(self, x, y, w=1, h=1):
        """finds the quadrant where the origin fits"""

        horizontal_line_midpoint = self.bounds.x + (self.bounds.w / 2)
        vertical_line_midpoint = self.bounds.y + (self.bounds.h / 2)

        # object origin in top quadrant
        top = y > vertical_line_midpoint

        if x < horizontal_line_midpoint:
            # its in the left

            if top:
                return 0
            else:
                return 1
        else:
            # right quadrants
            if top:
                return 3
            else:
                return 2


def find_length((x,y),(ox,oy)):
    dx = abs(x - ox)
    dy = abs(y - oy)
    return math.sqrt(dx * dx + dy * dy)