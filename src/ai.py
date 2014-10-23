from Queue import Queue

__author__ = 'Emily'



class PathFinder():
    def __init__(self):
        self.open_nodes = Queue.PriorityQueue()
        self.node_status = {}
        self.node_costs = {}


    def find_path(self, location, destination, graph):
        route = []

        self.open_nodes = Queue.PriorityQueue()
        self.node_status = {}
        self.node_costs = {}




class PathNode():
    def __init__(self, location, cost, parent=None, end=None):
        self.location = location
        self.direct_cost = cost
        self.cost = 0

        self.parent_node = parent
        self.end_node = end

        if self.end_node != None:
            self.cost = self.direct_cost