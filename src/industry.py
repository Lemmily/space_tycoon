from random import Random
from sets import Set

import pygame as pg
import xml.etree.ElementTree as ET

__author__ = 'Emily'


rand = Random()


# TODO: MAJOR: write in to allow for a building to be assigned a "Job", eg "make copper wire" or "make circuit board".
# This will allow the factory to be set to a specific production and allow the player to reassign it.


# class Job:
#     def __init__(self, resource):
#         pass
#         self.resource = resource # the target resource
#         self.


class Resource:
    def __init__(self, name, location, needs=None, byproducts=None, output=1.0, time=1.0, type=None):
        self.name = name  # or type or w/e like "iron ore"
        self.location = location  # type of building resource is made/gathered in eg, mine/furnace/factory
        self.type = type  # flavour of building, mine ~~> quarry, pump jack, sifting station, blah blah

        if not needs:
            needs = {}
        self.needs = needs  # what's needed to make one unit of this? {Resource: number, Resource: number}
        if not byproducts:
            byproducts = {}  # ## {Resource: (output, chance), Resource: (output, chance)}
        self.byproducts = byproducts  # type & quantity of by products produced when a unit of this resource is created.
        self.time = time
        self.output = output

    def __str__(self):
        return self.name + " " + self.location + " " + self.type

    def __repr__(self):
        return self.name


class Request:
    def __init__(self, resource, amount):
        self.age = 0.0
        self.resource = resource
        self.amount = amount

    def age(self, time):
        self.age += time

    def get_age(self):
        return self.age


class Building:
    def __init__(self, resource=None, depot=None, rate=0.5, variety=None, num=0):
        """
        :param resource:
        :param depot:
        :param rate: production rate for the building.
        :param num:
        :return:
        """
        self.num = num
        self.depot = depot  # the station where this resource is sent to.
        self.resource = resource  # resource produced

        # #TODO: Implement sources. (tie to planet resources deposits)
        self.source = None  # the resource source, eg planet/asteroid/depot/etc
        # self.needs = resource.needs #what resources and how much of it need to produce one resource unit.
        self.base_rate = rate  # # the rate per second at which the resource is mined/produced.
        self.rate = self.base_rate  # the rate at which the resource is mined plus any modifiers/
        self.units = 0.0

        # flavour, changes the name of the building; mine class type could be quarry, mine, pump jack. sift station, etc
        if variety is not None:
            self.variety = variety
        else:
            self.variety = self.__class__.__name__.lower()

        self.input_storage = {}
        self.storage = {}
        self.assign_resource(resource)

        # register with the depot
        self.depot.register(self)

    def __str__(self):
        return self.__class__.__name__, "of type", self.variety, " ", self.num, "producing", self.resource

    def update(self, dt):
        pass

    def pickup_all(self):
        returnables = self.storage.copy()
        for key in self.storage.keys():
            if returnables[key] > 0:
                left_over = returnables[key] % 1
                returnables[key] -= left_over
                self.storage[key] = left_over
        return returnables

    def assign_resource(self, resource):
        self.resource = resource  # resource produced
        if self.resource.needs is not None:
            self.input_storage = {res.name: 0.0 for res in
                                  self.resource.needs.keys()}  # setup storage for incoming resources.

        self.storage[resource.name] = 0.0
        if resource.byproducts is not None:
            for item in resource.byproducts:
                self.storage[item.name] = 0.0

    def receive(self, resources):
        for resource in resources.keys():
            print self.depot.owner, self.variety, self.num, "received", resource, resources[resource]
            self.input_storage[resource] += resources[resource]

    def make_requests(self):
        """
        Goes through each needed resource and checks if there's less than a default amount.
        Makes a request at the depot for a shipment.
        """
        resources = []
        for resource in self.resource.needs.keys():
            if self.input_storage[resource.name] < 5:  # TODO: make the number changeable.
                resources.append(resource)

        self.depot.request(self, resources)

    def all_resources_present(self):
        for resource in self.resource.needs.keys():
            if self.input_storage[resource.name] < self.resource.needs[resource]:
                return False

        return True

    def produce(self, dt):
        """
        produces the output, also does byproducts.
        :param dt:
        :return:
        """
        self.units += self.rate * dt
        if self.units >= self.resource.time:
            for resource in self.resource.needs.keys():
                self.input_storage[resource.name] -= self.resource.needs[resource]  # st instead of int

            self.storage[self.resource.name] += self.resource.output
            self.units = 0.0
            self.produce_byproducts()

    def produce_byproducts(self):
        if self.resource.byproducts is not None:
            for resource in self.resource.byproducts.keys():
                if rand.randint(1, 100) < self.resource.byproducts[resource][1] * 100:
                    self.storage[resource.name] += self.resource.byproducts[resource][0]


