from pygame.sprite import Sprite

__author__ = 'Emily'

import random

rand = random.Random()

class City():
    def __init__(self, name, x=-1, y=-1):
        self.name = name
        self.x = x
        self.y = y
        self.connections = {}


class WorldMap():
    def __init__(self, width, height, tile_width=24, tile_height=24, batch=None):
        """

        Sectors?
        :param width: number of tiles wide
        :param height: number of tiles high
        :param tile_width:
        :param tile_height:
        :param batch:
        :return:
        """
        self.width = width
        self.height = height
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.tiles = [[None for j in range(height)] for i in range(width)]
        self.cities = []
        self.cities_dict = {}
        self.connections = {}
        self.sprite = None

        for i in range(10):
            city = City("city" + str(i))
            self.place_city(city)
            city.sprite = Sprite #(resources.city_img,x=city.x * tile_width + tile_width/2, y=city.y * tile_height + tile_height/2, batch=batch)
            city.sprite.scale = 2

        self.create_connections()

    def place_city(self, city):
        """
        Tries to place the city on the map,
        :param city:
        :return:
        """
        placed = False

        distance = 8
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

        else:
            return False

    def check_city_distances(self, city, distance=8):
        if city.x == -1:
            return False
        for other_city in self.cities:
            if max(city.x, other_city.x) - min(city.x, other_city.x) < distance or max(city.y, other_city.y) - min(city.y, other_city.y) < distance:
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

    def check_mouse_pos(self, mouse_pos):
        tile_pos = (mouse_pos[0]/self.tile_width, mouse_pos[1]/self.tile_height)
        return self.tiles[tile_pos[0]][tile_pos[1]]
