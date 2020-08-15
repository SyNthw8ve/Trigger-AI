from trigger.train.cluster.gstream.link import Link
from typing import List, Optional, Tuple
from trigger.train.cluster.gstream.node import Node

class Graph:

    def __init__(self) -> None:

        self.nodes: List[Node] = []
        self.links: List[Link] = []

    def insert_node(self, node: Node) -> None:

        self.nodes.append(node)

    def insert_link(self, link) -> None:

        self.links.append(link)

    def has_link(self, v: Node, u: Node) -> bool:

        for link in self.links:

            if (link.u == u and link.v == v) or (link.u == v and link.v == u):

                return True

        return False

    def get_link(self, v: Node, u: Node) -> Optional[Link]:

        for link in self.links:

            if (link.u == u and link.v == v) or (link.u == v and link.v == u):

                return link

        return None

    def get_q_and_f(self) -> Tuple[Node, Node]:

        q = sorted(self.nodes, key=lambda node: node.error, reverse=True)[0]
        f = sorted(q.topological_neighbors, 
                                    key=lambda node: node.error, reverse=True)[0]

        return (q, f)