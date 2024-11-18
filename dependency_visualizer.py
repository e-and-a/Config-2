import sys
import os
import subprocess
import argparse

def parse_apkindex_content(content):
    packages = {}
    entries = content.strip().split('\n\n')
    for entry in entries:
        pkg_info = {}
        lines = entry.strip().split('\n')
        for line in lines:
            if line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key, value = parts
                    pkg_info[key.strip()] = value.strip()
        if 'P' in pkg_info:
            pkg_name = pkg_info['P'].strip().lower()
            packages[pkg_name] = pkg_info
    return packages

def build_dependency_graph(packages, pkg_name, graph, visited, depth=0, max_depth=10):
    pkg_name = pkg_name.strip().lower()
    if pkg_name not in packages:
        print(f"Пакет '{pkg_name}' не найден в репозитории.")
        return
    if pkg_name in visited:
        return
    if depth > max_depth:
        return
    visited.add(pkg_name)
    pkg_info = packages[pkg_name]
    deps_line = pkg_info.get('D', '')
    deps = deps_line.strip().split()
    for dep in deps:
        dep = dep.strip().lower()
        if dep:
            graph.append((pkg_name, dep))
            build_dependency_graph(packages, dep, graph, visited, depth + 1, max_depth)

def generate_mermaid_graph(graph):
    mermaid = 'graph TD\n'
    for src, dst in graph:
        mermaid += f'    {src} --> {dst}\n'
    return mermaid

def visualize_graph(mermaid_code, renderer_path):
    output_image = 'graph.png'
    tmpfile_path = 'graph.mmd'
    with open(tmpfile_path, 'w', encoding='utf-8') as tmpfile:
        tmpfile.write(mermaid_code)

    try:
        subprocess.run(
            [renderer_path, '-i', tmpfile_path, '-o', output_image],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"Граф успешно сохранён в {output_image}")
    except subprocess.CalledProcessError as e:
        print("Ошибка при визуализации графа:")
        print(e.stderr)
    except Exception as e:
        print(f"Ошибка при визуализации графа: {e}")

def main():
    parser = argparse.ArgumentParser(description='Визуализатор зависимостей пакетов Alpine Linux.')
    parser.add_argument('--renderer', required=True, help='Путь к программе для визуализации графов (например, mmdc).')
    parser.add_argument('--package', required=True, help='Имя анализируемого пакета.')
    args = parser.parse_args()

    args.package = args.package.strip().lower()

    try:
        with open('APKINDEX', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("Файл APKINDEX не найден. Убедитесь, что он находится в текущей директории.")
        sys.exit(1)

    packages = parse_apkindex_content(content)

    if args.package not in packages:
        print(f"Пакет '{args.package}' не найден в репозитории.")
        sys.exit(1)

    graph = []
    visited = set()
    build_dependency_graph(packages, args.package, graph, visited)

    if not graph:
        print(f"Пакет '{args.package}' не имеет зависимостей.")
        sys.exit(0)

    mermaid_code = generate_mermaid_graph(graph)
    print("Сгенерирован код диаграммы Mermaid:")
    print(mermaid_code)

    visualize_graph(mermaid_code, args.renderer)

if __name__ == '__main__':
    main()
