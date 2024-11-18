import sys
import os
import tarfile
import re
import tempfile
import subprocess
import argparse

def download_apkindex():
    try:
        with open('APKINDEX.tar.gz', 'rb') as f:
            apkindex_data = f.read()
        return apkindex_data
    except Exception as e:
        print(f"Ошибка при загрузке APKINDEX: {e}")
        sys.exit(1)

def parse_apkindex_content(content):
    packages = {}
    entries = content.strip().split('\n\n')
    for entry in entries:
        pkg_info = {}
        lines = entry.strip().split('\n')
        for line in lines:
            if line:
                key, value = line[0], line[2:]
                pkg_info[key] = value
        if 'P' in pkg_info:
            pkg_name = pkg_info['P']
            packages[pkg_name] = pkg_info
    return packages

def parse_apkindex(apkindex_data):
    with tempfile.TemporaryDirectory() as tmpdirname:
        apkindex_path = os.path.join(tmpdirname, 'APKINDEX.tar.gz')
        with open(apkindex_path, 'wb') as f:
            f.write(apkindex_data)
        with tarfile.open(apkindex_path, 'r:gz') as tar:
            try:
                member = tar.getmember('APKINDEX')
            except KeyError:
                print("Файл APKINDEX не найден в архиве.")
                sys.exit(1)
            f = tar.extractfile(member)
            content = f.read().decode('utf-8')
            return parse_apkindex_content(content)
    return {}

def build_dependency_graph(packages, pkg_name, graph, visited):
    if pkg_name not in packages:
        print(f"Пакет '{pkg_name}' не найден в репозитории.")
        return
    if pkg_name in visited:
        return
    visited.add(pkg_name)
    pkg_info = packages[pkg_name]
    deps = pkg_info.get('D', '').split()
    for dep in deps:
        dep = re.sub(r'<.*?>', '', dep)  # Удаляем версии зависимостей
        dep = dep.strip()
        if dep:
            graph.append((pkg_name, dep))
            build_dependency_graph(packages, dep, graph, visited)

def generate_mermaid_graph(graph):
    mermaid = 'graph TD\n'
    for src, dst in graph:
        mermaid += f'{src} --> {dst}\n'
    # Сохраняем Mermaid-код в файл для отладки
    with open('mermaid_debug.mmd', 'w', encoding='utf-8') as f:
        f.write(mermaid)
    return mermaid

def visualize_graph(mermaid_code, renderer_path):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False, encoding='utf-8') as tmpfile:
        tmpfile.write(mermaid_code)
        tmpfile_path = tmpfile.name

    output_image = tmpfile_path + '.png'

    try:
        subprocess.run(
            [renderer_path, '-i', tmpfile_path, '-o', output_image],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Открываем изображение в системе
        if sys.platform == 'darwin':
            subprocess.run(['open', output_image])
        elif sys.platform.startswith('linux'):
            subprocess.run(['xdg-open', output_image])
        elif sys.platform == 'win32':
            os.startfile(output_image)
        else:
            print(f"Граф сохранён в {output_image}")
    except subprocess.CalledProcessError as e:
        print("Ошибка при визуализации графа:")
        print(e.stderr)
    except Exception as e:
        print(f"Ошибка при визуализации графа: {e}")
    finally:
        pass  # Не удаляем временный файл для отладки

def main():
    parser = argparse.ArgumentParser(description='Визуализатор зависимостей пакетов Alpine Linux.')
    parser.add_argument('--renderer', required=True, help='Путь к программе для визуализации графов (например, mmdc).')
    parser.add_argument('--package', required=True, help='Имя анализируемого пакета.')
    args = parser.parse_args()

    apkindex_data = download_apkindex()
    packages = parse_apkindex(apkindex_data)

    graph = []
    visited = set()
    build_dependency_graph(packages, args.package, graph, visited)

    if not graph:
        print(f"Пакет '{args.package}' не имеет зависимостей или не найден.")
        sys.exit(0)

    mermaid_code = generate_mermaid_graph(graph)
    print("Сгенерирован код диаграммы Mermaid:")
    print(mermaid_code)

    visualize_graph(mermaid_code, args.renderer)

if __name__ == '__main__':
    main()
