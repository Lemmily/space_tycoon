
from random import Random
from sets import Set

__author__ = 'Emily'

import pygame as pg
import xml.etree.ElementTree as ET

rand = Random()

#TODO: MAJOR: write in to allow for a building to be assigned a "Job".
#This will allow the factory to be set to a specific production and allow the player to reassign it.


# class Job:
#     def __init__(self, resource):
#         pass
#         self.resource = resource # the target resource
#         self.


class Resource:
    def __init__(self, name, location, needs=None, byproducts=None, output=1.0, time=1.0, type=None):
        self.name = name # or type or w/e like "iron ore"
        self.location = location # type of building resource is made/gathered in eg, mine/furnace/factory
        self.type = type # flavour of building, mine ~~> quarry, pump jack, sifting station, blah blah

        if not needs: needs = {}
        self.needs = needs #what's needed to make one unit of this? {Resource: number, Resource: number}
        if not byproducts: byproducts = {}  ### {Resource: (output, chance), Resource: (output, chance)}
        self.byproducts = byproducts #type and quantity of by products produced when a unit of this resource is created.
        self.time = time
        self.output = output

    def produce_byproducts(self):
        if self.byproducts != None:
            byproducts=[]
            for resource in self.byproducts:
                pass


            return byproducts

class Building:
    def __init__(self, resource, depot, rate=0.5):
        """

        :param resource:
        :param depot:
        :param rate: production rate for the building.
        :return:
        """
        self.depot = depot # the station where this resource is sent to.
        self.resource = resource # resource produced
        self.source = None # the resource source, eg planet/asteroid/depot/etc #TODO: Implement. (tie to planet resources)
        # self.needs = resource.needs #what resources and how much of it need to produce one resource unit.
        self.base_rate = rate #  # the rate per second at which the resource is mined/produced.
        self.rate = self.base_rate# the rate at which the resource is mined plus any modifiers/
        self.units = 0.0

        #flavour, changes the name of the building A mine class type could be quarry, mine, pump jack. sift station, etc
        if type != None:
            self.type = type
        else:
            self.type = self.__class__.__name__.lower()

        if self.resource.needs != None:
            self.input_storage = {res.name:0 for res in self.resource.needs.keys()} #setup storage for incoming resources.


        self.storage = {resource.name: 0}
        if resource.byproducts != None:
            for item in resource.byproducts:
                self.storage[item.name] = 0

        #register with the depot
        self.depot.register(self)

    def update(self, dt):
        pass

    def pickup_all(self):
        returnables = self.storage.copy()
        for key in self.storage.keys():
            self.storage[key] = 0
        return returnables

    def receive(self, resources):
        for resource in resources.keys():
            self.input_storage[resource] += resources[resource]


    def make_request(self):
        resources = []
        for resource in self.resource.needs.keys():
            if self.input_storage[resource.name] < 5: #TODO: make the number changeable.
                resources.append(resource)

        self.depot.request(self, resources)

    def all_resources_present(self):
        for resource in self.resource.needs.keys():
            if self.input_storage[resource.name] < self.resource.needs[resource]:
                return False

        return True

    def produce(self, dt):
        self.units += self.rate * dt
        if self.units >= self.resource.time:
            for resource in self.resource.needs.keys():
                self.input_storage[resource.name] -= self.resource.needs[resource]

            self.storage[self.resource.name] += self.resource.output
            self.units = 0.0


class Mine(Building):
    def __init__(self, resource,  depot, rate=0.5, type="mine"):
        Building.__init__(self, resource, depot, rate)

    def update(self, dt):
        #work out how much resource produced.
        #TODO: will need to know how much resource is left at the source.
        #make some resource

        self.produce(dt)
        print self.units, "units of ", self.resource.name, " and ", self.storage[self.resource.name], " units stored"
            #once resource is multiple of x forward to depot? or depot periodically collects from storage.

        # pass