class Mine(Building):
    """ Raw resource gathering."""
    def __init__(self, resource, depot, resource_source, rate=0.5, variety="mine"):
        # type flavour, changes the name of the building; mine class type could be quarry, mine, pump jack. sift station
        Building.__init__(self, resource, depot, rate, variety)
        self.source = resource_source

    def update(self, dt):
        if self.all_resources_present():
            # work out how much resource produced.
            # TODO: will need to know how much resource is left at the source.
            # make some resource

            self.produce(dt)
            # print self.units, "units of ", self.resource.name, " and ",
            # self.storage[self.resource.name], " units stored"
            # once resource is multiple of x forward to depot? or depot periodically collects from storage.
        else:
            self.make_requests()

    def all_resources_present(self):
        if Building.all_resources_present(self) and self.check_source():
            return True
        return False

    def check_source(self):
        # TODO:do a check to make sure there's still resources to mine/farm/pump/etc...
        if self.source > self.resource.output:
            return True
        return False


class Furnace(Building):
    def __init__(self, resource, depot, rate=0.5, num=0):
        Building.__init__(self, resource, depot, rate, resource.type, num)

    def update(self, dt):
        if self.all_resources_present():
            # smelt
            self.produce(dt)
            # print self.units, "units of ", self.resource.name, " and ",
            # self.storage[self.resource.name], " units stored"
        else:
            self.make_requests()


class Factory(Building):
    def __init__(self, resource, depot, rate=0.25, num=0):
        Building.__init__(self, resource, depot, rate, None, num)

    def update(self, dt):
        if self.all_resources_present():
            # smelt
            self.produce(dt)
            # print self.units, "units of ", self.resource.name, " and ", self.storage[
            #     self.resource.name], " units stored"
        else:
            self.make_requests()

            # def produce(self, dt):
            #     self.units += self.rate * dt
            #     if self.units >= self.resource.time:
            #         for resource in self.resource.needs.keys():
            #             self.input_storage[resource.name] -= self.resource.needs[resource]
            #
            #         self.storage[self.resource.name] += self.resource.output
            #         self.units = 0.0


class Job:
    """
        A temporary and idealistic view of how the jobs might work. Jobs could be things like "produce goods" or "Repair wall"
        or "Deliver goods" or "pickup goods" or "Construct building".
    """
    def __init__(self):
        # Some kind of job thingy.
        pass

    def update(self, dt):
        # update the job - do your thinnngg
        pass


