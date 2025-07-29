# nagraph

A Python library for graph data structures and algorithms.

## Installation

```bash
pip install nagraph
```

## Usage

```py
from nagraph import Graph, GraphNode

# Create a graph
g = Graph(weighted=True)
node1 = g.add_node("1")
node2 = g.add_node("2")
g.add_edge("1", "2", weight=1.5)

# Example: Find shortest path
path = g.get_shortest_path("1", "2")
print(path)  # ['1', '2']
```

## Documentation

Full documentation is available at [link]().

## License

[MIT License](LICENSE)
