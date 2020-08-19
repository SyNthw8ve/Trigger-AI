from trigger.train.cluster.gstream.link import Link
from typing import List, Optional, Tuple, Dict
from trigger.train.cluster.gstream.node import Node

class Graph:

    def __init__(self) -> None:

        self.nodes: Dict[int, Node] = {}
        self.links: Dict[Tuple[int, int], Link] = {}

    def insert_node(self, node: Node) -> None:

        self.nodes[node.id] = node

    def remove_node(self, node: Node) -> None:

        self.nodes.pop(node.id)
        
    def get_node(self, id) -> Node:

        return self.nodes[id]

    def insert_link(self, v: Node, u: Node, link) -> None:

        self.links[(v.id, u.id)] = link

    def remove_link(self, v: Node, u: Node) -> None:

        if self.links.get((v.id, u.id), -1) != -1:

            self.links.pop((v.id, u.id))

        else:
            self.links.pop((u.id, v.id))
            

    def has_link(self, v: Node, u: Node) -> bool:

        return (self.links.get((v.id, u.id), -1) != -1) or (self.links.get((u.id, v.id), -1) != -1)
            
    def get_link(self, v: Node, u: Node) -> Optional[Link]:

        link = self.links.get((v.id, u.id), -1)

        if link != -1:

            return link

        return self.links.get((u.id, v.id), -1)

    def get_q_and_f(self) -> Tuple[Node, Node]:

        q = sorted(self.nodes.values(), key=lambda node: node.error, reverse=True)[0]
        f = sorted(q.topological_neighbors.values(), 
                                    key=lambda node: node.error, reverse=True)[0]

        return (q, f)