class Depot:
    def __init__(self, num=0, owner="player"):
        self.name = "Depot " + str(num)
        self.connected_depots = []
        self.storage = {}
        self.buildings = Set()
        self.requests = {}
        self.requests_by_type = {}
        self.producers = {}
        self.owner = owner

        for raw in raw_resources:
            self.storage[raw.name] = 0.0
        for processed in processed_resources:
            self.storage[processed.name] = 0.0

    def __str__(self):
        return self.owner + " " + self.name

    def update(self, dt):
        # collect from all registered buildings.
        # TODO: tell a building to send convoy of goods - which then takes some time.
        for building in self.buildings:
            resources = building.pickup_all()
            for key in resources.keys():
                if key in self.storage:
                    self.storage[key] += resources[key]
                else:
                    self.storage[key] = resources[key]
        self.fulfil_requests()
        print str(self) + ": ", self.storage

    def register(self, building):
        if building not in self.buildings:
            self.buildings.add(building)
            for key in building.storage.keys() and building.input_storage.keys():
                if key not in self.storage:
                    self.storage[key] = 0.0

            if building.resource.name not in self.producers:
                self.producers[building.resource.name] = 1
            else:
                self.producers[building.resource.name] += 1

    def request(self, building, specifics=None):
        # TODO: add in numerical requests.
        if building not in self.requests:
            if specifics is None:
                self.requests[building] = building.needs
            else:
                self.requests[building] = specifics

            for resource in self.requests[building]:
                if resource.name not in self.requests_by_type:
                    self.requests_by_type[resource.name] = []

                self.requests_by_type[resource.name].append(building)
                # TODO: make possible to amend requests, so if a delivery of x has been made, remove x from request.
                # or increase amount if there seems to be a need for it.

    def remove_request(self, building):
        # if not self.requests.has_key(building):
        for resource in self.requests[building]:
            self.requests_by_type[resource.name].remove(building)
        self.requests.pop(building)

    def fulfil_requests(self):
        # TODO: make priority in buildings. iron furnace higher over copper one for example.
        # TODO: make it possible to divide the resources differently, eg via priority.
        resource_division = {}
        for key in self.requests_by_type.keys():
            if len(self.requests_by_type[key]) > 0:
                # if the depot doesn't have any producers, send out a request.
                # TODO: change hardcoded value to an appropriate variable.
                if key not in self.producers and self.storage[key] < 10:
                    self.broadcast_request(key)
                requests = len(self.requests_by_type[key])
                per_request = int(self.storage[key]) / requests
                leftover = self.storage[key] % requests
                resource_division[key] = [per_request, leftover]

        for requester in self.requests.keys():
            delivery = {}
            for resource in self.requests[requester]:
                if resource_division[resource.name][0] > 0:
                    delivery[resource.name] = resource_division[resource.name][0]
                    self.storage[resource.name] -= resource_division[resource.name][0]
            if len(delivery.keys()) > 0:
                requester.receive(delivery)
                self.remove_request(requester)

    def broadcast_request(self, key):
        """ send a request to all connected depots for resources."""

        # DO SOMEWHERE ELSE?
        # # work out what is desperately needed.
        # needed = {resource_dict["slag"]: 5}  # temp example of resource request.
        requests = [resource_dict[key]]
        # go through and ask for the resource.
        for depot in self.connected_depots:
            # TODO: check if the depot is a producer? or just blanket send?
            depot.request(self, requests)

    def make_connection(self, depot):
        if depot not in self.connected_depots:
            self.connected_depots.append(depot)
            if self not in depot.connected_depots:
                depot.make_connection(self)
            print self, "connected to", depot

    def receive(self, resources):
        print str(self), "received", resources
        for resource in resources.keys():
            self.storage[resource] += resources[resource]


class IndustryManager:
    """
    temporary testing for industry stuffs


    this should eventually be part of the planets/locations. it will run the industries.

    """

    def __init__(self, owner="player"):
        global processed_resources, raw_resources

        self.ticks = 0
        self.buildings = []
        self.building_by_type = {"mine": [], "furnace": [], "factory": []}
        depot = Depot(1, owner)
        self.add_building(
            Factory(resource_dict["circuit board"], depot, rate=0.25 + float(rand.randint(-10, 10) / 100.0), num=0))
        self.add_building(
            Factory(resource_dict["circuit board"], depot, rate=0.25 + float(rand.randint(-10, 10) / 100.0), num=1))
        self.add_building(
            Factory(resource_dict["circuit board"], depot, rate=0.25 + float(rand.randint(-10, 10) / 100.0), num=2))

        self.depots = [self.create_depot_with_buildings(0, owner)]
        depot.make_connection(self.depots[0])
        self.depots.append(depot)

    def create_depot_with_buildings(self, num, owner):
        depot = Depot(num, owner)

        # Mine based production
        for i in range(10):
            rate = 0.75 + float(rand.randint(-10, 10) / 100.0)

            if i < 4:
                resource = resource_dict["fuel"]
            elif i < 6:
                resource = resource_dict["copper ore"]
            elif i < 9:
                resource = resource_dict["iron ore"]
            else:
                resource = resource_dict["stone"]

            building = Mine(resource, depot, 5000, rate=rate)
            self.add_building(building)

        # Furnace based production
        for i in range(7):
            if i < 3:
                resource = resource_dict["iron bar"]
            elif i < 7:
                resource = resource_dict["copper plate"]
            else:
                resource = resource_dict["stone brick"]

            rate = 0.5 + float(rand.randint(-10, 10) / 100.0)
            building = Furnace(resource, depot, rate=rate)
            self.add_building(building)

        # Factory based stuffs.
        for i in range(3):
            rate = 0.25 + float(rand.randint(-10, 10) / 100.0)
            if i <= 2:
                resource = resource_dict["copper wire"]
            else:
                resource = resource_dict["circuit board"]
            building = Factory(resource, depot, rate=rate)
            self.add_building(building)

        return depot

    def update(self, dt):
        for building in self.building_by_type["mine"]:
            building.update(dt)
        for building in self.building_by_type["furnace"]:
            building.update(dt)
        for building in self.building_by_type["factory"]:
            building.update(dt)

        self.ticks += 1
        if self.ticks % 30 == 0:
            # only do fetches from buildings every 30 ticks or so
            for depot in self.depots:
                depot.update(dt)

    def add_building(self, building):
        self.buildings.append(building)
        self.building_by_type[building.__class__.__name__.lower()].append(building)

    def get_producing(self):
        resources = []
        for depot in self.depots:
            for resource in depot.producers.keys():
                resources.append(resource_dict[resource])

        return resources


