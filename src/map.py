import math
import random

from pygame.rect import Rect
import pygame as pg
from src import R, ai
from src.render import Sprite, SortedUpdates
from src.utils import find_length

__author__ = 'Emily'

rand = random.Random()


# class City():
#     def __init__(self, name, x=-1, y=-1):
#         self.name = name
#         self.x = x
#         self.y = y
#         self.connections = {}


class ObjectOfInterest(Sprite):
    def __init__(self, name, x, y, frames=None, sprite_pos=None, scaling=2, ticks=2, depth=1, row=0):
        if frames is None:
            frames = R.TILE_CACHE["data/city.png"]
        Sprite.__init__(self, (x, y), frames, sprite_pos=sprite_pos, scaling=scaling, ticks=ticks, depth=depth, row=row)
        self.name = name
        self.x = x
        self.y = y
        self.parent = None
        self.zoom = "planet"
        # self.node = Node()
        self.connections = {}

    @property
    def location(self):
        return (self.x, self.y)


class Star(ObjectOfInterest):
    def __init__(self, name, x=-1, y=-1):
        ObjectOfInterest.__init__(self, name, x, y, R.TILE_CACHE["data/planet_1.png"], scaling=2, ticks=8, depth=2,
                                  row=1)


class Planet(ObjectOfInterest):
    def __init__(self, name, x=-1, y=-1):
        ObjectOfInterest.__init__(self, name, x, y, R.TILE_CACHE["data/planet_1.png"], scaling=2, ticks=8, depth=2)


class AsteroidCluster(ObjectOfInterest):
    def __init__(self, name, x=-1, y=-1):
        ObjectOfInterest.__init__(self, name, x, y, R.TILE_CACHE["data/planet_1.png"], sprite_pos=[0, 3], scaling=1,
                                  ticks=8, depth=2, row=3)


class Gateway(ObjectOfInterest):
    def __init__(self, name, x=-1, y=-1):
        ObjectOfInterest.__init__(self, name, x, y, R.TILE_CACHE["data/planet_1.png"], sprite_pos=[0, 4], scaling=2,
                                  ticks=8, depth=2, row=3)
        # self.node = Node(self.name, True, "solar")


ALL_OOI = [Planet, AsteroidCluster]  # Star not included as has special rules


class NotableObject(Sprite):
    def __init__(self, sector, (x, y), (w, h), frames=None, sprite_pos=None, scaling=2, ticks=2, depth=1, row=0):
        """
        :param sector: sector co-ordinate eg, (0,0)
        :return:
        """
        if frames is None:
            frames = R.TILE_CACHE["data/city.png"]
        Sprite.__init__(self, (x, y), frames, sprite_pos=sprite_pos, scaling=scaling, ticks=ticks, depth=depth, row=row)
        self.sector = sector
        self.x = x  # the x coordinate WITHIN the sector
        self.y = y
        self.w = w  # size of this "map" when zoomed to that level.
        self.h = h
        self.dimensions = Rect(x, y, w, h)
        self.name = "default"
        self.sprites = SortedUpdates()
        self.objects = []

        # used to store the coordinate position with a rect. self.rect tracks image screen position.
        self.orig_rect = self.rect.copy()
        self.parent = None
        self.zoom = "solar"
        self.connections = {}

    @property
    def location(self):
        return (self.x, self.y)

    def check_mouse_pos(self, mouse_pos, cam_pos=(0, 0)):
        for obj in self.objects:
            if obj.rect.collidepoint(mouse_pos):
                return obj
        # tile_pos = ((mouse_pos[0] + 1 + cam_pos[0])/self.tile_width, (mouse_pos[1] + 1 + cam_pos[1])/self.tile_height)
        # if 0 > tile_pos[0] > len(self.tiles) - 1 or  0 > tile_pos[1] > len(self.tiles[0]) - 1:
        #     return None
        return None
        # return self.tiles[tile_pos[0]][tile_pos[1]]

    def get_connections(self, connection, camera):
        """
        get connection tuples, WITH the offset from the camera applied.
        :param connection:
        :param camera:
        :return:
        """
        offset = camera.state.topleft
        new_connections = []
        for pair in connection:
            new_connections.append((pair[0] + offset[0], pair[1] + offset[1]))

        return new_connections

    def add_connection(self, obj, other_object):
        obj.connections[other_object.name] = ((obj.x, obj.y), (other_object.x, other_object.y))
        midpoint = (max(obj.x, other_object.x) - abs(obj.x - other_object.x) / 3,
                    max(obj.y, other_object.y) - abs(obj.y - other_object.y) / 3)
        self.connections[obj.name + other_object.name] = (
            (obj.x, obj.y), midpoint, (other_object.x, other_object.y))
        return True

    def make_graph(self):
        actual_x = self.sector.x * self.sector.w + self.x
        actual_y = self.sector.y * self.sector.h + self.y
        self.graph = ai.Graph((actual_x, actual_y))

        for obj in self.objects:
            obj_node = ai.Node(self.name + "-" + obj.name, obj.location, 20)
            self.graph.add_edge(obj_node)  # todo: create an appropriate cost lookup.

        for obj in self.objects:
            connections = []
            for connection in obj.connections.values():
                connections.append(connection[1])

            if len(connections) > 0:
                self.graph.add_connection(obj.location, connections)


