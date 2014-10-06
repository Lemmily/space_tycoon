import math
from pygame.rect import Rect
from src import R
from src.render import Sprite, SortedUpdates

__author__ = 'Emily'

import random

rand = random.Random()


# class City():
#     def __init__(self, name, x=-1, y=-1):
#         self.name = name
#         self.x = x
#         self.y = y
#         self.connections = {}


class Star(Sprite):
    def __init__(self, name, x=-1, y=-1):
        Sprite.__init__(self, (200, 200), R.TILE_CACHE["data/planet_1.png"], scaling=2, ticks=8, depth=2, row=1)
        self.name = name
        self.x = x
        self.y = y

class Planet(Sprite):
    def __init__(self, name, x=-1, y=-1):
        Sprite.__init__(self, (200, 200), R.TILE_CACHE["data/planet_1.png"], scaling=2, ticks=8, depth=2)
        self.name = name
        self.x = x
        self.y = y

class AsteroidCluster(Sprite):
    def __init__(self, name, x=-1, y=-1):
        Sprite.__init__(self, (200, 200), R.TILE_CACHE["data/planet_1.png"], sprite_pos=[0,3], scaling=1, ticks=8, depth=2, row=3)
        self.name = name
        self.x = x
        self.y = y


ALL_OOI = [Planet, AsteroidCluster]
class NotableObject(Sprite):
    def __init__(self, sector,(x,y),(w,h), frames=None, sprite_pos=None, scaling=2, ticks=2, depth=1, row=0 ):
        """
        :param sector: sector co-ordinate eg, (0,0)
        :return:
        """
        if frames == None:
            frames =R.TILE_CACHE["data/city.png"]
        Sprite.__init__(self, (x, y), frames, sprite_pos=sprite_pos, scaling=scaling, ticks=ticks, depth=depth, row=row)
        self.sector = sector
        self.x = x # the x coordinate WITHIN the sector
        self.y = y
        self.w = w # size of this "map" when zoomed to that level.
        self.h = h
        self.name = "default"
        self.sprites = SortedUpdates()
        self.objects = []
        self.orig_rect = self.rect.copy() #used to store the coordinate position with a rect. self.rect tracks image screen position.

    def check_mouse_pos(self, mouse_pos, cam_pos=(0,0)):
        for object in self.objects:
            if object.sprite.rect.collidepoint(mouse_pos):
                return object
        # tile_pos = ((mouse_pos[0] + 1 + cam_pos[0])/self.tile_width, (mouse_pos[1] + 1 + cam_pos[1])/self.tile_height)
        # if 0 > tile_pos[0] > len(self.tiles) - 1 or  0 > tile_pos[1] > len(self.tiles[0]) - 1:
        #     return None
        return None
        # return self.tiles[tile_pos[0]][tile_pos[1]]

class AsteroidField(NotableObject):
    def __init__(self, sector, (x, y), (w, h), tile_width=24, group=None):
        NotableObject.__init__(self, sector,(x,y),(w,h), R.TILE_CACHE["data/planet_1.png"], sprite_pos=[0,3], ticks=8, row=3)
        self.tile_width = tile_width
        # self.sprite = Sprite((x, y),

        for i in range(rand.randint(5, 15)):
            asteroid = AsteroidCluster("asteroid"+str(i), rand.randint(100, w), rand.randint(100, h))
            self.sprites.add(asteroid)
            self.objects.append(asteroid)

class RoguePlanet(NotableObject):
    def __init__(self, sector, (x, y), (w, h), tile_width=24, group=None):
        NotableObject.__init__(self, sector,(x,y),(w,h), R.TILE_CACHE["data/planet_1.png"], ticks=8, row=2)
        # self.sprite = Sprite((x, y)

class SolarSystem(NotableObject):
    def __init__(self, sector, (x, y), (w, h), tile_width=24, group=None):

        NotableObject.__init__(self, sector,(x,y),(w,h), R.TILE_CACHE["data/planet_1.png"], ticks=8, row=2)
        self.tile_width = tile_width #
        # self.objects = [] # moved to parent
        self.cities_dict = {}
        # self.connections = {}
        # self.sprite = Sprite((x, y)


        for i in range(rand.randint(2, 6)):
            planet = Planet("planet" + str(i))
            if self.place_planet(planet):
                # planet.sprite = Sprite((planet.x, planet.y), R.TILE_CACHE["data/planet_1.png"], ticks=8)
                if group != None:
                    group.add(planet)
                self.sprites.add(planet)

        # self.create_connections()

    def place_planet(self, planet):
        """
        Tries to place the city on the map,
        :param planet:
        :return:
        """
        placed = False

        distance = 5 * self.tile_width
        tries = 0
        while not placed and distance > 3 * self.tile_width:
            tries += 1
            x = rand.randint(self.tile_width, self.w - self.tile_width)
            y = rand.randint(self.tile_width, self.h - self.tile_width - 1)
            # y = rand.randint(1, len(self.tiles[x]) - 2)
            planet.x,planet.y = x,y

            placed = self.check_planet_distances(planet, distance)
            if tries >= 5:
                distance -= 1
                tries = 0

        if placed:
            self.objects.append(planet)
            self.cities_dict[planet.name] = planet
            # self.tiles[planet.x/self.tile_width][planet.y/self.tile_width] = planet
            return True

        else:
            return False

    def check_planet_distances(self, planet, distance=8):
        if planet.x == -1:
            return False
        for other_city in self.objects:
            dx = abs(planet.x - other_city.x)
            dy = abs(planet.y - other_city.y)
            if math.sqrt(dx * dx + dy * dy) < distance:
                return False

        return True # good position in terms of distances.



    def get_connections(self, connection, camera):
        offset = camera.state.topleft
        new_connections = []
        for pair in connection:
            new_connections.append((pair[0] + offset[0], pair[1] + offset[1]))

        return new_connections

    def add_connection(self, planet, other_planet):
        planet.connections[other_planet.name] = ((planet.x, planet.y), (other_planet.x, other_planet.y))
        midpoint = (max(planet.x, other_planet.x) - abs(planet.x - other_planet.x)/3, max(planet.y, other_planet.y) - abs(planet.y - other_planet.y)/3)
        self.connections[planet.name + other_planet.name] = ((planet.x, planet.y), midpoint, (other_planet.x, other_planet.y))
        return True




