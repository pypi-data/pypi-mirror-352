#
### Import libraries ###
#
from typing import Optional, Any, Callable
#
import random
import copy
import heapq
#
import numpy as np


#
### Class that represents a Graph node ###
#
class GraphNode:
    #
    ### Constructor ###
    #
    def __init__(self, node_id: str, graph: "Graph", values: Optional[dict[str, Any]] = None) -> None:
        #
        ### Unique ID of the node in the graph ###
        #
        self.node_id: str = node_id
        #
        ### Reference to the node's graph ###
        #
        self.graph: Graph = Graph
        #
        ### Container for values to register in this node ###
        #
        self.values: Optional[dict[str, Any]] = values


#
### Class that represents a graph ###
#
class Graph:
    #
    ### Constructor ###
    #
    def __init__(self, weighted: bool = False) -> None:
        """
        Initialize a new Graph instance.

        Args:
            weighted (bool, optional): Indicates if the graph is weighted. Defaults to False.

        Returns:
            None
        """

        #
        ### Container to quickly store & access all the nodes ###
        #
        self.nodes: dict[str, GraphNode] = {}
        #
        ### Indicates if there are weights stored to the edges ###
        #
        self.weighted: bool = weighted
        #
        ### Container to quickly store & access all the edges with weights ###
        #
        self.nodes_edges: dict[str, set[str] | dict[str, float]] = {}
        #
        ### To access in O(1) to all the edges from destination ###
        #
        self.nodes_edges_sym: dict[str, set[str]] = {}

    #
    ### Function to generate an unique node_id ###
    #
    def generate_unique_node_id(self) -> str:
        """
        Generate a unique node ID for the graph.

        Returns:
            str: A unique node ID.

        Raises:
            UserWarning: If the maximum iteration limit for generating a unique ID is reached.
        """

        #
        ### Constant for id generation, best if larger value to reduce collision and maximum nodes capacity ###
        #
        MAXINT: int = 9999999999
        #
        ### Generates random id ###
        #
        new_id: str = str(random.randint(0, MAXINT))
        #
        ### Guardrail to avoid while loop, maximum iteration limit, and raise error if limit reached ###
        #
        max_iter: int = 1000
        crt_iter: int = 0
        #
        ### While the generated node id already exists, generates a new one, and if max_iter reached, raise an error ###
        #
        while new_id in self.nodes:
            #
            ### Check for max iter limit reached ###
            #
            if crt_iter >= max_iter:
                #
                raise UserWarning("Error: Reached maximum iteration for unique new node id generation !")
            #
            ### Generates a new random node id ###
            #
            new_id = str(random.randint(0, MAXINT))
            #
            ### Increment iteration counter to avoid while loop ###
            #
            crt_iter += 1

    #
    ### Function to add a new node in the graph ###
    #
    def add_node(self, node_id: str = "", values: Optional[dict[str, Any]] = None) -> GraphNode:
        """
        Add a new node to the graph.

        Args:
            node_id (str, optional): The ID of the node. If empty, a unique ID is generated. Defaults to "".
            values (Optional[dict[str, Any]], optional): A dictionary of node attributes. Defaults to None.

        Returns:
            GraphNode: The newly created node.

        Raises:
            UserWarning: If a node with the given ID already exists.
        """

        #
        ### If no node_id given, generate an unique one ###
        #
        if node_id == "":
            #
            node_id = self.generate_unique_node_id()
        #
        ### Check for unicity of node_id ###
        #
        if node_id in self.nodes:
            #
            raise UserWarning(f"Error: Trying to add a node but a node with same node_id (=`{node_id}`) already exists in the graph !")
        #
        ### If no errors, add the node to the graph ###
        #
        self.nodes[node_id] = GraphNode(node_id=node_id, graph=self, values=values)
        #
        ### Returns the newly created node ###
        #
        return self.nodes[node_id]

    #
    ### Function to add an edge to the graph ###
    #
    def add_edge(self, src_node_id: str, dst_node_id: str, weight: float = 1, add_symetric: bool = False) -> None:
        """
        Add an edge to the graph.

        Args:
            src_node_id (str): The ID of the source node.
            dst_node_id (str): The ID of the destination node.
            weight (float, optional): The weight of the edge (used if graph is weighted). Defaults to 1.
            add_symetric (bool, optional): If True, adds the reverse edge. Defaults to False.

        Returns:
            None

        Raises:
            UserWarning: If either source or destination node does not exist.
        """

        #
        ### Check for source node existence ###
        #
        if src_node_id not in self.nodes:
            #
            raise UserWarning(f"Error: Trying to add an edge between two nodes, but node with node_id=`{src_node_id}` does not exist in the graph !")
        #
        ### Check for destination node existence ###
        #
        if dst_node_id not in self.nodes:
            #
            raise UserWarning(f"Error: Trying to add an edge between two nodes, but node with node_id=`{dst_node_id}` does not exist in the graph !")
        #
        ### If first edge from source node, initialize it ###
        #
        if src_node_id not in self.nodes_edges:
            #
            self.nodes_edges[src_node_id] = dict() if self.weighted else set()
        #
        if dst_node_id not in self.nodes_edges_sym:
            #
            self.nodes_edges_sym[dst_node_id] = set()
        #
        ### Add the edge to the graph ###
        #
        if self.weighted:
            #
            self.nodes_edges[src_node_id][dst_node_id] = weight
        #
        else:
            #
            self.nodes_edges[src_node_id].add( dst_node_id )
        #
        self.nodes_edges_sym[dst_node_id].add( src_node_id )
        #
        ### Adds the symetric edge if needed ###
        #
        if add_symetric:
            #
            self.add_edge(src_node_id=dst_node_id, dst_node_id=src_node_id, add_symetric=False)

    #
    ### Function to remove an edge from the graph ###
    #
    def remove_edge(self, src_node_id: str, dst_node_id: str, remove_symetric: bool = False) -> None:
        """
        Remove an edge from the graph.

        Args:
            src_node_id (str): The ID of the source node.
            dst_node_id (str): The ID of the destination node.
            remove_symetric (bool, optional): If True, removes the reverse edge. Defaults to False.

        Returns:
            None

        Raises:
            UserWarning: If either source or destination node does not exist, or if the edge does not exist.
        """

        #
        ### Check for source node existence ###
        #
        if src_node_id not in self.nodes:
            #
            raise UserWarning(f"Error: Trying to remove an edge between two nodes, but node with node_id=`{src_node_id}` does not exist in the graph !")
        #
        ### Check for destination node existence ###
        #
        if dst_node_id not in self.nodes:
            #
            raise UserWarning(f"Error: Trying to remove an edge between two nodes, but node with node_id=`{dst_node_id}` does not exist in the graph !")
        #
        ### Check for edge existence ###
        #
        if (src_node_id not in self.nodes_edges) or (dst_node_id not in self.nodes_edges[src_node_id]):
            #
            raise UserWarning(f"Error: Tring to remove an edge that doesn't exists from node_id={src_node_id} to node_id={dst_node_id}")
        #
        ### Removes the edge ###
        #
        if self.weighted:
            #
            self.nodes_edges[src_node_id].pop( dst_node_id )
        #
        else:
            #
            self.nodes_edges[src_node_id].remove( dst_node_id )
        #
        self.nodes_edges_sym[dst_node_id].remove( src_node_id )
        #
        ### Cleaning edge structure if empty ###
        #
        if len(self.nodes_edges[src_node_id]) == 0:
            #
            del self.nodes_edges[src_node_id]
        #
        if len(self.nodes_edges[dst_node_id]) == 0:
            del self.nodes_edges_sym[dst_node_id]

    #
    ### Function to remove all the edges that have a specific source node from the graph ###
    #
    def remove_all_edges_from_src_node(self, src_node_id: str) -> None:
        """
        Remove all edges originating from a specific source node.

        Args:
            src_node_id (str): The ID of the source node.

        Returns:
            None

        Raises:
            UserWarning: If the source node does not exist.
        """

        #
        ### Check for source node existence ###
        #
        if src_node_id not in self.nodes:
            #
            raise UserWarning(f"Error: Trying to remove an edge between two nodes, but node with node_id=`{src_node_id}` does not exist in the graph !")
        #
        ### If no edges, ends directly the function here ###
        #
        if src_node_id not in self.nodes_edges:
            #
            return
        #
        ### Remove all the edges from the source node ###
        #
        destination_nodes: list[str] = list( self.nodes_edges[src_node_id] )
        #
        for dst_node_id in destination_nodes:
            #
            self.remove_edge(src_node_id=src_node_id, dst_node_id=dst_node_id)

    #
    ### Function to remove all the edges that have a specific destination node from the graph ###
    #
    def remove_all_edges_to_dst_node(self, dst_node_id: str) -> None:
        """
        Remove all edges pointing to a specific destination node.

        Args:
            dst_node_id (str): The ID of the destination node.

        Returns:
            None

        Raises:
            UserWarning: If the destination node does not exist.
        """

        #
        ### Check for source node existence ###
        #
        if dst_node_id not in self.nodes:
            #
            raise UserWarning(f"Error: Trying to remove an edge between two nodes, but node with node_id=`{dst_node_id}` does not exist in the graph !")
        #
        ### If no edges, ends directly the function here ###
        #
        if dst_node_id not in self.nodes_edges_sym:
            #
            return
        #
        ### Remove all the edges that have the specific destination node ###
        #
        source_nodes: list[str] = list( self.nodes_edges_sym[dst_node_id] )
        #
        for src_node_id in source_nodes:
            #
            self.remove_edge(src_node_id=src_node_id, dst_node_id=dst_node_id)

    #
    ### Function to remove a node from the graph ###
    #
    def remove_node(self, node_id: str, remove_edges_with: bool = True) -> None:
        """
        Remove a node from the graph.

        Args:
            node_id (str): The ID of the node to remove.
            remove_edges_with (bool, optional): If True, removes all edges connected to the node. Defaults to True.

        Returns:
            None

        Raises:
            UserWarning: If the node does not exist or if edges exist and remove_edges_with is False.
        """

        #
        ### Check for node existence ###
        #
        if node_id not in self.nodes:
            #
            raise UserWarning(f"Error: trying to delete inexisting node in graph !")
        #
        ### Check for edges ###
        #
        has_edges: bool = (node_id in self.nodes_edges and len(self.nodes_edges[node_id]) > 0) or (node_id in self.nodes_edges_sym and len(self.nodes_edges_sym[node_id]) > 0)
        #
        if has_edges:
            #
            ### If removes edges with param ###
            #
            if not remove_edges_with:
                #
                raise UserWarning(f"Error: cannot remove a node from the graph without removing all its edges !")
            #
            ### Remove all the edges with node_id as source ###
            #
            self.remove_all_edges_from_src_node(src_node_id=node_id)
            #
            ### Remove all the edges with node_id as destination ###
            #
            self.remove_all_edges_to_dst_node(dst_node_id=node_id)
        #
        ### Remove the node from the node list ###
        #
        del self.nodes[node_id]

    #
    ### Function to get node ###
    #
    def get_node(self, node_id: str) -> GraphNode:
        """
        Retrieve a node from the graph by its ID.

        Args:
            node_id (str): The ID of the node.

        Returns:
            GraphNode: The node with the specified ID.

        Raises:
            UserWarning: If the node does not exist.
        """

        #
        ### Check for node existence ###
        #
        if node_id not in self.nodes:
            #
            raise UserWarning(f"Error: node not found with node_id=`{node_id}` in the graph !")
        #
        ### Returns the node ###
        #
        return self.nodes[node_id]

    #
    ### Function to get a specific node value ###
    #
    def get_node_value(self, node_id: str, value_key: str) -> GraphNode:
        """
        Get a specific value associated with a node.

        Args:
            node_id (str): The ID of the node.
            value_key (str): The key of the value to retrieve.

        Returns:
            Any: The value associated with the key.

        Raises:
            UserWarning: If the node or value key does not exist.
        """

        #
        ### Check for node existence ###
        #
        if node_id not in self.nodes:
            #
            raise UserWarning(f"Error: node not found with node_id=`{node_id}` in the graph !")
        #
        ### Check for value existence ###
        #
        if value_key not in self.nodes[node_id].values:
            #
            raise UserWarning(f"Error: value not found in node with node_id=`{node_id}` and value_key=`{value_key}` in the graph !")
        #
        ### Returns the value ###
        #
        return self.nodes[node_id].values[value_key]

    #
    ### Function to set a specific node value ###
    #
    def set_node_value(self, node_id: str, value_key: str, value: Any) -> None:
        """
        Set a specific value for a node.

        Args:
            node_id (str): The ID of the node.
            value_key (str): The key of the value to set.
            value (Any): The value to set.

        Returns:
            None

        Raises:
            UserWarning: If the node does not exist.
        """

        #
        ### Check for node existence ###
        #
        if node_id not in self.nodes:
            #
            raise UserWarning(f"Error: node not found with node_id=`{node_id}` in the graph !")
        #
        ### set the node value ###
        #
        self.nodes[node_id].values[value_key] = value

    #
    ### Function to delete a specific node value ###
    #
    def del_node_value(self, node_id: str, value_key: str) -> GraphNode:
        """
        Delete a specific value associated with a node.

        Args:
            node_id (str): The ID of the node.
            value_key (str): The key of the value to delete.

        Returns:
            None

        Raises:
            UserWarning: If the node or value key does not exist.
        """

        #
        ### Check for node existence ###
        #
        if node_id not in self.nodes:
            #
            raise UserWarning(f"Error: node not found with node_id=`{node_id}` in the graph !")
        #
        ### Check for value existence ###
        #
        if value_key not in self.nodes[node_id].values:
            #
            raise UserWarning(f"Error: value not found in node with node_id=`{node_id}` and value_key=`{value_key}` in the graph !")
        #
        ### Delete the value ###
        #
        del self.nodes[node_id].values[value_key]

    #
    ### Get all the in-neighbors ids ###
    #
    def get_predecessors_ids_of_node(self, node_id: str = "", node: Optional[GraphNode] = None) -> list[str]:
        """
        Get the IDs of all predecessor nodes of a given node.

        Args:
            node_id (str, optional): The ID of the node. Defaults to "".
            node (Optional[GraphNode], optional): The node object. Defaults to None.

        Returns:
            list[str]: A list of predecessor node IDs.

        Raises:
            UserWarning: If neither node_id nor node is provided, or if the node does not exist.
        """

        #
        ### Check for given arguments ###
        #
        if node_id == "" and node is None:
            #
            raise UserWarning(f"Error: Called function `get_predecessors_of_node` without valid arguments !")
        #
        if node is not None:
            #
            node_id = node.node_id
        #
        ### Check for for node existence ###
        #
        if node_id not in self.nodes:
            #
            raise UserWarning(f"Error: The node with node_id=`{node_id}` does't exist in the graph !")
        #
        ### Get all predecessors and returns them ###
        #
        if node_id not in self.nodes_edges_sym:
            #
            return []
        #
        return self.nodes_edges_sym[node_id]

    #
    ### Get all the out-neighbors ids ###
    #
    def get_successors_ids_of_node(self, node_id: str = "", node: Optional[GraphNode] = None) -> list[str]:
        """
        Get the IDs of all successor nodes of a given node.

        Args:
            node_id (str, optional): The ID of the node. Defaults to "".
            node (Optional[GraphNode], optional): The node object. Defaults to None.

        Returns:
            list[str]: A list of successor node IDs.

        Raises:
            UserWarning: If neither node_id nor node is provided, or if the node does not exist.
        """

        #
        ### Check for given arguments ###
        #
        if node_id == "" and node is None:
            #
            raise UserWarning(f"Error: Called function `get_successors_of_node` without valid arguments !")
        #
        if node is not None:
            #
            node_id = node.node_id
        #
        ### Check for for node existence ###
        #
        if node_id not in self.nodes:
            #
            raise UserWarning(f"Error: The node with node_id=`{node_id}` does't exist in the graph !")
        #
        ### Get all successors and returns them ###
        #
        if node_id not in self.nodes_edges:
            #
            return []
        #
        return self.nodes_edges[node_id]

    #
    ### Get all the in-neighbors ###
    #
    def get_predecessors_of_node(self, node_id: str = "", node: Optional[GraphNode] = None) -> list[GraphNode]:
        """
        Get all predecessor nodes of a given node.

        Args:
            node_id (str, optional): The ID of the node. Defaults to "".
            node (Optional[GraphNode], optional): The node object. Defaults to None.

        Returns:
            list[GraphNode]: A list of predecessor nodes.

        Raises:
            UserWarning: If neither node_id nor node is provided, or if the node does not exist.
        """

        #
        return [self.nodes[src_node_id] for src_node_id in self.get_predecessors_ids_of_node(node_id=node_id, node=node)]

    #
    ### Get all the out-neighbors ###
    #
    def get_successors_of_node(self, node_id: str = "", node: Optional[GraphNode] = None) -> list[GraphNode]:
        """
        Get all successor nodes of a given node.

        Args:
            node_id (str, optional): The ID of the node. Defaults to "".
            node (Optional[GraphNode], optional): The node object. Defaults to None.

        Returns:
            list[GraphNode]: A list of successor nodes.

        Raises:
            UserWarning: If neither node_id nor node is provided, or if the node does not exist.
        """

        #
        return [self.nodes[src_node_id] for dst_node_id in self.get_successors_ids_of_node(node_id=node_id, node=node)]

    #
    ### Function to get the in-degree of a specific node ###
    #
    def get_in_degree(self, node_id: str) -> int:
        """
        Get the in-degree of a specific node.

        Args:
            node_id (str): The ID of the node.

        Returns:
            int: The number of incoming edges to the node.

        Raises:
            UserWarning: If the node does not exist.
        """

        #
        ### Check for node existence ###
        #
        if node_id not in self.nodes:
            #
            raise UserWarning(f"Error: node not found with node_id=`{node_id}` in the graph !")
        #
        ### Returns the number of predecessors ###
        #
        return len(self.nodes_edges_sym.get(node_id, set()))

    #
    ### Function to get the out-degree of a specific node ###
    #
    def get_out_degree(self, node_id: str) -> int:
        """
        Get the out-degree of a specific node.

        Args:
            node_id (str): The ID of the node.

        Returns:
            int: The number of outgoing edges from the node.

        Raises:
            UserWarning: If the node does not exist.
        """

        #
        ### Check for node existence ###
        #
        if node_id not in self.nodes:
            #
            raise UserWarning(f"Error: node not found with node_id=`{node_id}` in the graph !")
        #
        ### Returns the number of successors ###
        #
        if self.weighted:
            return len(self.nodes_edges.get(node_id, {}))
        else:
            return len(self.nodes_edges.get(node_id, set()))

    #
    ### Function to get the total degree of a specific node (sum of in-degree and out-degree) ###
    #
    def get_degree(self, node_id: str) -> int:
        """
        Get the total degree (in-degree + out-degree) of a specific node.

        Args:
            node_id (str): The ID of the node.

        Returns:
            int: The total degree of the node.

        Raises:
            UserWarning: If the node does not exist.
        """

        #
        ### Check for node existence ###
        #
        if node_id not in self.nodes:
            #
            raise UserWarning(f"Error: node not found with node_id=`{node_id}` in the graph !")
        #
        ### Returns the sum of in-degree and out-degree ###
        #
        return self.get_in_degree(node_id) + self.get_out_degree(node_id)

    #
    ### Function to get the weight of a specific edge ###
    #
    def get_edge_weight(self, src_node_id: str, dst_node_id: str) -> float:
        """
        Get the weight of an edge between two nodes.

        Args:
            src_node_id (str): The ID of the source node.
            dst_node_id (str): The ID of the destination node.

        Returns:
            float: The weight of the edge.

        Raises:
            UserWarning: If the graph is unweighted, if either node does not exist, or if the edge does not exist.
        """

        #
        ### Check if graph is weighted ###
        #
        if not self.weighted:
            #
            raise UserWarning("Error: Cannot get edge weight from an unweighted graph!")
        #
        ### Check for source node existence ###
        #
        if src_node_id not in self.nodes:
            #
            raise UserWarning(f"Error: Source node with node_id=`{src_node_id}` does not exist in the graph !")
        #
        ### Check for destination node existence ###
        #
        if dst_node_id not in self.nodes:
            #
            raise UserWarning(f"Error: Destination node with node_id=`{dst_node_id}` does not exist in the graph !")
        #
        ### Check for edge existence and return weight ###
        #
        if src_node_id in self.nodes_edges and dst_node_id in self.nodes_edges[src_node_id]:
            #
            return self.nodes_edges[src_node_id][dst_node_id]
        #
        raise UserWarning(f"Error: Edge from node_id=`{src_node_id}` to node_id=`{dst_node_id}` does not exist.")

    #
    ### Function to check if an edge exists between two nodes ###
    #
    def has_edge(self, src_node_id: str, dst_node_id: str) -> bool:
        """
        Check if an edge exists between two nodes.

        Args:
            src_node_id (str): The ID of the source node.
            dst_node_id (str): The ID of the destination node.

        Returns:
            bool: True if the edge exists, False otherwise.
        """

        #
        ### Check for node existence (optional, but good for robustness) ###
        #
        if src_node_id not in self.nodes or dst_node_id not in self.nodes:
            return False
        #
        ### Check for edge existence ###
        #
        if self.weighted:
            return src_node_id in self.nodes_edges and dst_node_id in self.nodes_edges[src_node_id]
        else:
            return src_node_id in self.nodes_edges and dst_node_id in self.nodes_edges[src_node_id]

    #
    ### Function that performs a simple graph exploration
    #
    def explore_from_source(
        self,
        src_node_id: str,
        exploration_algorithm: str = "bfs",
        force_sym_edges_to_exists: bool = False,
        nodes_marks: Optional[dict[str, Any]] = None,
        custom_node_ordering: Optional[Callable[str, float]] = None,
        fn_to_mark_nodes: Callable[..., Any] = lambda _: 1,
        fn_to_mark_nodes_args: Optional[list[Any]] = None,
        fn_to_mark_nodes_kwargs: Optional[dict[str, Any]] = None,
        fn_on_loop: Callable[..., bool] = lambda _: True,
        fn_on_loop_args: Optional[list[Any]] = None,
        fn_on_loop_kwargs: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Perform a graph exploration starting from a source node using the specified algorithm.

        Args:
            src_node_id (str): The ID of the source node.
            exploration_algorithm (str, optional): The exploration algorithm ('bfs', 'dfs', or 'random'). Defaults to "bfs".
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to False.
            nodes_marks (Optional[dict[str, Any]], optional): Dictionary to store node marks. Defaults to None.
            custom_node_ordering (Optional[Callable[str, float]], optional): Function to order nodes. Defaults to None.
            fn_to_mark_nodes (Callable[..., Any], optional): Function to mark nodes. Defaults to lambda _: 1.
            fn_to_mark_nodes_args (Optional[list[Any]], optional): Arguments for fn_to_mark_nodes. Defaults to None.
            fn_to_mark_nodes_kwargs (Optional[dict[str, Any]], optional): Keyword arguments for fn_to_mark_nodes. Defaults to None.
            fn_on_loop (Callable[..., bool], optional): Function to control the exploration loop. Defaults to lambda _: True.
            fn_on_loop_args (Optional[list[Any]], optional): Arguments for fn_on_loop. Defaults to None.
            fn_on_loop_kwargs (Optional[dict[str, Any]], optional): Keyword arguments for fn_on_loop. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary of marked nodes.

        Raises:
            UserWarning: If the exploration algorithm is invalid.
        """
        #
        ### Check for valid algorithm ###
        #
        if not exploration_algorithm in ["bfs", "dfs", "random"]:
            #
            raise UserWarning(f"Error: unknown exploration algorithm = `{exploration_algorithm}`")
        #
        ### Initialize marked nodes, uses given one if given one ###
        #
        nodes_marks: dict[str, Any] = nodes_marks if nodes_marks is not None else {}
        #
        ### Initialize queue ###
        #
        queue: list[str] = []
        #
        ### Add initial node in queue ###
        #
        queue.append( src_node_id )
        #
        ### Exploration loop, explore while there are nodes in the queue ###
        #
        fn_on_loop_args_: list[Any] = fn_to_mark_nodes_args if fn_to_mark_nodes_args is not None else []
        fn_on_loop_kwargs_: dict[str, Any] = fn_to_mark_nodes_kwargs if fn_to_mark_nodes_kwargs is not None else {}
        #
        while queue and fn_on_loop(*fn_on_loop_args_, **fn_on_loop_kwargs_):
            #
            ### Get the next node to explore following the given algorithm ###
            #
            crt_node_id: str
            #
            if exploration_algorithm == "bfs":
                #
                crt_node_id = queue.pop(0)
            #
            elif exploration_algorithm == "dfs":
                #
                crt_node_id = queue.pop(-1)
            #
            else:
                #
                rid: int = random.randint(0, len(queue)-1)
                #
                crt_node_id = queue.pop(rid)
            #
            ### Check if the ode has already been marked ###
            #
            if crt_node_id in nodes_marks:
                #
                continue
            #
            ### Mark the node ###
            #
            fn_to_mark_nodes_args_: list[Any] = fn_to_mark_nodes_args if fn_to_mark_nodes_args is not None else []
            fn_to_mark_nodes_kwargs_: dict[str, Any] = fn_to_mark_nodes_kwargs if fn_to_mark_nodes_kwargs is not None else {}
            #
            nodes_marks[crt_node_id] = fn_to_mark_nodes( crt_node_id, *fn_to_mark_nodes_kwargs_, **fn_to_mark_nodes_kwargs_ )
            #
            ### Get neighbors ###
            #
            neighbors_ids: list[str] = self.get_successors_ids_of_node(node_id=crt_node_id)
            #
            if force_sym_edges_to_exists:
                #
                neighbors_ids += self.get_predecessors_ids_of_node(node_id=crt_node_id)
            #
            if custom_node_ordering is not None:
                #
                neighbors_ids.sort(keys=custom_node_ordering)
            #
            ### Explore neighbors ###
            #
            for neighbor_node_id in neighbors_ids:
                #
                ### Check if neighbor has been marked ###
                #
                if neighbor_node_id in nodes_marks:
                    #
                    continue
                #
                ### Add the neighbors to the queue ###
                #
                queue.append( neighbor_node_id )
        #
        ### Return curtom marked nodes, all the visited nodes have been marked, so nodes_marks.keys() is list of visited nodes ###
        #
        return nodes_marks

    #
    ### Function that performs a simple graph exploration and force all nodes exploration by calling auxiliar function until fully visited
    #
    def explore_all_nodes(
        self,
        exploration_algorithm: str = "bfs",
        force_sym_edges_to_exists: bool = False,
        custom_node_ordering: Optional[Callable[str, float]] = None,
        fn_to_mark_nodes: Callable[..., Any] = lambda _: 1,
        fn_to_mark_nodes_args: Optional[list[Any]] = None,
        fn_to_mark_nodes_kwargs: Optional[dict[str, Any]] = None,
        fn_on_loop: Callable[..., bool] = lambda _: True,
        fn_on_loop_args: Optional[list[Any]] = None,
        fn_on_loop_kwargs: Optional[dict[str, Any]] = None,
        fn_after_one_exploration: Callable[..., None] = lambda _: None,
        fn_after_one_exploration_args: Optional[list[Any]] = None,
        fn_after_one_exploration_kwargs: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Explore all nodes in the graph using the specified algorithm.

        Args:
            exploration_algorithm (str, optional): The exploration algorithm ('bfs', 'dfs', or 'random'). Defaults to "bfs".
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to False.
            custom_node_ordering (Optional[Callable[str, float]], optional): Function to order nodes. Defaults to None.
            fn_to_mark_nodes (Callable[..., Any], optional): Function to mark nodes. Defaults to lambda _: 1.
            fn_to_mark_nodes_args (Optional[list[Any]], optional): Arguments for fn_to_mark_nodes. Defaults to None.
            fn_to_mark_nodes_kwargs (Optional[dict[str, Any]], optional): Keyword arguments for fn_to_mark_nodes. Defaults to None.
            fn_on_loop (Callable[..., bool], optional): Function to control the exploration loop. Defaults to lambda _: True.
            fn_on_loop_args (Optional[list[Any]], optional): Arguments for fn_on_loop. Defaults to None.
            fn_on_loop_kwargs (Optional[dict[str, Any]], optional): Keyword arguments for fn_on_loop. Defaults to None.
            fn_after_one_exploration (Callable[..., None], optional): Function called after each exploration. Defaults to lambda _: None.
            fn_after_one_exploration_args (Optional[list[Any]], optional): Arguments for fn_after_one_exploration. Defaults to None.
            fn_after_one_exploration_kwargs (Optional[dict[str, Any]], optional): Keyword arguments for fn_after_one_exploration. Defaults to None.

        Returns:
            dict[str, Any]: A dictionary of marked nodes.
        """
        #
        ### Initialize marked nodes ###
        #
        nodes_marks: dict[str, Any] = {}
        #
        ### list to quickly access nodes that have not been visited ###
        #
        unvisited_nodes_lst: list[str] = list(self.nodes.keys())
        #
        if custom_node_ordering is not None:
            #
            unvisited_nodes_lst.sort(keys=custom_node_ordering)
        #
        unvisited_nodes: set[str] = set(unvisited_nodes_lst)
        #
        ### Wrapper function ###
        #
        def wrapper_fn_to_mark_nodes(visited_node_id: str, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
            #
            ### Remove node from unvisited_nodes ###
            #
            unvisited_nodes.remove(visited_node_id)
            #
            ### call wrapped function ###
            #
            fn_on_loop(visited_node_id, *args, **kwargs)

        #
        fn_after_one_exploration_args_ = fn_after_one_exploration_args if fn_after_one_exploration_args is not None else []
        fn_after_one_exploration_kwargs_ = fn_after_one_exploration_kwargs if fn_after_one_exploration_kwargs is not None else {}

        #
        ### Explore ALL nodes ###
        #
        while unvisited_nodes:
            #
            new_source_node_id: str = next(iter(unvisited_nodes))
            #
            nodes_marks = self.explore_from_source(
                src_node_id = new_source_node_id,
                exploration_algorithm = exploration_algorithm,
                force_sym_edges_to_exists = force_sym_edges_to_exists,
                nodes_marks = nodes_marks,
                custom_node_ordering = custom_node_ordering,
                fn_to_mark_nodes = wrapper_fn_to_mark_nodes,
                fn_to_mark_nodes_args = fn_to_mark_nodes_args,
                fn_to_mark_nodes_kwargs = fn_to_mark_nodes_kwargs,
                fn_on_loop = fn_on_loop,
                fn_on_loop_args = fn_on_loop_args,
                fn_on_loop_kwargs = fn_on_loop_kwargs
            )
            #
            fn_after_one_exploration(*fn_after_one_exploration_args_, **fn_after_one_exploration_kwargs_)

        #
        ### Return marked nodes ###
        #
        return nodes_marks

    #
    ### Function to get all the connex composants of the graph ###
    #
    def get_all_connex_composants(
        self,
        force_sym_edges_to_exists: bool = False,
        custom_node_ordering: Optional[Callable[str, float]] = None
    ) -> tuple[dict[str, int], list[list[str]]]:
        """
        Get all connected components of the graph.

        Args:
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to False.
            custom_node_ordering (Optional[Callable[str, float]], optional): Function to order nodes. Defaults to None.

        Returns:
            tuple[dict[str, int], list[list[str]]]: A tuple containing a dictionary mapping nodes to component IDs and a list of components (each component is a list of node IDs).
        """

        #
        ### Init var ###
        #
        crt_composant: int = 0
        #
        ### Define mark function ###
        #
        def mark_composant(*args, **kwargs) -> int:
            #
            return crt_composant
        #
        ### Define increment function ###
        #
        def increment_composant(*args, **kwargs) -> None:
            #
            crt_composant += 1
        #
        composantes: dict[str, int] = self.explore_all_nodes(
            force_sym_edges_to_exists=force_sym_edges_to_exists,
            custom_node_ordering=custom_node_ordering,
            fn_to_mark_nodes=mark_composant,
            fn_after_one_exploration=increment_composant
        )
        #
        composantes_nodes_lst: dict[int, list[str]] = {}
        #
        for node_id, comp_id in composantes.items():
            #
            if comp_id not in composantes_nodes_lst:
                #
                composantes_nodes_lst[comp_id] = []
            #
            composantes_nodes_lst[comp_id].append( node_id )
        #
        composantes_nodes_lst_final: list[list[str]] = []
        #
        for i in range(len(composantes_nodes_lst)):
            #
            composantes_nodes_lst_final.append( composantes_nodes_lst[i] )
        #
        return composantes, composantes_nodes_lst_final


    #
    ### Function to create a deep copy of the graph ###
    #
    def copy(self) -> 'Graph':
        """
        Create a deep copy of the graph.

        Returns:
            Graph: A new Graph instance with copied nodes and edges.
        """

        #
        ### Create a new graph instance with the same weighted property ###
        #
        new_graph: Graph = Graph(weighted=self.weighted)
        #
        ### Copy all nodes with their values ###
        #
        for node_id, node in self.nodes.items():
            new_graph.add_node(node_id=node_id, values=copy.deepcopy(node.values))
        #
        ### Copy all edges with their weights ###
        #
        for src_node_id, edges in self.nodes_edges.items():
            if self.weighted:
                for dst_node_id, weight in edges.items():
                    new_graph.add_edge(src_node_id=src_node_id, dst_node_id=dst_node_id, weight=weight)
            else:
                for dst_node_id in edges:
                    new_graph.add_edge(src_node_id=src_node_id, dst_node_id=dst_node_id)
        #
        ### Return the copied graph ###
        #
        return new_graph

    #
    ### Function to detect cycles in the graph ###
    #
    def has_cycle(self, force_sym_edges_to_exists: bool = False) -> bool:
        """
        Check if the graph contains a cycle.

        Args:
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to False.

        Returns:
            bool: True if a cycle exists, False otherwise.
        """

        #
        ### Initialize visited and recursion stack ###
        #
        visited: set[str] = set()
        rec_stack: set[str] = set()
        #
        ### DFS helper function ###
        #
        def dfs_cycle(node_id: str, parent: Optional[str] = None) -> bool:
            #
            ### Mark node as visited and add to recursion stack ###
            #
            visited.add(node_id)
            rec_stack.add(node_id)
            #
            ### Get neighbors ###
            #
            neighbors: list[str] = self.get_successors_ids_of_node(node_id=node_id)
            if force_sym_edges_to_exists:
                neighbors += [n for n in self.get_predecessors_ids_of_node(node_id=node_id) if n not in neighbors]
            #
            ### Explore neighbors ###
            #
            for neighbor_id in neighbors:
                #
                ### Skip parent in undirected graph to avoid false positives ###
                #
                if force_sym_edges_to_exists and neighbor_id == parent:
                    continue
                #
                ### If neighbor not visited, explore it ###
                #
                if neighbor_id not in visited:
                    if dfs_cycle(neighbor_id, node_id if force_sym_edges_to_exists else None):
                        return True
                #
                ### If neighbor is in recursion stack, a cycle is found ###
                #
                elif neighbor_id in rec_stack:
                    return True
            #
            ### Remove node from recursion stack ###
            #
            rec_stack.remove(node_id)
            return False
        #
        ### Check all nodes to handle disconnected components ###
        #
        for node_id in self.nodes:
            if node_id not in visited:
                if dfs_cycle(node_id):
                    return True
        #
        ### No cycles found ###
        #
        return False

    #
    ### Function to compute a spanning tree or minimum spanning tree ###
    #
    def get_spanning_tree(self) -> 'Graph':
        """
        Compute a spanning tree or minimum spanning tree of the graph.

        Returns:
            Graph: A new Graph instance representing the spanning tree (Kruskal's algorithm for weighted graphs, BFS for unweighted).
        """

        #
        ### Create a new graph for the spanning tree ###
        #
        spanning_tree: Graph = Graph(weighted=self.weighted)
        #
        ### If graph is empty, return empty graph ###
        #
        if not self.nodes:
            return spanning_tree
        #
        ### Union-Find data structure for Kruskal's algorithm ###
        #
        parent: dict[str, str] = {}
        rank: dict[str, int] = {}
        #
        def find(node_id: str) -> str:
            if node_id not in parent:
                parent[node_id] = node_id
                rank[node_id] = 0
            if parent[node_id] != node_id:
                parent[node_id] = find(parent[node_id])
            return parent[node_id]
        #
        def union(node1: str, node2: str) -> None:
            root1, root2 = find(node1), find(node2)
            if root1 != root2:
                if rank[root1] < rank[root2]:
                    parent[root1] = root2
                elif rank[root1] > rank[root2]:
                    parent[root2] = root1
                else:
                    parent[root2] = root1
                    rank[root1] += 1
        #
        ### Add all nodes to the spanning tree ###
        #
        for node_id in self.nodes:
            spanning_tree.add_node(node_id=node_id, values=copy.deepcopy(self.nodes[node_id].values))
        #
        ### For weighted graphs, use Kruskal's algorithm ###
        #
        if self.weighted:
            edges: list[tuple[float, str, str]] = []
            for src_node_id, edges_dict in self.nodes_edges.items():
                for dst_node_id, weight in edges_dict.items():
                    edges.append((weight, src_node_id, dst_node_id))
            edges.sort()  # Sort by weight
            #
            ### Add edges to spanning tree if they don't form a cycle ###
            #
            for weight, src_node_id, dst_node_id in edges:
                if find(src_node_id) != find(dst_node_id):
                    spanning_tree.add_edge(src_node_id=src_node_id, dst_node_id=dst_node_id, weight=weight)
                    union(src_node_id, dst_node_id)
        #
        ### For unweighted graphs, use BFS ###
        #
        else:
            visited: set[str] = set()
            queue: list[str] = [next(iter(self.nodes))]
            visited.add(queue[0])
            while queue:
                node_id = queue.pop(0)
                for neighbor_id in self.get_successors_ids_of_node(node_id):
                    if neighbor_id not in visited:
                        spanning_tree.add_edge(src_node_id=node_id, dst_node_id=neighbor_id)
                        queue.append(neighbor_id)
                        visited.add(neighbor_id)
        #
        ### Return the spanning tree ###
        #
        return spanning_tree

    #
    ### Function to check if the graph is a DAG ###
    #
    def is_dag(self) -> bool:
        """
        Check if the graph is a Directed Acyclic Graph (DAG).

        Returns:
            bool: True if the graph is a DAG, False otherwise.
        """

        #
        ### A graph with cycles cannot be a DAG ###
        #
        return not self.has_cycle(force_sym_edges_to_exists=False)

    #
    ### Function to compute shortest paths using Dijkstra's algorithm ###
    #
    def dijkstra(self, src_node_id: str) -> tuple[dict[str, float], dict[str, Optional[str]]]:
        """
        Compute shortest paths from a source node using Dijkstra's algorithm.

        Args:
            src_node_id (str): The ID of the source node.

        Returns:
            tuple[dict[str, float], dict[str, Optional[str]]]: A tuple of dictionaries containing distances and predecessors.

        Raises:
            UserWarning: If the source node does not exist or if negative weights are detected.
        """

        #
        ### Check for source node existence ###
        #
        if src_node_id not in self.nodes:
            raise UserWarning(f"Error: Source node with node_id=`{src_node_id}` does not exist in the graph !")
        #
        ### Initialize distances and predecessors ###
        #
        distances: dict[str, float] = {node_id: float('inf') for node_id in self.nodes}
        distances[src_node_id] = 0
        predecessors: dict[str, Optional[str]] = {node_id: None for node_id in self.nodes}
        #
        ### Priority queue for nodes to explore ###
        #
        pq: list[tuple[float, str]] = [(0, src_node_id)]
        visited: set[str] = set()
        #
        ### Main loop ###
        #
        while pq:
            dist, curr_node_id = heapq.heappop(pq)
            if curr_node_id in visited:
                continue
            visited.add(curr_node_id)
            #
            ### Explore neighbors ###
            #
            if curr_node_id in self.nodes_edges:
                for neighbor_id in self.get_successors_ids_of_node(curr_node_id):
                    weight = self.nodes_edges[curr_node_id][neighbor_id] if self.weighted else 1
                    if weight < 0:
                        raise UserWarning(f"Error: Negative weight detected in edge from `{curr_node_id}` to `{neighbor_id}` !")
                    new_dist = dist + weight
                    if new_dist < distances[neighbor_id]:
                        distances[neighbor_id] = new_dist
                        predecessors[neighbor_id] = curr_node_id
                        heapq.heappush(pq, (new_dist, neighbor_id))
        #
        ### Return distances and predecessors ###
        #
        return distances, predecessors

    #
    ### Function to compute shortest path using A* algorithm ###
    #
    def a_star(self, src_node_id: str, dst_node_id: str, heuristic: Callable[[str, str], float]) -> tuple[list[str], float]:
        """
        Compute the shortest path between two nodes using the A* algorithm.

        Args:
            src_node_id (str): The ID of the source node.
            dst_node_id (str): The ID of the destination node.
            heuristic (Callable[[str, str], float]): Heuristic function estimating the cost to the destination.

        Returns:
            tuple[list[str], float]: A tuple containing the shortest path and its total cost.

        Raises:
            UserWarning: If either node does not exist, if negative weights are detected, or if no path exists.
        """

        #
        ### Check for source and destination node existence ###
        #
        if src_node_id not in self.nodes:
            raise UserWarning(f"Error: Source node with node_id=`{src_node_id}` does not exist in the graph !")
        if dst_node_id not in self.nodes:
            raise UserWarning(f"Error: Destination node with node_id=`{dst_node_id}` does not exist in the graph !")
        #
        ### Initialize distances, predecessors, and f-scores ###
        #
        g_scores: dict[str, float] = {node_id: float('inf') for node_id in self.nodes}
        g_scores[src_node_id] = 0
        f_scores: dict[str, float] = {node_id: float('inf') for node_id in self.nodes}
        f_scores[src_node_id] = heuristic(src_node_id, dst_node_id)
        predecessors: dict[str, Optional[str]] = {node_id: None for node_id in self.nodes}
        #
        ### Priority queue for nodes to explore ###
        #
        pq: list[tuple[float, str]] = [(f_scores[src_node_id], src_node_id)]
        visited: set[str] = set()
        #
        ### Main loop ###
        #
        while pq:
            f_score, curr_node_id = heapq.heappop(pq)
            if curr_node_id == dst_node_id:
                path: list[str] = []
                current: Optional[str] = curr_node_id
                while current is not None:
                    path.append(current)
                    current = predecessors[current]
                path.reverse()
                return path, g_scores[dst_node_id]
            if curr_node_id in visited:
                continue
            visited.add(curr_node_id)
            #
            ### Explore neighbors ###
            #
            if curr_node_id in self.nodes_edges:
                for neighbor_id in self.get_successors_ids_of_node(curr_node_id):
                    weight = self.nodes_edges[curr_node_id][neighbor_id] if self.weighted else 1
                    if weight < 0:
                        raise UserWarning(f"Error: Negative weight detected in edge from `{curr_node_id}` to `{neighbor_id}` !")
                    tentative_g_score = g_scores[curr_node_id] + weight
                    if tentative_g_score < g_scores[neighbor_id]:
                        predecessors[neighbor_id] = curr_node_id
                        g_scores[neighbor_id] = tentative_g_score
                        f_scores[neighbor_id] = tentative_g_score + heuristic(neighbor_id, dst_node_id)
                        heapq.heappush(pq, (f_scores[neighbor_id], neighbor_id))
        #
        ### No path found ###
        #
        raise UserWarning(f"Error: No path exists from `{src_node_id}` to `{dst_node_id}` !")

    #
    ### Function to get the adjacency matrix representation of the graph ###
    #
    def get_adjacency_matrix(self) -> tuple[np.ndarray, dict[str, int]]:
        """
        Get the adjacency matrix representation of the graph.

        Returns:
            tuple[np.ndarray, dict[str, int]]: A tuple containing the adjacency matrix and a node-to-index mapping.
        """

        #
        ### Get list of node IDs for consistent ordering ###
        #
        node_ids: list[str] = list(self.nodes.keys())
        n: int = len(node_ids)
        #
        ### Create mapping of node IDs to indices ###
        #
        node_to_index: dict[str, int] = {node_id: i for i, node_id in enumerate(node_ids)}
        #
        ### Initialize adjacency matrix ###
        #
        matrix: np.ndarray = np.zeros((n, n), dtype=float)
        #
        ### Populate matrix ###
        #
        for src_node_id in self.nodes_edges:
            for dst_node_id in self.get_successors_ids_of_node(src_node_id):
                src_idx: int = node_to_index[src_node_id]
                dst_idx: int = node_to_index[dst_node_id]
                matrix[src_idx, dst_idx] = (
                    self.nodes_edges[src_node_id][dst_node_id]
                    if self.weighted
                    else 1.0
                )
        #
        ### Return matrix and node-to-index mapping ###
        #
        return matrix, node_to_index

    #
    ### Function to get the adjacency list representation of the graph ###
    #
    def get_adjacency_list(self) -> dict[str, list[tuple[str, Optional[float]]]]:
        """
        Get the adjacency list representation of the graph.

        Returns:
            dict[str, list[tuple[str, Optional[float]]]]: A dictionary mapping each node to a list of (neighbor_id, weight) tuples.
        """

        #
        ### Initialize adjacency list ###
        #
        adj_list: dict[str, list[tuple[str, Optional[float]]]] = {
            node_id: [] for node_id in self.nodes
        }
        #
        ### Populate adjacency list ###
        #
        for src_node_id in self.nodes_edges:
            for dst_node_id in self.get_successors_ids_of_node(src_node_id):
                weight: Optional[float] = (
                    self.nodes_edges[src_node_id][dst_node_id]
                    if self.weighted
                    else None
                )
                adj_list[src_node_id].append((dst_node_id, weight))
        #
        ### Return adjacency list ###
        #
        return adj_list

    #
    ### Function to create a graph from an adjacency matrix ###
    #
    @staticmethod
    def from_adjacency_matrix(matrix: np.ndarray, node_ids: Optional[list[str]] = None, weighted: bool = True) -> 'Graph':
        """
        Create a graph from an adjacency matrix.

        Args:
            matrix (np.ndarray): The adjacency matrix.
            node_ids (Optional[list[str]], optional): List of node IDs. Defaults to None (generates IDs 0 to n-1).
            weighted (bool, optional): If True, the graph is weighted. Defaults to True.

        Returns:
            Graph: A new Graph instance constructed from the matrix.

        Raises:
            UserWarning: If the matrix is not square, contains negative values, or if node IDs are invalid.
        """

        #
        ### Validate matrix ###
        #
        if not isinstance(matrix, np.ndarray) or matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise UserWarning("Error: Input matrix must be a square NumPy array!")
        if np.any(matrix < 0):
            raise UserWarning("Error: Matrix contains negative values!")
        #
        ### Get number of nodes ###
        #
        n: int = matrix.shape[0]
        #
        ### Generate or validate node IDs ###
        #
        if node_ids is None:
            node_ids = [str(i) for i in range(n)]
        else:
            if len(node_ids) != n or len(set(node_ids)) != n:
                raise UserWarning("Error: Node IDs must be unique and match matrix dimensions!")
        #
        ### Create new graph ###
        #
        graph: Graph = Graph(weighted=weighted)
        #
        ### Add nodes ###
        #
        for node_id in node_ids:
            graph.add_node(node_id=node_id)
        #
        ### Add edges ###
        #
        for i in range(n):
            for j in range(n):
                if matrix[i, j] != 0:
                    graph.add_edge(
                        src_node_id=node_ids[i],
                        dst_node_id=node_ids[j],
                        weight=matrix[i, j] if weighted else 1.0
                    )
        #
        ### Return constructed graph ###
        #
        return graph

    #
    ### Function to get the list of all edges in the graph ###
    #
    def get_edge_list(self) -> list[tuple[str, str, Optional[float]]]:
        """
        Get a list of all edges in the graph.

        Returns:
            list[tuple[str, str, Optional[float]]]: A list of tuples containing source node ID, destination node ID, and weight (if weighted).
        """

        #
        ### Initialize edge list ###
        #
        edge_list: list[tuple[str, str, Optional[float]]] = []
        #
        ### Populate edge list ###
        #
        for src_node_id in self.nodes_edges:
            for dst_node_id in self.get_successors_ids_of_node(src_node_id):
                weight: Optional[float] = (
                    self.nodes_edges[src_node_id][dst_node_id]
                    if self.weighted
                    else None
                )
                edge_list.append((src_node_id, dst_node_id, weight))
        #
        ### Return edge list ###
        #
        return edge_list

    #
    ### Function to check if the graph is fully connected ###
    #
    def is_connected(self, force_sym_edges_to_exists: bool = True) -> bool:
        """
        Check if the graph is fully connected.

        Args:
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to True.

        Returns:
            bool: True if the graph is connected, False otherwise.
        """

        #
        ### If graph is empty, return True (vacuously connected) ###
        #
        if not self.nodes:
            return True
        #
        ### Get connected components ###
        #
        _, components = self.get_all_connex_composants(
            force_sym_edges_to_exists=force_sym_edges_to_exists
        )
        #
        ### Graph is connected if there is exactly one component ###
        #
        return len(components) == 1

    #
    ### Function to get the shortest path between two nodes ###
    #
    def get_shortest_path(self, src_node_id: str, dst_node_id: str) -> list[str]:
        """
        Get the shortest path between two nodes using Dijkstra's algorithm.

        Args:
            src_node_id (str): The ID of the source node.
            dst_node_id (str): The ID of the destination node.

        Returns:
            list[str]: The list of node IDs in the shortest path.

        Raises:
            UserWarning: If either node does not exist or if no path exists.
        """

        #
        ### Check for source and destination node existence ###
        #
        if src_node_id not in self.nodes:
            raise UserWarning(f"Error: Source node with node_id=`{src_node_id}` does not exist in the graph !")
        if dst_node_id not in self.nodes:
            raise UserWarning(f"Error: Destination node with node_id=`{dst_node_id}` does not exist in the graph !")
        #
        ### Run Dijkstra's algorithm ###
        #
        distances, predecessors = self.dijkstra(src_node_id)
        #
        ### Check if path exists ###
        #
        if distances[dst_node_id] == float('inf'):
            raise UserWarning(f"Error: No path exists from `{src_node_id}` to `{dst_node_id}` !")
        #
        ### Reconstruct path ###
        #
        path: list[str] = []
        current: Optional[str] = dst_node_id
        while current is not None:
            path.append(current)
            current = predecessors[current]
        path.reverse()
        #
        ### Return path ###
        #
        return path

    #
    ### Function to compute a topological sort of the graph ###
    #
    def topological_sort(self) -> list[str]:
        """
        Compute a topological sort of the graph.

        Returns:
            list[str]: A list of node IDs in topological order.

        Raises:
            UserWarning: If the graph contains a cycle.
        """

        #
        ### Check if graph is a DAG ###
        #
        if not self.is_dag():
            raise UserWarning("Error: Graph contains a cycle and cannot be topologically sorted!")
        #
        ### Initialize result and visited set ###
        #
        order: list[str] = []
        visited: set[str] = set()
        #
        ### DFS helper function ###
        #
        def dfs(node_id: str) -> None:
            visited.add(node_id)
            for neighbor_id in self.get_successors_ids_of_node(node_id):
                if neighbor_id not in visited:
                    dfs(neighbor_id)
            order.append(node_id)
        #
        ### Run DFS on all unvisited nodes ###
        #
        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id)
        #
        ### Reverse to get topological order ###
        #
        order.reverse()
        return order

    #
    ### Function to compute the transitive closure of the graph ###
    #
    def get_transitive_closure(self) -> tuple[np.ndarray, dict[str, int]]:
        """
        Compute the transitive closure of the graph using the Floyd-Warshall algorithm.

        Returns:
            tuple[np.ndarray, dict[str, int]]: A tuple containing the reachability matrix and a node-to-index mapping.
        """

        #
        ### Get list of node IDs for consistent ordering ###
        #
        node_ids: list[str] = list(self.nodes.keys())
        n: int = len(node_ids)
        #
        ### Create mapping of node IDs to indices ###
        #
        node_to_index: dict[str, int] = {node_id: i for i, node_id in enumerate(node_ids)}
        #
        ### Initialize reachability matrix ###
        #
        matrix: np.ndarray = np.zeros((n, n), dtype=bool)
        #
        ### Set initial reachability based on edges ###
        #
        for src_node_id in self.nodes_edges:
            for dst_node_id in self.get_successors_ids_of_node(src_node_id):
                src_idx: int = node_to_index[src_node_id]
                dst_idx: int = node_to_index[dst_node_id]
                matrix[src_idx, dst_idx] = True
        #
        ### Floyd-Warshall algorithm for transitive closure ###
        #
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    matrix[i, j] = matrix[i, j] or (matrix[i, k] and matrix[k, j])
        #
        ### Set diagonal to True (each node reaches itself) ###
        #
        np.fill_diagonal(matrix, True)
        #
        ### Return matrix and node-to-index mapping ###
        #
        return matrix, node_to_index

    #
    ### Function to compute the diameter of the graph (longest shortest path) ###
    #
    def get_diameter(self, force_sym_edges_to_exists: bool = True) -> float:
        """
        Compute the diameter of the graph (longest shortest path).

        Args:
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to True.

        Returns:
            float: The diameter of the graph.

        Raises:
            UserWarning: If the graph is not connected.
        """

        #
        ### Check if graph is connected ###
        #
        if not self.is_connected(force_sym_edges_to_exists=force_sym_edges_to_exists):
            raise UserWarning("Error: Graph is not connected, diameter is undefined!")
        #
        ### Initialize maximum shortest path length ###
        #
        max_distance: float = 0.0
        #
        ### Run Dijkstra's algorithm from each node ###
        #
        for src_node_id in self.nodes:
            distances, _ = self.dijkstra(src_node_id)
            #
            ### Consider symmetric edges if specified ###
            #
            if force_sym_edges_to_exists:
                for dst_node_id in self.get_predecessors_ids_of_node(src_node_id):
                    if self.weighted:
                        weight: float = self.get_edge_weight(dst_node_id, src_node_id)
                    else:
                        weight: float = 1.0
                    if distances[dst_node_id] > weight:
                        distances[dst_node_id] = weight
            #
            ### Update maximum distance ###
            #
            max_distance = max(max_distance, max((d for d in distances.values() if d != float('inf')), default=0.0))
        #
        ### Return diameter ###
        #
        return max_distance

    #
    ### Function to create a graph with all edge directions reversed ###
    #
    def reverse_graph(self) -> 'Graph':
        """
        Create a new graph with all edge directions reversed.

        Returns:
            Graph: A new Graph instance with reversed edges.
        """

        #
        ### Create a new graph with the same weighted property ###
        #
        reversed_graph: Graph = Graph(weighted=self.weighted)
        #
        ### Add all nodes with their values ###
        #
        for node_id, node in self.nodes.items():
            reversed_graph.add_node(node_id=node_id, values=copy.deepcopy(node.values))
        #
        ### Add reversed edges ###
        #
        for src_node_id, edges in self.nodes_edges.items():
            for dst_node_id in self.get_successors_ids_of_node(src_node_id):
                weight: Optional[float] = self.nodes_edges[src_node_id][dst_node_id] if self.weighted else 1.0
                reversed_graph.add_edge(src_node_id=dst_node_id, dst_node_id=src_node_id, weight=weight)
        #
        ### Return reversed graph ###
        #
        return reversed_graph

    #
    ### Function to compute strongly connected components using Kosaraju's algorithm ###
    #
    def get_strongly_connected_components(self) -> tuple[dict[str, int], list[list[str]]]:
        """
        Compute strongly connected components using Kosaraju's algorithm.

        Returns:
            tuple[dict[str, int], list[list[str]]]: A tuple containing a dictionary mapping nodes to component IDs and a list of components.
        """

        #
        ### Step 1: Perform DFS to get finishing times ###
        #
        visited: set[str] = set()
        finish_order: list[str] = []
        #
        def dfs_first_pass(node_id: str) -> None:
            visited.add(node_id)
            for neighbor_id in self.get_successors_ids_of_node(node_id):
                if neighbor_id not in visited:
                    dfs_first_pass(neighbor_id)
            finish_order.append(node_id)
        #
        ### Run DFS on all nodes ###
        #
        for node_id in self.nodes:
            if node_id not in visited:
                dfs_first_pass(node_id)
        #
        ### Step 2: Reverse the graph ###
        #
        reversed_graph: Graph = self.reverse_graph()
        #
        ### Step 3: Perform DFS on reversed graph in order of decreasing finishing times ###
        #
        visited.clear()
        components: dict[str, int] = {}
        component_list: list[list[str]] = []
        component_id: int = 0
        #
        def dfs_second_pass(node_id: str, comp_id: int) -> None:
            visited.add(node_id)
            components[node_id] = comp_id
            if comp_id >= len(component_list):
                component_list.append([])
            component_list[comp_id].append(node_id)
            for neighbor_id in reversed_graph.get_successors_ids_of_node(node_id):
                if neighbor_id not in visited:
                    dfs_second_pass(neighbor_id, comp_id)
        #
        ### Process nodes in reverse finishing order ###
        #
        for node_id in reversed(finish_order):
            if node_id not in visited:
                dfs_second_pass(node_id, component_id)
                component_id += 1
        #
        ### Return components mapping and list of components ###
        #
        return components, component_list

    #
    ### Function to compute the clustering coefficient for a node or the average for the graph ###
    #
    def get_clustering_coefficient(self, node_id: Optional[str] = None, force_sym_edges_to_exists: bool = True) -> float:
        """
        Compute the clustering coefficient for a node or the average for the graph.

        Args:
            node_id (Optional[str], optional): The ID of the node. If None, computes the average for all nodes. Defaults to None.
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to True.

        Returns:
            float: The clustering coefficient.

        Raises:
            UserWarning: If the specified node does not exist.
        """

        #
        ### If node_id is specified, compute local clustering coefficient ###
        #
        if node_id is not None:
            if node_id not in self.nodes:
                raise UserWarning(f"Error: Node with node_id=`{node_id}` does not exist in the graph!")
            #
            ### Get neighbors (successors and predecessors if undirected) ###
            #
            neighbors: set[str] = set(self.get_successors_ids_of_node(node_id))
            if force_sym_edges_to_exists:
                neighbors.update(self.get_predecessors_ids_of_node(node_id))
            neighbors.discard(node_id)  # Remove self-loop if present
            k: int = len(neighbors)
            if k < 2:
                return 0.0  # No triangles possible
            #
            ### Count edges between neighbors ###
            #
            edge_count: int = 0
            for n1 in neighbors:
                for n2 in neighbors:
                    if n1 < n2:  # Avoid double-counting
                        if self.has_edge(n1, n2) or (force_sym_edges_to_exists and self.has_edge(n2, n1)):
                            edge_count += 1
            #
            ### Compute clustering coefficient: 2 * edges_between_neighbors / (k * (k-1)) ###
            #
            return (2.0 * edge_count) / (k * (k - 1)) if k >= 2 else 0.0
        #
        ### Otherwise, compute average clustering coefficient ###
        #
        total_cc: float = 0.0
        node_count: int = 0
        for node_id in self.nodes:
            cc: float = self.get_clustering_coefficient(node_id, force_sym_edges_to_exists)
            total_cc += cc
            node_count += 1
        #
        ### Return average ###
        #
        return total_cc / node_count if node_count > 0 else 0.0

    #
    ### Function to get the shortest path using A* algorithm ###
    #
    def get_shortest_path_astar(self, src_node_id: str, dst_node_id: str, heuristic: Callable[[str, str], float]) -> list[str]:
        """
        Get the shortest path between two nodes using the A* algorithm.

        Args:
            src_node_id (str): The ID of the source node.
            dst_node_id (str): The ID of the destination node.
            heuristic (Callable[[str, str], float]): Heuristic function estimating the cost to the destination.

        Returns:
            list[str]: The list of node IDs in the shortest path.

        Raises:
            UserWarning: If either node does not exist or if no path exists.
        """

        #
        ### Check for source and destination node existence ###
        #
        if src_node_id not in self.nodes:
            raise UserWarning(f"Error: Source node with node_id=`{src_node_id}` does not exist in the graph !")
        if dst_node_id not in self.nodes:
            raise UserWarning(f"Error: Destination node with node_id=`{dst_node_id}` does not exist in the graph !")
        #
        ### Run A* algorithm and extract path ###
        #
        path, _ = self.a_star(src_node_id, dst_node_id, heuristic)
        #
        ### Return path ###
        #
        return path

    #
    ### Function to compute shortest paths between all pairs of nodes ###
    #
    def get_all_pairs_shortest_paths(self, force_sym_edges_to_exists: bool = True) -> tuple[np.ndarray, dict[str, int]]:
        """
        Compute shortest paths between all pairs of nodes.

        Args:
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to True.

        Returns:
            tuple[np.ndarray, dict[str, int]]: A tuple containing the distance matrix and a node-to-index mapping.

        Raises:
            UserWarning: If negative weights are detected in a weighted graph.
        """

        #
        ### Get list of node IDs for consistent ordering ###
        #
        node_ids: list[str] = list(self.nodes.keys())
        n: int = len(node_ids)
        #
        ### Create mapping of node IDs to indices ###
        #
        node_to_index: dict[str, int] = {node_id: i for i, node_id in enumerate(node_ids)}
        #
        ### Initialize distance matrix ###
        #
        matrix: np.ndarray = np.full((n, n), float('inf'), dtype=float)
        np.fill_diagonal(matrix, 0)
        #
        ### For unweighted graphs, use BFS ###
        #
        if not self.weighted:
            for src_node_id in node_ids:
                distances, _ = self.dijkstra(src_node_id)
                src_idx: int = node_to_index[src_node_id]
                for dst_node_id, dist in distances.items():
                    dst_idx: int = node_to_index[dst_node_id]
                    matrix[src_idx, dst_idx] = dist
                if force_sym_edges_to_exists:
                    for pred_node_id in self.get_predecessors_ids_of_node(src_node_id):
                        pred_idx: int = node_to_index[pred_node_id]
                        matrix[pred_idx, src_idx] = 1.0
        #
        ### For weighted graphs, use Floyd-Warshall ###
        #
        else:
            #
            ### Populate matrix with edge weights ###
            #
            for src_node_id in self.nodes_edges:
                src_idx: int = node_to_index[src_node_id]
                for dst_node_id in self.get_successors_ids_of_node(src_node_id):
                    dst_idx: int = node_to_index[dst_node_id]
                    matrix[src_idx, dst_idx] = self.nodes_edges[src_node_id][dst_node_id]
                if force_sym_edges_to_exists:
                    for pred_node_id in self.get_predecessors_ids_of_node(src_node_id):
                        pred_idx: int = node_to_index[pred_node_id]
                        matrix[pred_idx, src_idx] = self.nodes_edges[pred_node_id][src_node_id]
            #
            ### Floyd-Warshall algorithm ###
            #
            for k in range(n):
                for i in range(n):
                    for j in range(n):
                        if matrix[i, k] != float('inf') and matrix[k, j] != float('inf'):
                            matrix[i, j] = min(matrix[i, j], matrix[i, k] + matrix[k, j])
        #
        ### Check for negative weights ###
        #
        if self.weighted and np.any(matrix < 0):
            raise UserWarning("Error: Negative weights detected in shortest paths!")
        #
        ### Return distance matrix and node-to-index mapping ###
        #
        return matrix, node_to_index

    #
    ### Function to compute the eccentricity of a node ###
    #
    def get_eccentricity(self, node_id: str, force_sym_edges_to_exists: bool = True) -> float:
        """
        Compute the eccentricity of a node (maximum shortest path distance).

        Args:
            node_id (str): The ID of the node.
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to True.

        Returns:
            float: The eccentricity of the node.

        Raises:
            UserWarning: If the node does not exist.
        """

        #
        ### Check for node existence ###
        #
        if node_id not in self.nodes:
            raise UserWarning(f"Error: Node with node_id=`{node_id}` does not exist in the graph !")
        #
        ### Run Dijkstra's algorithm ###
        #
        distances, _ = self.dijkstra(node_id)
        #
        ### Consider predecessors for undirected graphs ###
        #
        if force_sym_edges_to_exists:
            for pred_node_id in self.get_predecessors_ids_of_node(node_id):
                weight: float = self.get_edge_weight(pred_node_id, node_id) if self.weighted else 1.0
                distances[pred_node_id] = min(distances[pred_node_id], weight)
        #
        ### Find maximum finite distance ###
        #
        max_distance: float = max((d for d in distances.values() if d != float('inf')), default=0.0)
        #
        ### Return eccentricity ###
        #
        return max_distance

    #
    ### Function to find the center of the graph ###
    #
    def get_center(self, force_sym_edges_to_exists: bool = True) -> list[str]:
        """
        Find the center of the graph (nodes with minimum eccentricity).

        Args:
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to True.

        Returns:
            list[str]: A list of node IDs in the center.

        Raises:
            UserWarning: If the graph is not connected.
        """

        #
        ### Check if graph is connected ###
        #
        if not self.is_connected(force_sym_edges_to_exists=force_sym_edges_to_exists):
            raise UserWarning("Error: Graph is not connected, center is undefined!")
        #
        ### Compute eccentricity for each node ###
        #
        eccentricities: dict[str, float] = {}
        for node_id in self.nodes:
            eccentricities[node_id] = self.get_eccentricity(node_id, force_sym_edges_to_exists)
        #
        ### Find minimum eccentricity ###
        #
        min_ecc: float = min(eccentricities.values())
        #
        ### Collect nodes with minimum eccentricity ###
        #
        center_nodes: list[str] = [node_id for node_id, ecc in eccentricities.items() if ecc == min_ecc]
        #
        ### Return center nodes ###
        #
        return center_nodes

    #
    ### Function to check if graph is bipartite and return a bipartition ###
    #
    def get_bipartite_partition(self, force_sym_edges_to_exists: bool = True) -> dict[str, int]:
        """
        Check if the graph is bipartite and return its bipartition.

        Args:
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to True.

        Returns:
            dict[str, int]: A dictionary mapping nodes to their partition (0 or 1).

        Raises:
            UserWarning: If the graph is not bipartite.
        """

        #
        ### Initialize colors (0 or 1 for partitions, None for unvisited) ###
        #
        colors: dict[str, Optional[int]] = {node_id: None for node_id in self.nodes}
        #
        ### BFS to assign colors ###
        #
        def color_bfs(start_node_id: str) -> bool:
            colors[start_node_id] = 0
            queue: list[str] = [start_node_id]
            while queue:
                curr_node_id: str = queue.pop(0)
                curr_color: int = colors[curr_node_id]
                neighbors: list[str] = self.get_successors_ids_of_node(curr_node_id)
                if force_sym_edges_to_exists:
                    neighbors += [n for n in self.get_predecessors_ids_of_node(curr_node_id) if n not in neighbors]
                for neighbor_id in neighbors:
                    if colors[neighbor_id] is None:
                        colors[neighbor_id] = 1 - curr_color
                        queue.append(neighbor_id)
                    elif colors[neighbor_id] == curr_color:
                        return False
            return True
        #
        ### Check all components ###
        #
        for node_id in self.nodes:
            if colors[node_id] is None:
                if not color_bfs(node_id):
                    raise UserWarning("Error: Graph is not bipartite!")
        #
        ### Return partition mapping ###
        #
        return {node_id: color for node_id, color in colors.items() if color is not None}

    #
    ### Function to compute the maximum flow between source and sink ###
    #
    def get_maximum_flow(self, src_node_id: str, sink_node_id: str) -> tuple[float, 'Graph']:
        """
        Compute the maximum flow between a source and sink node using the Edmonds-Karp algorithm.

        Args:
            src_node_id (str): The ID of the source node.
            sink_node_id (str): The ID of the sink node.

        Returns:
            tuple[float, Graph]: A tuple containing the maximum flow value and the residual graph.

        Raises:
            UserWarning: If the graph is unweighted, if either node does not exist, or if source and sink are the same.
        """

        #
        ### Check for valid input ###
        #
        if not self.weighted:
            raise UserWarning("Error: Maximum flow requires a weighted graph!")
        if src_node_id not in self.nodes:
            raise UserWarning(f"Error: Source node with node_id=`{src_node_id}` does not exist in the graph !")
        if sink_node_id not in self.nodes:
            raise UserWarning(f"Error: Sink node with node_id=`{sink_node_id}` does not exist in the graph !")
        if src_node_id == sink_node_id:
            raise UserWarning("Error: Source and sink nodes must be different!")
        #
        ### Create residual graph ###
        #
        residual_graph: Graph = self.copy()
        flow: float = 0.0
        #
        ### BFS to find augmenting path ###
        #
        def bfs_augmenting_path() -> Optional[dict[str, Optional[str]]]:
            visited: set[str] = {src_node_id}
            predecessors: dict[str, Optional[str]] = {src_node_id: None}
            queue: list[str] = [src_node_id]
            while queue:
                curr_node_id: str = queue.pop(0)
                if curr_node_id in residual_graph.nodes_edges:
                    for neighbor_id in residual_graph.get_successors_ids_of_node(curr_node_id):
                        if neighbor_id not in visited and residual_graph.nodes_edges[curr_node_id][neighbor_id] > 0:
                            visited.add(neighbor_id)
                            predecessors[neighbor_id] = curr_node_id
                            queue.append(neighbor_id)
                            if neighbor_id == sink_node_id:
                                return predecessors
            return None
        #
        ### Edmonds-Karp algorithm ###
        #
        while True:
            predecessors = bfs_augmenting_path()
            if predecessors is None:
                break
            #
            ### Find bottleneck capacity ###
            #
            bottleneck: float = float('inf')
            curr_node_id: str = sink_node_id
            while curr_node_id != src_node_id:
                pred_node_id: str = predecessors[curr_node_id]
                bottleneck = min(bottleneck, residual_graph.nodes_edges[pred_node_id][curr_node_id])
                curr_node_id = pred_node_id
            #
            ### Update residual graph and flow ###
            #
            flow += bottleneck
            curr_node_id = sink_node_id
            while curr_node_id != src_node_id:
                pred_node_id = predecessors[curr_node_id]
                residual_graph.nodes_edges[pred_node_id][curr_node_id] -= bottleneck
                if residual_graph.nodes_edges[pred_node_id][curr_node_id] == 0:
                    residual_graph.remove_edge(pred_node_id, curr_node_id)
                if curr_node_id not in residual_graph.nodes_edges:
                    residual_graph.nodes_edges[curr_node_id] = {}
                residual_graph.nodes_edges[curr_node_id][pred_node_id] = residual_graph.nodes_edges.get(curr_node_id, {}).get(pred_node_id, 0) + bottleneck
                curr_node_id = pred_node_id
        #
        ### Return maximum flow and residual graph ###
        #
        return flow, residual_graph

    #
    ### Function to compute the minimum cut between source and sink ###
    #
    def get_minimum_cut(self, src_node_id: str, sink_node_id: str) -> tuple[list[tuple[str, str, float]], float]:
        """
        Compute the minimum cut between a source and sink node.

        Args:
            src_node_id (str): The ID of the source node.
            sink_node_id (str): The ID of the sink node.

        Returns:
            tuple[list[tuple[str, str, float]], float]: A tuple containing the list of cut edges and the cut value.

        Raises:
            UserWarning: If the graph is unweighted, if either node does not exist, or if source and sink are the same.
        """

        #
        ### Check for valid input ###
        #
        if not self.weighted:
            raise UserWarning("Error: Minimum cut requires a weighted graph!")
        if src_node_id not in self.nodes:
            raise UserWarning(f"Error: Source node with node_id=`{src_node_id}` does not exist in the graph !")
        if sink_node_id not in self.nodes:
            raise UserWarning(f"Error: Sink node with node_id=`{sink_node_id}` does not exist in the graph !")
        if src_node_id == sink_node_id:
            raise UserWarning("Error: Source and sink nodes must be different!")
        #
        ### Compute maximum flow to get residual graph ###
        #
        flow, residual_graph = self.get_maximum_flow(src_node_id, sink_node_id)
        #
        ### Find nodes reachable from source in residual graph ###
        #
        reachable: set[str] = set()
        queue: list[str] = [src_node_id]
        reachable.add(src_node_id)
        while queue:
            curr_node_id: str = queue.pop(0)
            if curr_node_id in residual_graph.nodes_edges:
                for neighbor_id in residual_graph.get_successors_ids_of_node(curr_node_id):
                    if neighbor_id not in reachable and residual_graph.nodes_edges[curr_node_id][neighbor_id] > 0:
                        reachable.add(neighbor_id)
                        queue.append(neighbor_id)
        #
        ### Identify cut edges (from reachable to non-reachable nodes) ###
        #
        cut_edges: list[tuple[str, str, float]] = []
        cut_value: float = 0.0
        for src_node_id in reachable:
            for dst_node_id in self.get_successors_ids_of_node(src_node_id):
                if dst_node_id not in reachable:
                    weight: float = self.nodes_edges[src_node_id][dst_node_id]
                    cut_edges.append((src_node_id, dst_node_id, weight))
                    cut_value += weight
        #
        ### Return cut edges and cut value ###
        #
        return cut_edges, cut_value

    #
    ### Function to check if the graph is a tree ###
    #
    def is_tree(self, force_sym_edges_to_exists: bool = True) -> bool:
        """
        Check if the graph is a tree.

        Args:
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to True.

        Returns:
            bool: True if the graph is a tree, False otherwise.
        """

        #
        ### Handle empty graph ###
        #
        if not self.nodes:
            return True
        #
        ### For undirected graphs: check if connected and acyclic ###
        #
        if force_sym_edges_to_exists:
            return self.is_connected(force_sym_edges_to_exists=True) and not self.has_cycle(force_sym_edges_to_exists=True)
        #
        ### For directed graphs: check for single root and no cycles ###
        #
        if self.has_cycle(force_sym_edges_to_exists=False):
            return False
        root_count: int = 0
        for node_id in self.nodes:
            if self.get_in_degree(node_id) == 0:
                root_count += 1
            elif self.get_in_degree(node_id) != 1:
                return False
            if root_count > 1:
                return False
        return root_count == 1

    #
    ### Function to find bridges in the graph ###
    #
    def get_bridges(self, force_sym_edges_to_exists: bool = True) -> list[tuple[str, str]]:
        """
        Find all bridges in the graph.

        Args:
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to True.

        Returns:
            list[tuple[str, str]]: A list of tuples representing bridge edges.

        Raises:
            UserWarning: If the graph is directed (force_sym_edges_to_exists is False).
        """

        #
        ### Check for undirected graph ###
        #
        if not force_sym_edges_to_exists:
            raise UserWarning("Error: Bridges are defined for undirected graphs only!")
        #
        ### Initialize discovery and low-link values ###
        #
        discovery: dict[str, int] = {}
        low: dict[str, int] = {}
        parent: dict[str, Optional[str]] = {}
        time: list[int] = [0]
        bridges: list[tuple[str, str]] = []
        #
        ### DFS to find bridges ###
        #
        def dfs_bridge(node_id: str) -> None:
            discovery[node_id] = low[node_id] = time[0]
            time[0] += 1
            neighbors: list[str] = self.get_successors_ids_of_node(node_id)
            neighbors += [n for n in self.get_predecessors_ids_of_node(node_id) if n not in neighbors]
            for neighbor_id in neighbors:
                if neighbor_id not in discovery:
                    parent[neighbor_id] = node_id
                    dfs_bridge(neighbor_id)
                    low[node_id] = min(low[node_id], low[neighbor_id])
                    if low[neighbor_id] > discovery[node_id]:
                        bridges.append((min(node_id, neighbor_id), max(node_id, neighbor_id)))
                elif neighbor_id != parent.get(node_id):
                    low[node_id] = min(low[node_id], discovery[neighbor_id])
        #
        ### Run DFS on all unvisited nodes ###
        #
        for node_id in self.nodes:
            if node_id not in discovery:
                parent[node_id] = None
                dfs_bridge(node_id)
        #
        ### Return sorted bridges for consistent output ###
        #
        return sorted(bridges)

    #
    ### Function to find articulation points in the graph ###
    #
    def get_articulation_points(self, force_sym_edges_to_exists: bool = True) -> list[str]:
        """
        Find all articulation points in the graph.

        Args:
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to True.

        Returns:
            list[str]: A list of node IDs that are articulation points.

        Raises:
            UserWarning: If the graph is directed (force_sym_edges_to_exists is False).
        """

        #
        ### Check for undirected graph ###
        #
        if not force_sym_edges_to_exists:
            raise UserWarning("Error: Articulation points are defined for undirected graphs only!")
        #
        ### Initialize discovery, low-link, and parent ###
        #
        discovery: dict[str, int] = {}
        low: dict[str, int] = {}
        parent: dict[str, Optional[str]] = {}
        time: list[int] = [0]
        articulation_points: set[str] = set()
        #
        ### DFS to find articulation points ###
        #
        def dfs_articulation(node_id: str, root_children: list[int]) -> None:
            discovery[node_id] = low[node_id] = time[0]
            time[0] += 1
            child_count: int = 0
            neighbors: list[str] = self.get_successors_ids_of_node(node_id)
            neighbors += [n for n in self.get_predecessors_ids_of_node(node_id) if n not in neighbors]
            for neighbor_id in neighbors:
                if neighbor_id not in discovery:
                    child_count += 1
                    parent[neighbor_id] = node_id
                    dfs_articulation(neighbor_id, root_children)
                    low[node_id] = min(low[node_id], low[neighbor_id])
                    if parent[node_id] is None:
                        root_children[0] += 1
                        if root_children[0] >= 2:
                            articulation_points.add(node_id)
                    elif low[neighbor_id] >= discovery[node_id]:
                        articulation_points.add(node_id)
                elif neighbor_id != parent.get(node_id):
                    low[node_id] = min(low[node_id], discovery[neighbor_id])
        #
        ### Run DFS on all unvisited nodes ###
        #
        for node_id in self.nodes:
            if node_id not in discovery:
                parent[node_id] = None
                root_children: list[int] = [0]
                dfs_articulation(node_id, root_children)
        #
        ### Return sorted articulation points ###
        #
        return sorted(list(articulation_points))

    #
    ### Function to get the number of nodes in the graph ###
    #
    def get_node_count(self) -> int:
        """
        Get the number of nodes in the graph.

        Returns:
            int: The number of nodes.
        """

        #
        ### Return the number of nodes ###
        #
        return len(self.nodes)

    #
    ### Function to get the number of edges in the graph ###
    #
    def get_edge_count(self) -> int:
        """
        Get the number of edges in the graph.

        Returns:
            int: The number of edges.
        """

        #
        ### Initialize edge count ###
        #
        count: int = 0
        #
        ### Count edges in nodes_edges ###
        #
        for src_node_id in self.nodes_edges:
            count += len(self.nodes_edges[src_node_id])
        #
        ### Return edge count ###
        #
        return count

    #
    ### Function to check if the graph is empty ###
    #
    def is_empty(self) -> bool:
        """
        Check if the graph is empty.

        Returns:
            bool: True if the graph has no nodes, False otherwise.
        """

        #
        ### Return True if graph has no nodes ###
        #
        return len(self.nodes) == 0

    #
    ### Function to check if a path exists between two nodes ###
    #
    def has_path(self, src_node_id: str, dst_node_id: str, force_sym_edges_to_exists: bool = False) -> bool:
        """
        Check if a path exists between two nodes.

        Args:
            src_node_id (str): The ID of the source node.
            dst_node_id (str): The ID of the destination node.
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to False.

        Returns:
            bool: True if a path exists, False otherwise.

        Raises:
            UserWarning: If either node does not exist.
        """

        #
        ### Check for source and destination node existence ###
        #
        if src_node_id not in self.nodes:
            raise UserWarning(f"Error: Source node with node_id=`{src_node_id}` does not exist in the graph !")
        if dst_node_id not in self.nodes:
            raise UserWarning(f"Error: Destination node with node_id=`{dst_node_id}` does not exist in the graph !")
        #
        ### Use BFS to check reachability ###
        #
        nodes_marks: dict[str, int] = self.explore_from_source(
            src_node_id=src_node_id,
            exploration_algorithm="bfs",
            force_sym_edges_to_exists=force_sym_edges_to_exists,
            fn_to_mark_nodes=lambda _: 1
        )
        #
        ### Return True if destination was visited ###
        #
        return dst_node_id in nodes_marks

    #
    ### Function to compute all-pairs shortest paths with actual paths ###
    #
    def get_all_pairs_shortest_paths_with_paths(self, force_sym_edges_to_exists: bool = True) -> tuple[np.ndarray, dict[str, int], dict[str, dict[str, Optional[str]]]]:
        """
        Compute all-pairs shortest paths with predecessor information.

        Args:
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to True.

        Returns:
            tuple[np.ndarray, dict[str, int], dict[str, dict[str, Optional[str]]]]: A tuple containing the distance matrix, node-to-index mapping, and predecessors.

        Raises:
            UserWarning: If negative weights are detected in a weighted graph.
        """

        #
        ### Get list of node IDs for consistent ordering ###
        #
        node_ids: list[str] = list(self.nodes.keys())
        n: int = len(node_ids)
        #
        ### Create mapping of node IDs to indices ###
        #
        node_to_index: dict[str, int] = {node_id: i for i, node_id in enumerate(node_ids)}
        #
        ### Initialize distance matrix and predecessor dictionary ###
        #
        matrix: np.ndarray = np.full((n, n), float('inf'), dtype=float)
        np.fill_diagonal(matrix, 0)
        predecessors: dict[str, dict[str, Optional[str]]] = {node_id: {n: None for n in node_ids} for node_id in node_ids}
        #
        ### For unweighted graphs, use BFS ###
        #
        if not self.weighted:
            for src_node_id in node_ids:
                distances, preds = self.dijkstra(src_node_id)
                src_idx: int = node_to_index[src_node_id]
                for dst_node_id, dist in distances.items():
                    dst_idx: int = node_to_index[dst_node_id]
                    matrix[src_idx, dst_idx] = dist
                    predecessors[src_node_id][dst_node_id] = preds[dst_node_id]
                if force_sym_edges_to_exists:
                    for pred_node_id in self.get_predecessors_ids_of_node(src_node_id):
                        pred_idx: int = node_to_index[pred_node_id]
                        matrix[pred_idx, src_idx] = 1.0
                        predecessors[pred_node_id][src_node_id] = src_node_id
        #
        ### For weighted graphs, use Floyd-Warshall ###
        #
        else:
            #
            ### Populate matrix with edge weights ###
            #
            for src_node_id in self.nodes_edges:
                src_idx: int = node_to_index[src_node_id]
                for dst_node_id in self.get_successors_ids_of_node(src_node_id):
                    dst_idx: int = node_to_index[dst_node_id]
                    matrix[src_idx, dst_idx] = self.nodes_edges[src_node_id][dst_node_id]
                    predecessors[src_node_id][dst_node_id] = dst_node_id
                if force_sym_edges_to_exists:
                    for pred_node_id in self.get_predecessors_ids_of_node(src_node_id):
                        pred_idx: int = node_to_index[pred_node_id]
                        matrix[pred_idx, src_idx] = self.nodes_edges[pred_node_id][src_node_id]
                        predecessors[pred_node_id][src_node_id] = src_node_id
            #
            ### Floyd-Warshall algorithm with predecessors ###
            #
            for k in range(n):
                for i in range(n):
                    for j in range(n):
                        if matrix[i, k] != float('inf') and matrix[k, j] != float('inf'):
                            if matrix[i, j] > matrix[i, k] + matrix[k, j]:
                                matrix[i, j] = matrix[i, k] + matrix[k, j]
                                predecessors[node_ids[i]][node_ids[j]] = predecessors[node_ids[i]][node_ids[k]]
        #
        ### Check for negative weights ###
        #
        if self.weighted and np.any(matrix < 0):
            raise UserWarning("Error: Negative weights detected in shortest paths!")
        #
        ### Return distance matrix, node-to-index mapping, and predecessors ###
        #
        return matrix, node_to_index, predecessors

    #
    ### Function to find an Eulerian path or circuit in the graph ###
    #
    def get_eulerian_path(self, force_sym_edges_to_exists: bool = True) -> list[str]:
        """
        Find an Eulerian path or circuit in the graph.

        Args:
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to True.

        Returns:
            list[str]: A list of node IDs forming an Eulerian path or circuit.

        Raises:
            UserWarning: If the graph does not satisfy Eulerian path conditions or is not connected.
        """

        #
        ### Check if graph is empty ###
        #
        if not self.nodes:
            return []
        #
        ### Check degree conditions ###
        #
        odd_degree_nodes: list[str] = []
        start_node: Optional[str] = None
        if force_sym_edges_to_exists:
            for node_id in self.nodes:
                degree: int = self.get_degree(node_id)
                if degree % 2 == 1:
                    odd_degree_nodes.append(node_id)
            if len(odd_degree_nodes) > 2:
                raise UserWarning("Error: Graph has more than two nodes with odd degree, no Eulerian path exists!")
            start_node = odd_degree_nodes[0] if odd_degree_nodes else next(iter(self.nodes))
        else:
            out_minus_in: list[str] = []
            for node_id in self.nodes:
                out_deg: int = self.get_out_degree(node_id)
                in_deg: int = self.get_in_degree(node_id)
                if out_deg == in_deg + 1:
                    start_node = node_id
                elif out_deg + 1 == in_deg:
                    out_minus_in.append(node_id)
                elif out_deg != in_deg:
                    raise UserWarning("Error: Graph does not satisfy Eulerian path conditions for directed graph!")
            if len(out_minus_in) > 1 or (start_node is None and out_minus_in):
                raise UserWarning("Error: Graph does not satisfy Eulerian path conditions for directed graph!")
            if start_node is None:
                start_node = next(iter(self.nodes))
        #
        ### Check if graph is connected ###
        #
        if not self.is_connected(force_sym_edges_to_exists=force_sym_edges_to_exists):
            raise UserWarning("Error: Graph is not connected, no Eulerian path exists!")
        #
        ### Create a copy of edges to modify ###
        #
        edge_copy: dict[str, list[str]] = {}
        for src_node_id in self.nodes_edges:
            edge_copy[src_node_id] = list(self.get_successors_ids_of_node(src_node_id))
            if force_sym_edges_to_exists:
                edge_copy[src_node_id] += [n for n in self.get_predecessors_ids_of_node(src_node_id) if n not in edge_copy[src_node_id]]
        #
        ### Hierholzer’s algorithm ###
        #
        path: list[str] = []
        circuit: list[str] = [start_node]
        while circuit:
            current: str = circuit[-1]
            if current in edge_copy and edge_copy[current]:
                next_node: str = edge_copy[current].pop()
                if force_sym_edges_to_exists:
                    edge_copy[next_node].remove(current)
                circuit.append(next_node)
            else:
                path.append(circuit.pop())
        #
        ### Reverse path to get correct order ###
        #
        path.reverse()
        #
        ### Verify all edges used ###
        #
        for src in edge_copy:
            if edge_copy[src]:
                raise UserWarning("Error: Not all edges were used, graph may not have an Eulerian path!")
        #
        ### Return Eulerian path ###
        #
        return path

    #
    ### Function to find a Hamiltonian path or cycle in the graph ###
    #
    def get_hamiltonian_path(self, force_sym_edges_to_exists: bool = True, find_cycle: bool = False) -> list[str]:
        """
        Find a Hamiltonian path or cycle in the graph.

        Args:
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to True.
            find_cycle (bool, optional): If True, find a Hamiltonian cycle instead of a path. Defaults to False.

        Returns:
            list[str]: A list of node IDs forming a Hamiltonian path or cycle.

        Raises:
            UserWarning: If no Hamiltonian path or cycle exists.
        """

        #
        ### Warning for computational complexity ###
        #
        if len(self.nodes) > 20:
            print("Warning: Hamiltonian path computation is NP-complete and may be slow for large graphs!")
        #
        ### Initialize path and visited set ###
        #
        path: list[str] = []
        visited: set[str] = set()
        start_node: str = next(iter(self.nodes)) if self.nodes else ""
        #
        ### Backtracking helper function ###
        #
        def backtrack(current: str, nodes_visited: int) -> bool:
            if nodes_visited == len(self.nodes):
                if find_cycle:
                    neighbors: list[str] = self.get_successors_ids_of_node(current)
                    if force_sym_edges_to_exists:
                        neighbors += [n for n in self.get_predecessors_ids_of_node(current) if n not in neighbors]
                    return start_node in neighbors
                return True
            for neighbor_id in self.get_successors_ids_of_node(current):
                if force_sym_edges_to_exists:
                    neighbors: list[str] = self.get_successors_ids_of_node(current)
                    neighbors += [n for n in self.get_predecessors_ids_of_node(current) if n not in neighbors]
                else:
                    neighbors = self.get_successors_ids_of_node(current)
                for neighbor_id in neighbors:
                    if neighbor_id not in visited:
                        visited.add(neighbor_id)
                        path.append(neighbor_id)
                        if backtrack(neighbor_id, nodes_visited + 1):
                            return True
                        visited.remove(neighbor_id)
                        path.pop()
            return False
        #
        ### Check if graph is empty ###
        #
        if not self.nodes:
            return []
        #
        ### Start backtracking ###
        #
        path.append(start_node)
        visited.add(start_node)
        if not backtrack(start_node, 1):
            raise UserWarning("Error: No Hamiltonian path or cycle exists in the graph!")
        #
        ### Return Hamiltonian path ###
        #
        return path

    #
    ### Function to compute betweenness centrality for each node ###
    #
    def get_betweenness_centrality(self, force_sym_edges_to_exists: bool = True) -> dict[str, float]:
        """
        Compute the betweenness centrality for each node.

        Args:
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to True.

        Returns:
            dict[str, float]: A dictionary mapping node IDs to their betweenness centrality scores.
        """

        #
        ### Get all-pairs shortest paths with predecessors ###
        #
        matrix, node_to_index, predecessors = self.get_all_pairs_shortest_paths_with_paths(force_sym_edges_to_exists)
        #
        ### Initialize centrality scores ###
        #
        centrality: dict[str, float] = {node_id: 0.0 for node_id in self.nodes}
        n: int = len(self.nodes)
        #
        ### Compute shortest paths and count node occurrences ###
        #
        for src_node_id in self.nodes:
            for dst_node_id in self.nodes:
                if src_node_id == dst_node_id:
                    continue
                if matrix[node_to_index[src_node_id], node_to_index[dst_node_id]] == float('inf'):
                    continue
                #
                ### Reconstruct all shortest paths using predecessors ###
                #
                paths: list[list[str]] = []
                stack: list[tuple[str, list[str]]] = [(dst_node_id, [dst_node_id])]
                while stack:
                    current, path = stack.pop()
                    pred = predecessors[src_node_id][current]
                    if pred is None:
                        if current == src_node_id:
                            paths.append(path[::-1])
                        continue
                    new_path = path + [pred]
                    stack.append((pred, new_path))
                #
                ### Count node occurrences in shortest paths ###
                #
                for path in paths:
                    for node_id in path[1:-1]:  # Exclude source and destination
                        centrality[node_id] += 1.0 / len(paths)
        #
        ### Normalize centrality scores ###
        #
        for node_id in centrality:
            centrality[node_id] /= ((n - 1) * (n - 2) / 2) if n > 2 else 1
        #
        ### Return centrality scores ###
        #
        return centrality

    #
    ### Function to compute closeness centrality for each node ###
    #
    def get_closeness_centrality(self, force_sym_edges_to_exists: bool = True) -> dict[str, float]:
        """
        Compute the closeness centrality for each node.

        Args:
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to True.

        Returns:
            dict[str, float]: A dictionary mapping node IDs to their closeness centrality scores.
        """

        #
        ### Initialize centrality scores ###
        #
        centrality: dict[str, float] = {node_id: 0.0 for node_id in self.nodes}
        n: int = len(self.nodes)
        #
        ### Compute shortest path distances for each node ###
        #
        for node_id in self.nodes:
            distances, _ = self.dijkstra(node_id)
            if force_sym_edges_to_exists:
                for pred_node_id in self.get_predecessors_ids_of_node(node_id):
                    weight: float = self.get_edge_weight(pred_node_id, node_id) if self.weighted else 1.0
                    distances[pred_node_id] = min(distances[pred_node_id], weight)
            #
            ### Sum finite distances ###
            #
            total_distance: float = sum(d for d in distances.values() if d != float('inf'))
            if total_distance > 0:
                centrality[node_id] = (n - 1) / total_distance
            else:
                centrality[node_id] = 0.0
        #
        ### Return centrality scores ###
        #
        return centrality

    #
    ### Function to compute degree centrality for each node ###
    #
    def get_degree_centrality(self, force_sym_edges_to_exists: bool = True) -> dict[str, float]:
        """
        Compute the degree centrality for each node.

        Args:
            force_sym_edges_to_exists (bool, optional): Treat the graph as undirected. Defaults to True.

        Returns:
            dict[str, float]: A dictionary mapping node IDs to their degree centrality scores.
        """

        #
        ### Initialize centrality scores ###
        #
        centrality: dict[str, float] = {node_id: 0.0 for node_id in self.nodes}
        n: int = len(self.nodes)
        #
        ### Compute degree for each node ###
        #
        for node_id in self.nodes:
            degree: int = self.get_degree(node_id) if force_sym_edges_to_exists else self.get_out_degree(node_id)
            centrality[node_id] = degree / (n - 1) if n > 1 else 0.0
        #
        ### Return centrality scores ###
        #
        return centrality


    def get_subgraph(self, node_ids: list[str]) -> 'Graph':
        """
        Create a subgraph containing only the specified nodes and edges between them.

        Args:
            node_ids (list[str]): A list of node IDs to include in the subgraph.

        Returns:
            Graph: A new Graph instance containing the specified nodes and their connecting edges.

        Raises:
            UserWarning: If any node ID in the list does not exist in the graph or if the input list is empty.
        """
        # Validate input
        if not node_ids:
            raise UserWarning("The list of node IDs cannot be empty.")

        for node_id in node_ids:
            if node_id not in self._nodes:
                raise UserWarning(f"Node {node_id} does not exist in the graph.")

        # Create a new graph with the same weighted property
        subgraph = Graph(weighted=self._weighted)

        # Add nodes to the subgraph
        for node_id in node_ids:
            node = self._nodes[node_id]
            subgraph.add_node(node_id=node_id, values=node._values.copy() if node._values else None)

        # Add edges between the specified nodes
        for src_id in node_ids:
            src_node = self._nodes[src_id]
            for dst_id, weight in src_node._successors.items():
                if dst_id in node_ids:
                    subgraph.add_edge(src_node_id=src_id, dst_node_id=dst_id, weight=weight)

        return subgraph
