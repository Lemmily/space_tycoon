import math
from src import R
from src.render import Sprite

__author__ = 'Emily'

import random

rand = random.Random()

class City():
    def __init__(self, name, x=-1, y=-1):
        self.name = name
        self.x = x
        self.y = y
        self.connections = {}


class WorldMap:
    def __init__(self, width, height, tile_width=24, tile_height=None, group=None):
        """

        Sectors?
        :param width: number of tiles wide
        :param height: number of tiles high
        :param tile_width:
        :param tile_height:
        :param batch:
        :return:
        """
        self.width = width #* tile_width #stored as pixels
        self.height = height #* (tile_height or tile_width)
        self.tile_width = tile_width
        self.tile_height = tile_height or tile_width
        self.tiles = [[None for j in range(height/tile_width)] for i in range(width/tile_width)]
        self.planets = []
        self.cities_dict = {}
        self.connections = {}
        self.sprite = None

        for i in range(20):
            planet = City("city" + str(i))
            if self.place_planet(planet):
                planet.sprite = Sprite((planet.x, planet.y), R.TILE_CACHE["data/two.png"], sprite_pos=[0,0])
                if group != None:
                    group.add(planet.sprite)
                # city.sprite.scale = 2

        self.create_connections()

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
            x = rand.randint(self.tile_width, len(self.tiles * self.tile_width) - self.tile_width - 1)
            y = rand.randint(self.tile_width, len(self.tiles[x/self.tile_width] * self.tile_width) - self.tile_width - 1)
            # y = rand.randint(1, len(self.tiles[x]) - 2)
            planet.x,planet.y = x,y

            placed = self.check_planet_distances(planet, distance)
            if tries >= 5:
                distance -= 1
                tries = 0

        if placed:
            self.planets.append(planet)
            self.cities_dict[planet.name] = planet
            self.tiles[planet.x/self.tile_width][planet.y/self.tile_width] = planet
            return True

        else:
            return False

    def check_planet_distances(self, planet, distance=8):
        if planet.x == -1:
            return False
        for other_city in self.planets:
            dx = abs(planet.x - other_city.x)
            dy = abs(planet.y - other_city.y)
            if math.sqrt(dx * dx + dy * dy) < distance:
                return False

        return True # good position in terms of distances.

    def create_connections(self):
        for planet in self.planets:
            connected = False
            while not connected:
                num = rand.randint(0,9) #inclusive of upper limit.
                # connection = "city" + str(num)
                other_city = rand.choice(self.planets)
                # other_city = self.cities_dict[connection]
                if other_city.name != planet.name and not ( self.connections.has_key(planet.name + other_city.name) or self.connections.has_key(other_city.name + planet.name)):
                    planet.connections[other_city.name] = ((planet.x, planet.y), (other_city.x, other_city.y))
                    midpoint = (max(planet.x, other_city.x) - abs(planet.x - other_city.x)/3, max(planet.y, other_city.y) - abs(planet.y - other_city.y)/3)
                    self.connections[planet.name + other_city.name] = ((planet.x, planet.y), midpoint, (other_city.x, other_city.y))
                    connected = True

    def check_mouse_pos(self, mouse_pos, cam_pos=(0,0)):
        for object in self.planets:
            if object.sprite.rect.collidepoint(mouse_pos):
                return object
        # tile_pos = ((mouse_pos[0] + 1 + cam_pos[0])/self.tile_width, (mouse_pos[1] + 1 + cam_pos[1])/self.tile_height)
        # if 0 > tile_pos[0] > len(self.tiles) - 1 or  0 > tile_pos[1] > len(self.tiles[0]) - 1:
        #     return None
        return None
        # return self.tiles[tile_pos[0]][tile_pos[1]]

    def get_connections(self, connection, camera):
        offset = camera.state.topleft
        new_connections = []
        for pair in connection:
            new_connections.append((pair[0] + offset[0], pair[1] + offset[1]))

        return new_connections

