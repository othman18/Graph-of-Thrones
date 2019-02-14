import xml.etree.ElementTree

import h3graph.calc as calc
import h3graph.draw as draw
import statistics

NODE_RADIUS = 40


class Graph(object):

    def __init__(self, nodes=list(), edges=list()):
        self.nodes = nodes
        self.edges = edges
        self.max_edge_count = 0
        self.median_edge_count = 0
        self.mean_edge_count = 0

    def add_node(self, node):
        if type(node) != Node:
            raise TypeError("Type must be H3Node")

        existing_node = self.find_node_by_id(node.id)
        if existing_node is not None:
            self.remove_node(existing_node)

        self.nodes.append(node)
        return node

    def add_new_node(self, id, **properties):
        node = Node(id, **properties)
        return self.add_node(node)

    def remove_node_by_id(self, id):
        node = self.find_node_by_id(id)
        self.remove_node(node)

    def remove_node(self, node):
        if node is None:
            return
        self.remove_edges_by_node(node)
        self.nodes.remove(node)

    def add_edge(self, edge):
        if type(edge) != Edge:
            raise TypeError("Type must be H3Edge")

        self.edges.append(edge)
        return edge

    def add_new_edge(self, source_node, target_node, directed=False, **properties):
        edge = Edge(source_node, target_node, directed, **properties)
        return self.add_edge(edge)

    def remove_edges_by_node(self, node):
        # edgesToRemove = []
        for edge in self.edges:
            if edge.sourceNode == node or edge.targeteNode == node:
                self.edges.remove(edge)
                # edgesToRemove.append(node)
        # self.edges.remove(edgesToRemove)

    def add_new_edge_by_ids(self, source_node_name, target_node_name, directed=False, **properties):
        src = self.find_node_by_id(source_node_name)
        trgt = self.find_node_by_id(target_node_name)
        if src is not None and trgt is not None:
            return self.add_new_edge(src, trgt, directed, **properties)
        return None

    def get_nodes(self):
        return self.nodes

    def get_edges(self):
        return self.edges

    def find_node_by_id(self, id):
        for node in self.nodes:
            if node.id == id:
                return node
        return None

    def sort_nodes_by_property(self, property_name):
        self.nodes.sort(key=lambda node: str(getattr(node, property_name, '')))

    def load(self, path):
        # Parse graphml
        e = xml.etree.ElementTree.parse(path)

        # Build the graph
        # iterate all nodes
        for x in e.find("graph").findall("node"):
            id = int(x.attrib["id"])
            properties = dict()

            for data in x.findall("data"):
                k = data.get("key")
                v = data.text
                properties[k] = v

            node = Node(id, **properties)
            self.add_node(node)

        # iterate all edges
        for x in e.find("graph").findall("edge"):
            # all edges are directed by default, else attribute directed="false" is attached
            # all edges have an element <data key="relation">...</data>
            src = self.find_node_by_id(int(x.attrib["source"]))
            trgt = self.find_node_by_id(int(x.attrib["target"]))

            properties = dict()
            for d in x.findall("data"):
                # k = x.findall("data")[0].get("key")
                # v = x.findall("data")[0].text
                k = d.attrib["key"]
                v = d.text
                properties[k] = v

            directed = x.get("directed") != "false"

            edge = Edge(src, trgt, directed, **properties)
            self.add_edge(edge)

    def add_edge_count_to_nodes(self):
        for e in self.edges:
            for node in [e.sourceNode, e.targetNode]:
                curr_edge_count = node.get("edge_count")
                if curr_edge_count is None:
                    node.update_properties(edge_count=1)
                else:
                    node.update_properties(edge_count=curr_edge_count + 1)

    def calc_statistics(self):
        """place for calculating further properties of the graph"""
        nb_edges = [n.edge_count for n in self.nodes]
        self.max_edge_count = max(nb_edges)
        print("max nb edges:", self.max_edge_count)
        self.median_edge_count = statistics.median(nb_edges)
        print("median nb edges:", self.median_edge_count)
        self.mean_edge_count = statistics.mean(nb_edges)
        print("mean nb edges:", self.mean_edge_count)

    def define_node_positions(self):

        # Make house-birth characters neighbours
        self.sort_nodes_by_property("house-birth")

        # Find nodes that have a single edge only an reposition them:
        single_edge_nodes = self.get_single_edge_nodes()

        # Calculate counts on each circle
        total_node_count = len(self.nodes)
        main_circle_nodes = total_node_count - len(single_edge_nodes)

        # calculate all possible circle positions
        positions = calc.calc_positions(main_circle_nodes, draw.WIDTH_IN_MM, draw.HEIGHT_IN_MM, 400 * calc.POS_SCALE)
        outer_circle_positions = calc.calc_positions(main_circle_nodes, draw.WIDTH_IN_MM, draw.HEIGHT_IN_MM, 450 * calc.POS_SCALE)

        index = 0
        for node in self.nodes:
            if node in single_edge_nodes:
                continue

            node.x = positions[index][0]
            node.y = positions[index][1]

            index = index + 1

        # positioning single edge nodes
        for sen in single_edge_nodes:
            neighbours = self.get_neighbours_of(sen)
            if (len(neighbours) > 0):
                (x, y) = calc.get_nearest_position(outer_circle_positions, neighbours[0].x, neighbours[0].y)
                outer_circle_positions.remove((x, y))
                sen.x = x
                sen.y = y

    def get_single_edge_nodes(self):
        nodeToEdgeCount = dict()

        for e in self.edges:
            for n in [e.sourceNode, e.targetNode]:
                if e.targetNode.name == "Olly" or e.sourceNode.name == "Olly":
                    nodeToEdgeCount[n] = 0
                if e.targetNode.name == "Drogo" or e.sourceNode.name == "Drogo":
                    nodeToEdgeCount[n] = 0
                if e.targetNode.name == "Beric Dondarrion" or e.sourceNode.name == "Beric Dondarrion":
                    nodeToEdgeCount[n] = 0
                if e.targetNode.name == "Shae" or e.sourceNode.name == "Shae":
                    nodeToEdgeCount[n] = 0
                #if e.targetNode.name == "Night King" or e.sourceNode.name == "Night King":
                #    nodeToEdgeCount[n] = 0
                if e.targetNode.name == "Alliser Thorne" or e.sourceNode.name == "Alliser Thorne":
                    nodeToEdgeCount[n] = 0
                currentCount = nodeToEdgeCount.get(n)
                if currentCount is None:
                    currentCount = 0
                currentCount = currentCount + 1
                nodeToEdgeCount[n] = currentCount

        resultList = []

        for key in nodeToEdgeCount:
            if nodeToEdgeCount[key] == 1:
                resultList.append(key)

        return resultList

    def get_neighbours_of(self, node):
        result = []
        for e in self.edges:
            if e.sourceNode == node or e.targetNode == node:
                if e.sourceNode != node:
                    result.append(e.sourceNode)
                if e.targetNode != node:
                    result.append(e.targetNode)
        return result

    def update_graph(self):
        """executes all manipulating functions"""
        self.add_edge_count_to_nodes()
        self.calc_statistics()

    def draw(self):
        draw.draw_graph(self)