class AsteroidField(NotableObject):
    def __init__(self, sector, (x, y), (w, h), tile_width=24, group=None):
        NotableObject.__init__(self, sector, (x, y), (w, h), R.TILE_CACHE["data/planet_1.png"], sprite_pos=[0, 3],
                               ticks=8, row=3)
        self.tile_width = tile_width
        # self.sprite = Sprite((x, y),

        for i in range(rand.randint(5, 15)):
            asteroid = AsteroidCluster("asteroid" + str(i), rand.randint(100, w), rand.randint(100, h))
            asteroid.parent = self
            self.sprites.add(asteroid)
            self.objects.append(asteroid)


class RoguePlanet(NotableObject):
    def __init__(self, sector, (x, y), (w, h), tile_width=24, group=None):
        NotableObject.__init__(self, sector, (x, y), (w, h), R.TILE_CACHE["data/planet_1.png"], ticks=8, row=2)
        # self.sprite = Sprite((x, y)


class SolarSystem(NotableObject):
    def __init__(self, sector, (x, y), (w, h), tile_width=24, group=None):

        NotableObject.__init__(self, sector, (x, y), (w, h), R.TILE_CACHE["data/planet_1.png"], sprite_pos=[0, 2],
                               ticks=8, row=2)
        self.tile_width = tile_width  #
        # self.objects = [] # moved to parent
        self.cities_dict = {}
        # self.connections = {}
        # self.sprite = Sprite((x, y)

        self.bg = Sprite()
        center = self.bg.rect.center
        self.bg.image = pg.Surface((w, h))
        self.bg.rect = self.image.get_rect()
        self.bg.rect.center = center
        self.bg.image.fill((50, 0, 0))
        self.sprites.add(self.bg)
        self.star = star = Star("star" + str(sector.x) + str(sector.y), w / 2, h / 2)
        self.sprites.add(star)
        self.objects.append(star)

        gx, gy = self.place_planet()
        gateway = Gateway("gateway", gx, gy)
        self.add_object(gateway)

        for i in range(rand.randint(2, 6)):
            x, y = self.place_planet()
            if x != -1:
                planet = Planet("planet" + str(i), x, y)
                # planet.sprite = Sprite((planet.x, planet.y), R.TILE_CACHE["data/planet_1.png"], ticks=8)
                self.add_object(planet)
                pg.gfxdraw.aacircle(self.bg.image, w / 2, h / 2, int(find_length(planet.x_y, star.x_y)),
                                    (200, 200, 100))
                pg.draw.circle(self.bg.image, (200, 200, 100), (w / 2, h / 2), int(find_length(planet.x_y, star.x_y)),
                               2)
                # self.tiles[planet.x/self.tile_width][planet.y/self.tile_width] = planet

        self.create_connections()

    def add_object(self, obj):
        obj.parent = self
        # if group != None:
        #     group.add(planet)
        self.sprites.add(obj)
        self.objects.append(obj)
        self.cities_dict[obj.name] = obj

    def place_planet(self):
        """
        Tries to place the planet on the map,
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
            placed = self.check_planet_distances((x, y), distance)
            if tries >= 5:
                distance -= 1
                tries = 0

        return x, y

    def check_planet_distances(self, (x, y), distance=8):
        """
        check that planets are a at least :param: distance away.
        :param distance:
        :return: whether the location is distant enough away.
        """
        if x == -1:
            return False
        for other_object in self.objects:
            dx = abs(x - other_object.x)
            dy = abs(y - other_object.y)
            if math.sqrt(dx * dx + dy * dy) < distance:
                return False

        return True  # good position in terms of distances.

    def add_connection(self, obj, other_object):
        obj.connections[other_object.name] = ((obj.x, obj.y), (other_object.x, other_object.y))
        # midpoint = (max(object.x, other_object.x) - abs(object.x - other_object.x)/3, max(object.y, other_object.y) - abs(object.y - other_object.y)/3)
        self.connections[obj.name + other_object.name] = ((obj.x, obj.y), (other_object.x, other_object.y))
        return True

    # def add_connection(self, object, other_object):
    #     object.connections[other_object.name] = ((object.x, object.y), (other_object.x, other_object.y))
    #
    #     x_dev = rand.randint(-abs(object.x - other_object.x), abs(object.x - other_object.x)) #deviation in the x for midpoint
    #     y_dev = rand.randint(-abs(object.y - other_object.y), abs(object.y - other_object.y)) #same for y
    #     midpoint = (max(object.x, other_object.x) - x_dev, max(object.y, other_object.y) - y_dev)
    #
    #     self.connections[object.name + other_object.name] = ((object.x, object.y), midpoint, (other_object.x, other_object.y))
    #
    #     return True

    def get_connections(self, connection, camera):
        offset = camera.state.topleft
        new_connections = []
        for pair in connection:
            new_connections.append((pair[0] + offset[0], pair[1] + offset[1]))

        return new_connections

    def create_connections(self):
        for poi in self.objects:
            connected = False
            while not connected and poi != self.star:
                # num = rand.randint(0,9) #inclusive of upper limit.
                # connection = "city" + str(num)
                other_poi = rand.choice(self.objects)
                # other_city = self.cities_dict[connection]
                if other_poi != self.star and other_poi.name != poi.name and not (
                            poi.name + other_poi.name in self.connections or other_poi.name + poi.name in self.connections):
                    connected = self.add_connection(poi, other_poi)
                else:
                    break


ALL_POI = [SolarSystem, AsteroidField]


class Sector:
    def __init__(self, x, y, w, h=None, name="sector"):
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
        self.dimensions = None
        self.parent = None
        self.name = name
        self.zoom = "sector"
        self.graph = None

        for i in range(rand.randint(3, 9)):
            x, y = self.find_place()
            while not x:
                x, y = self.find_place()
            poi = rand.choice(ALL_POI)(self, (x, y), (512, 512))
            poi.parent = self
            poi.name = poi.__class__.__name__.capitalize() + str(i)
            self.add_poi(poi)

        self.create_connections()
        self.make_graph()

    def add_poi(self, poi):
        self.points_of_interest.append(poi)
        self.sprites.add(poi)

    def add_connection(self, obj, other_object):
        obj.connections[other_object.name] = ((obj.x, obj.y), (other_object.x, other_object.y))
        # no longer puts midpoint in here
        self.connections[obj.name + other_object.name] = ((obj.x, obj.y), (other_object.x, other_object.y))

        return True

    def get_points_from_connections(self, pos):
        new_connections = []
        for pair in self.connections.values():
            obj = pair[0]
            other_object = pair[1]

            x_dev = -abs(obj[0] - other_object[0])
            # / coef + abs(object[0] - other_object[0]) * coef #deviation in the x for midpoint
            y_dev = abs(obj[1] - other_object[1])  # same for y
            # y_dev = -abs(object[1] - other_object[1]) / coef + abs(object[1] - other_object[1]) * coef #same for y
            # y_dev = rand.randint(-abs(object[1] - other_object[1]), abs(object[1] - other_object[1])) #same for y

            x_dev = max(other_object[0], obj[0]) - min(other_object[0], obj[0])
            y_dev = max(other_object[1], obj[1]) - min(other_object[1], obj[1])

            # adds in a deviation to make a pretty curve for line drawings
            midpoint = (max(obj[0], other_object[0]) - x_dev, max(obj[1], other_object[1]) - y_dev)
            midpoint = (x_dev, y_dev)

            new_connections.append(((obj[0] + pos[0], obj[1] + pos[1]),
                                    (midpoint[0] + pos[0], midpoint[1] + pos[1]),
                                    # (midpoint[0] , midpoint[1] ),
                                    (other_object[0] + pos[0], other_object[1] + pos[1])))

        return new_connections

    def create_connections(self):
        for poi in self.points_of_interest:
            connected = False
            while not connected:
                # num = rand.randint(0,9) #inclusive of upper limit.
                # connection = "city" + str(num)
                other_poi = rand.choice(self.points_of_interest)
                # other_city = self.cities_dict[connection]
                if other_poi.name != poi.name and not (poi.name + other_poi.name in self.connections
                                                       or (other_poi.name + poi.name) in self.connections):
                    connected = self.add_connection(poi, other_poi)
                else:
                    break

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
                distance -= 1 * R.TILE_SIZE / 2
                tries = 0

        if placed:

            return x, y

        else:
            return False, False

    def check_distance(self, x, y, distance):
        for obj in self.points_of_interest:
            if find_length((x, y), (obj.x, obj.y)) > distance:
                return True

        if len(self.points_of_interest) == 0:
            return True

        return False

    def check_mouse_pos(self, mouse_pos, camera_pos, (x, y)=(None, None)):
        if x is None:
            x = mouse_pos[0] - camera_pos[0]
            y = mouse_pos[1] - camera_pos[1]

        for place in self.points_of_interest:
            # TODO: potentially change it to use the places' rect instead of the sprite.
            if place.orig_rect.collidepoint(x,
                                            y):
                return place

        return None

    def make_graph(self):
        self.graph = ai.SolarGraph((self.x, self.y))
        for point in self.points_of_interest:
            point.make_graph()
            node = ai.Node(point.name, point.location, 10, True, point.graph)
            self.graph.add_edge(node)

        for connection in self.connections.values():
            self.graph.add_connection(connection[0], [connection[1]])


class Galaxy:
    def __init__(self):
        self.sectors = []
        self.sector_rects = {}
        self.rects_sectors = {}
        self.connections = {}
        self.parent = None
        self.zoom = "galaxy"

        # self.sprites = SortedUpdates()
        self.w = 0
        self.h = 0

        for x in range(2):
            self.sectors.append([])
            for y in range(2):
                sector, rect = self.create_sector(x, y)
                sector.parent = self

                self.sectors[x].append(sector)
                self.sector_rects[sector] = rect
                self.rects_sectors[
                    rect.topleft] = sector  # Rect is not a hashable object so done it to the topleft tuple instead
                self.w += sector.w
                self.h += sector.h

        self.dimensions = Rect(0, 0, self.w, self.h)

        self.active_sector = self.sectors[0][0]  # set to first for now.

    def create_sector(self, x, y, sector_size=1024):
        sector = Sector(x, y, sector_size)
        rect = Rect(x * sector_size, y * sector_size, sector_size, sector_size)
        sector.dimensions = rect
        # other stuff...
        return sector, rect

    def check_mouse_pos(self, mouse_pos, camera_pos):
        x = mouse_pos[0] - camera_pos[0]
        y = mouse_pos[1] - camera_pos[1]

        print mouse_pos, camera_pos, "=", x, y

        # if self.active_sector.rect.collidepoint(x,y):
        return self.active_sector.check_mouse_pos(mouse_pos, camera_pos, (x, y))

    def graphify_galaxy(self):
        pass
