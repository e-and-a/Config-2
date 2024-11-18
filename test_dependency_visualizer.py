import pytest
from dependency_visualizer import parse_apkindex_content, build_dependency_graph

def test_parse_apkindex_content():
    content = '''
P:package-a
V:1.0.0
D:package-b package-c
T:Example package A

P:package-b
V:1.0.0
D:package-d
T:Example package B

P:package-c
V:1.0.0
D:
T:Example package C

P:package-d
V:1.0.0
D:
T:Example package D
'''
    packages = parse_apkindex_content(content)
    assert len(packages) == 4
    assert 'package-a' in packages
    assert packages['package-a']['D'] == 'package-b package-c'

def test_build_dependency_graph():
    packages = {
        'package-a': {'D': 'package-b package-c'},
        'package-b': {'D': 'package-d'},
        'package-c': {'D': ''},
        'package-d': {'D': ''},
    }
    graph = []
    visited = set()
    build_dependency_graph(packages, 'package-a', graph, visited)
    assert len(graph) == 3
    assert ('package-a', 'package-b') in graph
    assert ('package-a', 'package-c') in graph
    assert ('package-b', 'package-d') in graph