class Node(object):

    def __init__(self, id, **properties):
        """Initializes a node/vertex.

        :param id: The id of the node.
        :type id: int
        :param properties: The keyword arguments that are added as properties to the Node.

        You can define the properties of a node yourself:
        >>> node_1 = Node(1, status='Alive', width=5)
        >>> node_1.id
        1
        >>> node_1.status
        'Alive'
        >>> node_1.width
        5
        >>> node_2 = Node(2, my_special_property='killer')
        >>> node_2.my_special_property
        'killer'

        If you want to load a dict:
        >>> properties =  {'status': 'Alive', 'width': 5}
        >>> node_3 = Node(3, **properties)
        """
        self.id = id
        for (key, value) in properties.items():
            setattr(self, key, value)

    def __str__(self):
        return '{this_class}{properties}'.format(this_class=self.__class__,
                                                 properties=self.__dict__)

    def update_properties(self, **properties):
        """Update or insert a new property of an edge.

        :param properties: The keyword arguments that are added as properties to the node.

        The following command updates the status and adds a new properties:
        >>> node_1 = Node(1, status='Alive', width=5)
        >>> node_1.update_properties(status='Alive', width=66, color='blue')
        >>> node_1.__dict__
        {'id': 1, 'status': 'Alive', 'width': 66, 'color': 'blue'}
        """
        for (key, value) in properties.items():
            setattr(self, key, value)

    def get(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        return None

    def fulfills_all_properties(self, **properties):
        """
        Checks if all of the properties are fulfilled.
        (The properties are connected by AND)

        :param properties: The keyword arguments to check if fulfilled
        :return: True, if all properties are fulfilled otherwise False.
        :type: bool

        >>> node = Node(1, status='Alive', group='Brotherhood Without Banners')
        >>> node.fulfills_all_properties(status='Alive', group='Brotherhood Without Banners')
        True
        >>> node.fulfills_all_properties(status='Deceased', group='Brotherhood Without Banners')
        False
        >>> node.fulfills_all_properties(status='Alive', group='Brotherhood Without Banners', name='Drogon')
        False
        >>> properties =  {'id': 1, 'house-birth': 'House Clegane', 'width': 66}
        >>> node = Node(**properties)
        >>> property = {'house-birth': 'House Clegane'}
        >>> node.fulfills_all_properties(**property)
        True
        """
        curr_properties = self.__dict__
        for (key, value) in properties.items():
            if key not in curr_properties or value != curr_properties[key]:
                return False
        return True


class Edge(object):

    def __init__(self, source_node, target_node, directed=False, **properties):
        """Initializes an edge.

        :param source_node: The source node of the edge.
        :type source_node: Node
        :param target_node: The target node of the edge.
        :type target_node: Node
        :param directed: whether the edge is directed.
        :type directed: bool
        :param properties: The keyword arguments that are added as properties to the edge.

        You can define the properties of a edge yourself:
        >>> node_1 = Node(1)
        >>> node_2 = Node(2)
        >>> edge_1_2 = Edge(node_1, node_2, True, relation='killed')
        >>> edge_1_2.relation
        'killed'
        """
        self.sourceNode = source_node
        self.targetNode = target_node
        self.directed = directed
        for (key, value) in properties.items():
            setattr(self, key, value)

    def __str__(self):
        # TODO(gitdown) return node ids of source and target nodes.
        return '{this_class}{properties}'.format(this_class=self.__class__,
                                                 properties=self.__dict__)

    def score_relevance(self, max, median):
        source_node = self.sourceNode
        target_node = self.targetNode
        threshold = (max + median) / 2
        mean = (source_node.edge_count + target_node.edge_count) / 2
        if mean > threshold:
            return 1
        return 0


    def update_properties(self, **properties):
        """Update or insert a new property of an edge.


        :param properties: The keyword arguments that are added as properties to the Edge.

        >>> node_1 = Node(1)
        >>> node_2 = Node(2)
        >>> edge_1_2 = Edge(node_1, node_2, True, relation='killed')

        The following command updates the relation and adds a new properties:
        >>> edge_1_2.update_properties(relation='sibling', width=5)
        >>> edge_1_2.relation
        'sibling'
        >>> edge_1_2.width
        5
        """
        for (key, value) in properties.items():
            setattr(self, key, value)

    def get(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        return None

    def fulfills_all_properties(self, **properties):
        """
        Checks if all of the properties are fulfilled.
        (The properties are connected by AND)

        :param properties: The keyword arguments to check if fulfilled
        :return: True, if all properties are fulfilled otherwise False.
        :type: bool

        >>> node_1 = Node(1)
        >>> node_2 = Node(2)
        >>> edge_1_2 = Edge(node_1, node_2, directed=True, relation='killed')
        >>> edge_1_2.fulfills_all_properties(directed=True, relation='killed')
        True
        >>> edge_1_2.fulfills_all_properties(directed=True, relation='sibling')
        False
        >>> edge_1_2.fulfills_all_properties(directed=True, relation='killed', type='legal')
        False

        """
        curr_properties = self.__dict__
        for (key, value) in properties.items():
            if key not in curr_properties or value != curr_properties[key]:
                return False
        return True