class Furnace(Building):
    def __init__(self, resource, depot, rate=0.5):
        Building.__init__(self, resource, depot, rate)

    def update(self, dt):
        if self.all_resources_present():
            #smelt
            self.produce(dt)
            print self.units, "units of ", self.resource.name, " and ", self.storage[self.resource.name], " units stored"
        else:
            self.make_request()






class Factory:
    def __init__(self, resource, depot, rate=0.25):
        Building.__init__(self, resource, depot, rate)


    def update(self, dt):
        if self.all_resources_present():
            #smelt
            self.produce(dt)
            print self.units, "units of ", self.resource.name, " and ", self.storage[self.resource.name], " units stored"
        else:
            self.make_request()

    def produce(self, dt):
        self.units += self.rate * dt
        if self.units >= self.resource.time:
            for resource in self.resource.needs.keys():
                self.input_storage[resource.name] -= self.resource.needs[resource]

            self.storage[self.resource.name] += self.resource.output
            self.units = 0.0


class Depot:
    def __init__(self):
        self.storage = {}
        self.buildings = Set()
        self.requests = {}
        self.requests_by_type = {}

        for raw in raw_resources:
            self.storage[raw.name] = 0.0
        for processed in processed_resources:
            self.storage[processed.name] = 0.0

    def update(self, dt):
        for building in self.buildings:
            resources = building.pickup_all()
            for key in resources.keys():
                self.storage[key] += resources[key]
        self.fulfil_requests()
        print self.storage

    def register(self, building):
        if building not in self.buildings:
            self.buildings.add(building)
            for key in building.storage.keys():
                if not self.storage.has_key(key):
                    self.storage[key] = 0

    def request(self, building, specifics=None):

        if not self.requests.has_key(building):
            if specifics == None:
                self.requests[building] = building.needs
            else:
                self.requests[building] = specifics

            for resource in self.requests[building]:
                if not self.requests_by_type.has_key(resource.name):
                    self.requests_by_type[resource.name] = []

                self.requests_by_type[resource.name].append(building)
        #TODO: make possibly to amend requests


    def fulfil_requests(self):
        #TODO: make priority in buildings. iron furnace higher over copper one for example.
        #TODO: make it possible to divide the resources differently, eg via priority.
        resource_division = {}
        for key in self.requests_by_type.keys():
            if len(self.requests_by_type[key]) > 0:
                requests =len(self.requests_by_type[key])
                per_request = self.storage[key] / requests
                leftover =  self.storage[key] % requests
                resource_division[key] = [per_request, leftover]
        for requester in self.requests.keys():
            delivery = {}
            for resource in self.requests[requester]:
                delivery[resource.name] = resource_division[resource.name][0]
                self.storage[resource.name] -= resource_division[resource.name][0]
            requester.receive(delivery)




class IndustryManager:
    """ temporary testing for industry stuffs
    """
    def __init__(self, depot):
        global processed_resources, raw_resources


        self.ticks = 0
        self.depot = depot
        self.buildings = []
        self.building_by_type = {"mine":[], "furnace": [], "factory": []}

        for i in range(5):
            rate = 0.75 + float(rand.randint(-10,10)/100.0)
            building =  Mine(raw_resources[0], depot, rate=rate )
            self.buildings.append(building)
            self.building_by_type["mine"].append(building)
        for i in range(5):
            rate = 0.5 + float(rand.randint(-10,10)/100.0)
            building =  Mine(raw_resources[1], depot, rate=rate)
            self.buildings.append(building)
            self.building_by_type["furnace"].append(building)

        for i in range(5):
            rate = 0.25 + float(rand.randint(-10,10)/100.0)
            building = Furnace(processed_resources[0], depot, rate=rate)
            self.buildings.append(building)
            self.building_by_type["factory"].append(building)


    def update(self, dt):
        for building in self.building_by_type["mine"]:
            building.update(dt)
        for building in self.building_by_type["furnace"]:
            building.update(dt)
        for building in self.building_by_type["factory"]:
            building.update(dt)

        self.ticks += 1
        if self.ticks > 30:
            #only do fetches from buildings every 30 ticks or so
            self.depot.update(dt)
            self.ticks -= 30


