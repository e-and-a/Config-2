import random

def generate_apkindex(num_packages=1000):
    packages = []
    for i in range(1, num_packages + 1):
        pkg_name = f"package-{i}"
        version = "1.0.0"
        # Каждому пакету дадим от 0 до 5 случайных зависимостей на пакеты с меньшим номером
        num_deps = random.randint(0, 5)
        if i > 1:
            deps = random.sample([f"package-{j}" for j in range(1, i)], min(num_deps, i - 1))
        else:
            deps = []
        pkg_entry = f"""P:{pkg_name}
V:{version}
D:{' '.join(deps)}
T:Example package {i}
"""
        packages.append(pkg_entry)
    # Объединяем все записи пакетов с двумя переносами строки
    apkindex_content = "\n\n".join(packages)
    with open("APKINDEX", "w", encoding="utf-8") as f:
        f.write(apkindex_content)
    print(f"Сгенерирован файл APKINDEX с {num_packages} пакетами.")

if __name__ == "__main__":
    generate_apkindex()