ALL_POI = [SolarSystem, AsteroidField]
class Sector:
    def __init__(self, x ,y, w, h=None):
        """

        :param x: sector x coordinate
        :param y: sector y coordinate
        :return:
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h or w
        self.connections = {}
        self.points_of_interest = []
        self.sprites = SortedUpdates()
        self.rect = None

        for i in range(rand.randint(3, 9)):
            x,y = self.find_place()
            while x == False:
                x,y = self.find_place()
            poi = rand.choice(ALL_POI)(self, (x, y), (512, 512))
            self.add_poi(poi)



    def add_poi(self, poi):
        self.points_of_interest.append(poi)
        self.sprites.add(poi)

    def add_connection(self, object, other_object):
        object.connections[other_object.name] = ((object.x, object.y), (other_object.x, other_object.y))

        x_dev = rand.randint(-abs(object.x - other_object.x), abs(object.x - other_object.x)) #deviation in the x for midpoint
        y_dev = rand.randint(-abs(object.y - other_object.y), abs(object.y - other_object.y)) #same for y
        midpoint = (max(object.x, other_object.x) - x_dev, max(object.y, other_object.y) - y_dev)

        self.connections[object.name + other_object.name] = ((object.x, object.y), midpoint, (other_object.x, other_object.y))

        return True

    def create_connections(self):
        for poi in self.points_of_interest:
            connected = False
            while not connected:
                # num = rand.randint(0,9) #inclusive of upper limit.
                # connection = "city" + str(num)
                other_poi = rand.choice(self.points_of_interest)
                # other_city = self.cities_dict[connection]
                if other_poi.name != poi.name and not ( self.connections.has_key(poi.name + other_poi.name) or self.connections.has_key(other_poi.name + poi.name)):
                    connected = self.add_connection(poi, other_poi)

    def find_place(self):
        x, y = 0, 0

        placed = False

        distance = 5 * R.TILE_SIZE
        tries = 0
        while not placed and distance > 3 * R.TILE_SIZE:
            tries += 1
            x = rand.randint(R.TILE_SIZE, self.w - R.TILE_SIZE)
            y = rand.randint(R.TILE_SIZE, self.h - R.TILE_SIZE - 1)
            # y = rand.randint(1, len(self.tiles[x]) - 2)

            placed = self.check_distance(x, y, distance)
            if not placed and tries >= 5:
                distance -= 1 * R.TILE_SIZE/2
                tries = 0

        if placed:

            return x,y

        else:
            return False, False

    def check_distance(self, x, y, distance):
        for object in self.points_of_interest:
            if length((x,y), (object.x,object.y)) > distance:
                return True

        if len(self.points_of_interest) == 0:
            return True

        return False

    def check_mouse_pos(self, x, y):
        for place in self.points_of_interest:
            if place.orig_rect.collidepoint(x, y): #TODO: potentially change it to use the places' rect instead of the sprite.
                return place

        return None


class Galaxy:
    def __init__(self):
        self.sectors = []
        self.sector_rects = {}
        self.rects_sectors = {}
        self.connections = {}

        # self.sprites = SortedUpdates()


        for i in range(4):
            self.sectors.append([])
            for j in range(4):
                sector, rect = self.create_sector(i, j)

                self.sectors[i].append(sector)
                self.sector_rects[sector] = rect
                self.rects_sectors[rect.topleft] = sector # Rect is not a hashable object so done it to the topleft tuple instead


        self.active_sector = self.sectors[0][0]


    def create_sector(self, x, y, sector_size=1024):
        sector = Sector(x,y,sector_size)
        rect = Rect(x*sector_size, y * sector_size, sector_size, sector_size)
        sector.rect = rect
        #other stuff...
        return sector, rect

    def check_mouse_pos(self,mouse_pos, camera_pos):
        x = mouse_pos[0] - camera_pos[0]
        y = mouse_pos[1] - camera_pos[1]

        print mouse_pos, camera_pos, "=", x, y

        # if self.active_sector.rect.collidepoint(x,y):
        return self.active_sector.check_mouse_pos(x, y)


def length((x,y),(ox,oy)):
    dx = abs(x - ox)
    dy = abs(y - oy)
    return math.sqrt(dx * dx + dy * dy)