def main():
    global raw_resources, processed_resources, resource_dict

    # iron_ore = Resource("iron ore", "mine")
    # copper_ore = Resource("copper ore", "mine")
    # fuel = Resource("fuel", "mine")
    # iron_plate = Resource("iron plate", "furnace", needs={iron_ore: 1, fuel: 1})
    # copper_plate = Resource("copper plate", "furnace", needs={copper_ore: 1, fuel: 1})
    #
    #
    # # iron_bar = Resource("iron bar", "factory", needs=[(iron_plate, 2)])
    # # copper_wire = Resource("copper wire", "factory", needs=[(copper_plate, 2)], output=3)
    # #
    # # circuit = Resource("circuit board", "factory", needs= [(iron_plate, 1), (copper_wire, 2)])
    #
    # raw_resources = [iron_ore, copper_ore, fuel]
    # processed_resources = [iron_plate, copper_plate ] #iron_bar, copper_wire, circuit
    pg.init()
    pg.display.set_mode((1440, 768))
    pg.display.set_caption('space trader tycoon')
    clock = pg.time.Clock()
    pg.display.flip()

    industry_manager = IndustryManager(Depot())
    while not game_over:
        dt = 1/float(clock.tick(30))

        industry_manager.update(dt)

        handle_events()

def handle_events():
    global game_over
    for event in pg.event.get():
        # print event
        if event.type == pg.QUIT:
            game_over = True


raw_resources = []
processed_resources = []
resource_dict = {} # lookup by name.

def construct_resources_tables():
    global raw_resources, processed_resources, resource_dict

    tree = ET.parse('data/resources.xml')
    root = tree.getroot()

    # raw_resources_t = [] # dont need this because dont need to make any connections
    t_processed_resources = []

    for res in root.findall("raw"):
        #do raw things
        name = res.attrib["name"]
        location = res.find("location").text
        if len(res.find("location").attrib) > 0:
            type = res.find("location").attrib["name"]
        else:
            type = None
        output = float(res.find("output").text)
        time = float(res.find("time").text)

        resource = Resource(name, location, output=output, time=time, type=type)
        raw_resources.append(resource)
        resource_dict[name] = resource


    # Now do the processed ones, these take a bit more work.
    for res in root.findall("processed"):
        #do raw things
        name = res.attrib["name"]
        location = res.find("location").text
        if len(res.find("location").attrib) > 0:
            type = res.find("location").attrib["name"]
        else:
            type = None
        output = float(res.find("output").text)
        time = float(res.find("time").text)
        byproducts = []
        for byproduct in res.findall("byproduct"):
            type_res = byproduct.attrib["type"]
            amount = byproduct.attrib["amount"]
            chance = byproduct.attrib["chance"]
            byproducts.append((type_res, amount, chance))
        needs = []
        #sort out the needs, will need to hook up the correct resource object later.
        for need in res.findall("need"):
            type_res = need.attrib["type"]
            amount = need.attrib["amount"]
            needs.append((type_res, amount))

        resource = Resource(name, location, output=output, time=time, type=type)
        t_processed_resources.append((resource, needs, byproducts))
        resource_dict[name] = resource


    for entry in t_processed_resources:
        res = entry[0]
        needs = entry[1]
        byproducts = entry[2]
        entry=None

        if len(needs) > 0:
            final_needs = {}
            for entry in needs:
                type_res = entry[0]
                amount = entry[1]
                final_needs[resource_dict[type_res]] = amount
            res.needs = final_needs
        else:
            res.needs = {}

        if len(byproducts) > 0:
            final_byprods = {}
            for entry in byproducts:
                type_res = entry[0]
                amount = entry[1]
                chance = entry[2]
                final_byprods[resource_dict[type_res]] = (amount, chance)
            res.byproducts = final_byprods
        else:
            res.byproducts = {}

        processed_resources.append(res)


construct_resources_tables()

game_over = False

main()


