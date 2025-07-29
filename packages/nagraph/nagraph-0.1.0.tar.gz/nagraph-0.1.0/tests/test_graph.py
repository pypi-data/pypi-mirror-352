# tests/test_graph.py
import unittest
from nagraph import Graph, GraphNode

class TestGraph(unittest.TestCase):
    def test_add_node(self):
        g = Graph()
        node = g.add_node("1")
        self.assertEqual(g.get_node("1"), node)

    def test_add_edge(self):
        g = Graph(weighted=True)
        g.add_node("1")
        g.add_node("2")
        g.add_edge("1", "2", weight=1.5)
        self.assertTrue(g.has_edge("1", "2"))
        self.assertEqual(g.get_edge_weight("1", "2"), 1.5)

if __name__ == '__main__':
    unittest.main()