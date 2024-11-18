import pytest
import io
import tarfile
from dependency_visualizer import (
    parse_apkindex,
    build_dependency_graph,
    generate_mermaid_graph
)

@pytest.fixture
def sample_packages():
    apkindex_content = b"""
P:packageA
V:1.0.0
D:packageB packageC

P:packageB
V:1.0.0
D:packageC

P:packageC
V:1.0.0
D:
"""
    # Создаём архив APKINDEX.tar.gz в памяти
    tar_bytes = io.BytesIO()
    with tarfile.open(fileobj=tar_bytes, mode='w:gz') as tar:
        tarinfo = tarfile.TarInfo(name='APKINDEX')
        tarinfo.size = len(apkindex_content)
        tar.addfile(tarinfo, io.BytesIO(apkindex_content))
    tar_bytes.seek(0)
    apkindex_data = tar_bytes.read()

    packages = parse_apkindex(apkindex_data)
    return packages

def test_parse_apkindex(sample_packages):
    assert 'packageA' in sample_packages
    assert 'packageB' in sample_packages
    assert 'packageC' in sample_packages

def test_build_dependency_graph(sample_packages):
    graph = []
    visited = set()
    build_dependency_graph(sample_packages, 'packageA', graph, visited)
    expected_graph = [
        ('packageA', 'packageB'),
        ('packageA', 'packageC'),
        ('packageB', 'packageC')
    ]
    assert sorted(graph) == sorted(expected_graph)

def test_generate_mermaid_graph():
    graph = [('packageA', 'packageB'), ('packageA', 'packageC')]
    mermaid_code = generate_mermaid_graph(graph)
    expected_mermaid = 'graph TD\npackageA --> packageB\npackageA --> packageC\n'
    assert mermaid_code.strip() == expected_mermaid.strip()
