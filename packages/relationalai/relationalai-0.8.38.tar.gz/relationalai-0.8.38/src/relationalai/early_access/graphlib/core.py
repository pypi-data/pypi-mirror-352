"""
Core functionality for the graphlib package.
"""
from typing import Optional

from relationalai.early_access.builder import Concept, Relationship
from relationalai.early_access.builder import Integer#, Float
from relationalai.early_access.builder import where, define, count

class Graph():
    def __init__(self,
            *,
            directed: bool,
            weighted: bool,
            aggregator: Optional[str] = None,
        ):
        assert isinstance(directed, bool), "The `directed` argument must be a boolean."
        assert isinstance(weighted, bool), "The `weighted` argument must be a boolean."
        self.directed = directed
        self.weighted = weighted

        assert isinstance(aggregator, type(None)), "Weight aggregation not yet supported."
        # TODO: In the hopefully not-too-distant future, this argument will
        #   allow the user to specify whether and how to aggregate weights
        #   for multi-edges that exist at the user interface (Edge) level
        #   to construct the internal edge/weight list representation.
        #   The `str` type is just a placeholder; it should be something else.

        # Introduce Node and Edge concepts.
        Node = Concept("Node")
        Edge = Concept("Edge")
        Edge.src = Relationship("{edge:Edge} has source {src:Node}")
        Edge.dst = Relationship("{edge:Edge} has destination {dst:Node}")
        Edge.weight = Relationship("{edge:Edge} has weight {weight:Float}")
        self.Node = Node
        self.Edge = Edge

        # TODO: Require that each Edge has an Edge.src.
        # TODO: Require that each Edge has an Edge.dst.
        # TODO: If weighted, require that each Edge has an Edge.weight.
        # TODO: If not weighted, require that each Edge does not have an Edge.weight.

        # TODO: Suppose that type checking should in future restrict `src` and
        #   `dst` to be `Node`s, but at the moment we may need a require for that.
        # TODO: Suppose that type checking should in future restrict `weight` to be
        #   `Float`s, but at the moment we may need a require for that.

        # TODO: Transform Node and Edge into underlying edge-/weight-list representation.
        # NOTE: Operate under the assumption that `Node` contains all
        #   possible nodes, i.e. we can use the `Node` Concept directly as
        #   the node list. Has the additional benefit of allowing relationships
        #   (for which it makes sense) to be properties of `Node` rather than standalone.
        self._define_edge_relationships()
 
        self._define_num_nodes_relationship()
        self._define_num_edges_relationship()

        self._define_neighbor_relationships()
        self._define_count_neighbor_relationships()
        self._define_common_neighbor_relationship()
        self._define_count_common_neighbor_relationship()

        self._define_degree_relationships()


    def _define_edge_relationships(self):
        """
        Define the self._edge and self._weight relationships,
        consuming the Edge concept's `src`, `dst`, and `weight` relationships.
        """
        self._edge = Relationship("{src:Node} has edge to {dst:Node}")
        self._weight = Relationship("{src:Node} has edge to {dst:Node} with weight {weight:Float}")

        Edge = self.Edge
        if self.directed and self.weighted:
            define(
                self._weight(Edge.src, Edge.dst, Edge.weight),
                self._edge(Edge.src, Edge.dst)
            )
        elif self.directed and not self.weighted:
            define(
                self._weight(Edge.src, Edge.dst, 1.0),
                self._edge(Edge.src, Edge.dst)
            )
        elif not self.directed and self.weighted:
            define(
                self._weight(Edge.src, Edge.dst, Edge.weight),
                self._weight(Edge.dst, Edge.src, Edge.weight),
                self._edge(Edge.src, Edge.dst),
                self._edge(Edge.dst, Edge.src)
            )
        elif not self.directed and not self.weighted:
            define(
                self._weight(Edge.src, Edge.dst, 1.0),
                self._weight(Edge.dst, Edge.src, 1.0),
                self._edge(Edge.src, Edge.dst),
                self._edge(Edge.dst, Edge.src)
            )

    def _define_num_nodes_relationship(self):
        """Define the self._num_nodes relationship."""
        self._num_nodes = Relationship("The graph has {num_nodes:Integer} nodes")
        define(self._num_nodes(count(self.Node) | 0))

    def _define_num_edges_relationship(self):
        """Define the self._num_edges relationship."""
        self._num_edges = Relationship("The graph has {num_edges:Integer} edges")

        src, dst = self.Node.ref(), self.Node.ref()

        if self.directed:
            define(self._num_edges(count(src, dst, self._edge(src, dst)) | 0))
        elif not self.directed:
            define(self._num_edges(count(src, dst, self._edge(src, dst), src <= dst) | 0))
            # TODO: Generates an UnresolvedOverload warning from the typer.
            #   Should be sorted out by improvements in the typer (to allow
            #   comparisons between instances of concepts).


    def _define_neighbor_relationships(self):
        """Define the self.[in,out]neighbor relationships."""
        self._neighbor = Relationship("{src:Node} has neighbor {dst:Node}")
        self._inneighbor = Relationship("{dst:Node} has inneighbor {src:Node}")
        self._outneighbor = Relationship("{src:Node} has outneighbor {dst:Node}")

        src, dst = self.Node.ref(), self.Node.ref()
        where(self._edge(src, dst)).define(self._neighbor(src, dst), self._neighbor(dst, src))
        where(self._edge(dst, src)).define(self._inneighbor(src, dst))
        where(self._edge(src, dst)).define(self._outneighbor(src, dst))
        # Note that these definitions happen to work for both
        # directed and undirected graphs due to `edge` containing
        # each edge's symmetric partner in the undirected case.

    def _define_count_neighbor_relationships(self):
        """
        Define the self._count_[in,out]neighbor relationships.
        Note that these relationships differ from corresponding
        [in,out]degree relationships in that they yield empty
        rather than zero absent [in,out]neighbors.
        Primarily for internal consumption.
        """
        self._count_neighbor = Relationship("{src:Node} has neighbor count {count:Integer}")
        self._count_inneighbor = Relationship("{dst:Node} has inneighbor count {count:Integer}")
        self._count_outneighbor = Relationship("{src:Node} has outneighbor count {count:Integer}")

        src, dst = self.Node.ref(), self.Node.ref()
        where(self._neighbor(src, dst)).define(self._count_neighbor(src, count(dst).per(src)))
        where(self._inneighbor(dst, src)).define(self._count_inneighbor(dst, count(src).per(dst)))
        where(self._outneighbor(src, dst)).define(self._count_outneighbor(src, count(dst).per(src)))


    def _define_common_neighbor_relationship(self):
        """Define the self._common_neighbor relationship."""
        self._common_neighbor = Relationship("{node_a:Node} and {node_b:Node} have common neighbor {node_c:Node}")

        node_a, node_b, node_c = self.Node.ref(), self.Node.ref(), self.Node.ref()
        where(self._neighbor(node_a, node_c), self._neighbor(node_b, node_c)).define(self._common_neighbor(node_a, node_b, node_c))

    def _define_count_common_neighbor_relationship(self):
        """Define the self._count_common_neighbor relationship."""
        self._count_common_neighbor = Relationship("{node_a:Node} and {node_b:Node} have common neighbor count {count:Integer}")

        node_a, node_b, node_c = self.Node.ref(), self.Node.ref(), self.Node.ref()
        where(self._common_neighbor(node_a, node_b, node_c)).define(self._count_common_neighbor(node_a, node_b, count(node_c).per(node_a, node_b)))


    def _define_degree_relationships(self):
        """Define the self._[in,out]degree relationships."""
        self._degree = Relationship("{node:Node} has degree {count:Integer}")
        self._indegree = Relationship("{node:Node} has indegree {count:Integer}")
        self._outdegree = Relationship("{node:Node} has outdegree {count:Integer}")

        incount, outcount = Integer.ref(), Integer.ref()

        where(
            _indegree := where(self._count_inneighbor(self.Node, incount)).select(incount),
        ).define(self._indegree(self.Node, _indegree | 0))

        where(
            _outdegree := where(self._count_outneighbor(self.Node, outcount)).select(outcount),
        ).define(self._outdegree(self.Node, _outdegree | 0))

        if self.directed:
            where(
                _indegree := where(self._indegree(self.Node, incount)).select(incount),
                _outdegree := where(self._outdegree(self.Node, outcount)).select(outcount),
            ).define(self._degree(self.Node, (_indegree | 0) + (_outdegree | 0)))
        elif not self.directed:
            neighcount = Integer.ref()
            where(
                _degree := where(self._count_neighbor(self.Node, neighcount)).select(neighcount),
            ).define(self._degree(self.Node, _degree | 0))


    # Public accessor methods for private relationships.
    def num_nodes(self): return self._num_nodes
    def num_edges(self): return self._num_edges

    def neighbor(self): return self._neighbor
    def inneighbor(self): return self._inneighbor
    def outneighbor(self): return self._outneighbor

    def count_neighbor(self): return self._count_neighbor
    def count_inneighbor(self): return self._count_inneighbor
    def count_outneighbor(self): return self._count_outneighbor

    def common_neighbor(self): return self._common_neighbor
    def count_common_neighbor(self): return self._count_common_neighbor

    def degree(self): return self._degree
    def indegree(self): return self._indegree
    def outdegree(self): return self._outdegree
