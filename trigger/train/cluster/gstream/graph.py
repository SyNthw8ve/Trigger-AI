

class Graph:

    def __init__(self):

        self.nodes = []
        self.links = []

    def insert_node(self, node):

        self.nodes.append(node)

    def insert_link(self, link):

        self.links.append(link)

    def get_q_and_f(self) -> Node, Node:

        q = sorted(self.nodes, key=lambda node: node.error, reverse=True)[0]
        f = sorted(q.topological_neighbors, 
                                    key=lambda node: node.error, reverse=True)[0]

        return (q, f)