class EconomyManager:
    def __init__(self, products):
        # Manages economic viability. Needs to know which products are required for the things it's trying to produce.
        self.resources = {}
        self.products = products
        for resource in products:
            for need in resource.needs.keys():
                if need in self.resources.keys():
                    self.resources[need] += resource.needs[need]
                else:
                    self.resources[need] = resource.needs[need]

    def update(self, dt):
        # go through requests and see if they are needed?
        pass


def main():
    global raw_resources, processed_resources, resource_dict

    pg.init()
    # pg.display.set_mode((1440, 768))
    # pg.display.set_caption('space trader tycoon')
    clock = pg.time.Clock()
    # pg.display.flip()

    industry_manager = IndustryManager("player")
    alien_industry_manager = IndustryManager("alien")

    economy_manager = EconomyManager(industry_manager.get_producing())
    alien_economy_manager = EconomyManager(alien_industry_manager.get_producing())

    while not game_over:
        dt = 1 / float(clock.tick(30))

        industry_manager.update(dt)
        alien_industry_manager.update(dt)

        economy_manager.update(dt)
        alien_economy_manager.update(dt)

        handle_events()


def handle_events():
    global game_over
    for event in pg.event.get():
        # print event
        if event.type == pg.QUIT:
            game_over = True

# ##
# ##
# ## static variables for a master list of resources.
# ##
# ##
raw_resources = []
processed_resources = []
manufactured_resources = []
resource_dict = {}  # lookup by name.


def parse_resources(res, t_resources):
    # do raw things
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
        amount = float(byproduct.attrib["amount"])
        chance = float(byproduct.attrib["chance"])
        byproducts.append((type_res, amount, chance))
    needs = []
    # sort out the needs, will need to hook up the correct resource object later.
    for need in res.findall("need"):
        type_res = need.attrib["type"]
        amount = float(need.attrib["amount"])
        needs.append((type_res, amount))

    resource = Resource(name, location, output=output, time=time, type=type)
    t_resources.append((resource, needs, byproducts))
    resource_dict[name] = resource
    return t_resources


def hook_up_resources(entry, resource_table):
        res = entry[0]
        needs = entry[1]
        byproducts = entry[2]
        entry = None

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

        resource_table.append(res)


def construct_resources_tables():
    global raw_resources, processed_resources, resource_dict

    tree = ET.parse('data/resources.xml')
    root = tree.getroot()

    t_raw_resources = []
    t_processed_resources = []
    t_manufactured_resources = []

    for res in root.findall("raw"):
        parse_resources(res, t_raw_resources)

    for res in root.findall("processed"):
        parse_resources(res, t_processed_resources)

    for res in root.findall("manufactured"):
        # do raw things
        parse_resources(res, t_manufactured_resources)

    # Now, hook up the resource objects to the needs of processed resources.
    for entry in t_raw_resources:
        hook_up_resources(entry, raw_resources)

    for entry in t_processed_resources:
        hook_up_resources(entry, processed_resources)

    for entry in t_manufactured_resources:
        hook_up_resources(entry, manufactured_resources)


construct_resources_tables()

game_over = False

main()
