# from Queue import Queue

__author__ = 'Emily'


import heapq


class Graph:
    def __init__(self, location=(0,0)):
        self.nodes = {}
        self.edges = {}

    def neighbours(self, id):
        return self.edges[id]

    def add_edge(self, node, neighbours = []):
        self.nodes[node] = node
        self.edges[node] = neighbours

    def add_connection(self, node, new_neighbours):
        if self.edges.has_key(node):
            (self.edges[node].append(neighbour) for neighbour in new_neighbours)

    def cost(self, a, b):
        return self.nodes.get(a).cost(self.nodes.get(b))



class SolarGraph(Graph):
    def __init__(self):
        super.__init__(self)

    def get_child(self, location):
        return self.nodes.get(location).get_child()





class PriorityQueue:
   def __init__(self):
      self.elements = []

   def empty(self):
      return len(self.elements) == 0

   def put(self, item, priority):
      heapq.heappush(self.elements, (priority, item))

   def get(self):
      return heapq.heappop(self.elements)[1]



class PathFinder():
    def __init__(self):
        self.frontier = PriorityQueue()
        self.came_from = {}
        self.cost_so_far = {}


    def dijkstra_search(self, graph, start, goal):
        #todo: factor in the technology - can the ship travel the distances between nodes?
        #todo: possibly havea seperate function that constructs a graph of reachable nodes to use for this.
        self.frontier = PriorityQueue()
        self.frontier.put(start, 0)

        self.came_from = {}
        self.cost_so_far = {}
        self.came_from[start] = None
        self.cost_so_far[start] = 0

        while not self.frontier.empty():
            current = self.frontier.get()

            if current == goal:
                break

            for next in graph.neighbours(current):
                new_cost = self.cost_so_far[current] + graph.cost(current, next)
                if next not in self.cost_so_far or new_cost < self.cost_so_far[next]:
                    self.cost_so_far[next] = new_cost  #cost
                    priority = new_cost
                    self.frontier.put(next, priority)
                    self.came_from[next] = current

        return self.came_from, self.cost_so_far


    def a_star(self, graph, start, goal):
        #todo: factor in the technology - can the ship travel the distances between nodes?
        #todo: possibly havea seperate function that constructs a graph of reachable nodes to use for this.
        self.frontier = PriorityQueue()
        self.frontier.put(start, 0)

        self.came_from = {}
        self.cost_so_far = {}
        self.came_from[start] = None
        self.cost_so_far[start] = 0

        while not self.frontier.empty():
            current = self.frontier.get()

            if current == goal:
                break

            for next in graph.neighbours(current):
                new_cost = self.cost_so_far[current] + graph.cost(current, next)
                if next not in self.cost_so_far or new_cost < self.cost_so_far[next]:
                    self.cost_so_far[next] = new_cost + heuristic(goal, next) # cost, plus distance to end.
                    priority = new_cost
                    self.frontier.put(next, priority)
                    self.came_from[next] = current

        return self.came_from, self.cost_so_far


    def reconstruct_path(self, came_from, start, goal):
        current = goal
        path = [current]
        while current != start:
            current = came_from[current]
            path.append(current)

        return path



class Node():
    def __init__(self, name, location, cost, solar=False, child=None): #parent=None, end=None):
        self.name = name
        self.location = location #tuple? (x,y)
        self.direct_cost = cost #cost of entering node
        self.solar = solar
        self.child = child #graph of solar system/object/thing this node represents
        #
        # self.cost = self.direct_cost

    def cost(self, node):
        """

        :param node: other node
        :return: direct cost of entry of other node plus distance.
        """
        return node.direct_cost + heuristic(self.location, node.location)


    def get_child(self):
        return self.child

    def __str__(self):
        return str(self.location)

    def __hash__(self):
        # print(hash(str(self)))
        return hash(str(self))

    def __eq__(self, other):
        return hash(str(self)) == hash(str(other))


def heuristic(a, b):
   (x1, y1) = a
   (x2, y2) = b
   return abs(x1 - x2) + abs(y1 - y2)


# graph = Graph()
#
# a = Node("A", (10,10), 10)
# graph.add_edge(a, [(30,15),(0,60)])
# graph.add_edge(Node("B", (30,15), 100), [(15,70),(30,60)])
# graph.add_edge(Node("C", (30,60), 15), [(0,0)])
# graph.add_edge(Node("D", (15,70), 10), [(30,60)])
# graph.add_edge(Node("E", (0,60), 15), [(30,15), (15,70)])
#
# pather = PathFinder()
#
# a,b = pather.dijkstra_search(graph, (10,10), (30,60))
# c,d = pather.dijkstra_search(graph, (10,10), (30,60))
# path = pather.reconstruct_path(a,(10,10), (30,60))
# print "djikstra", path
# path = pather.reconstruct_path(c,(10,10), (30,60))
# print "a_star", path