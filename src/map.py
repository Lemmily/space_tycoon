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
        self.cities = []
        self.cities_dict = {}
        self.connections = {}
        self.sprite = None

        for i in range(20):
            city = City("city" + str(i))
            if self.place_city(city):
                city.sprite = Sprite((city.x * self.tile_width, city.y * self.tile_height), R.TILE_CACHE["data/two.png"], sprite_pos=[0,0])
                                 #(resources.city_img,x=city.x * tile_width + tile_width/2, y=city.y * tile_height + tile_height/2, batch=batch)
                if group != None:
                    group.add(city.sprite)
                # city.sprite.scale = 2

        self.create_connections()

    def place_city(self, city):
        """
        Tries to place the city on the map,
        :param city:
        :return:
        """
        placed = False

        distance = 5
        tries = 0
        while placed == False and distance > 3:
            tries += 1
            x = rand.randint(1, len(self.tiles) - 2)
            y = rand.randint(1, len(self.tiles[x]) - 2)
            city.x,city.y = x,y

            placed = self.check_city_distances(city, distance)
            if tries >= 5:
                distance -= 1
                tries = 0

        if placed:
            self.cities.append(city)
            self.cities_dict[city.name] = city
            self.tiles[city.x][city.y] = city
            return True

        else:
            return False

    def check_city_distances(self, city, distance=8):
        if city.x == -1:
            return False
        for other_city in self.cities:
            dx = abs(city.x - other_city.x)
            dy = abs(city.y - other_city.y)
            if math.sqrt(dx * dx + dy * dy) < distance:
                return False

        return True # good position in terms of distances.

    def create_connections(self):
        for city in self.cities:
            connected = False
            while not connected:
                num = rand.randint(0,9) #inclusive of upper limit.
                # connection = "city" + str(num)
                other_city = rand.choice(self.cities)
                # other_city = self.cities_dict[connection]
                if other_city.name != city.name and not ( self.connections.has_key(city.name + other_city.name) or self.connections.has_key(other_city.name + city.name)):
                    city.connections[other_city.name] = (city.x, city.y, other_city.x, other_city.y)
                    self.connections[city.name + other_city.name] = (city.x, city.y, other_city.x, other_city.y)
                    connected = True

    def check_mouse_pos(self, mouse_pos, cam_pos=(0,0)):
        for city in self.cities:
            if city.sprite.rect.collidepoint(mouse_pos):
                return city
        # tile_pos = ((mouse_pos[0] + 1 + cam_pos[0])/self.tile_width, (mouse_pos[1] + 1 + cam_pos[1])/self.tile_height)
        # if 0 > tile_pos[0] > len(self.tiles) - 1 or  0 > tile_pos[1] > len(self.tiles[0]) - 1:
        #     return None
        return None
        # return self.tiles[tile_pos[0]][tile_pos[1]]
