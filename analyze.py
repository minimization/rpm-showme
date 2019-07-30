#!/usr/bin/python3

import dnf


# === Data Structures ===
#
# data = {
#     "packages": {
#         "package1": Package,
#         "package2": Package
#     },
#     "groups": {
#         "group1": Group,
#         "group2": Group
#     },
#     "graph": {
#         "node1": Node,
#         "node2": Node
#     }
# }
# 
# 
# Package = {
#     "name": "package",
#     "epoch": "",
#     "version": "2.4",
#     "release": "3.fc36",
#     "arch": "arm",
#     "nevra": "package-2.4-3.fc36.arm"
#     "size": 432423,
#     "requires": [
#         "capability 1",
#         "capability 2"
#     ],
#     "requires_resolved": [
#         "package2",
#         "package3"
#     ]
# }
# 
# Group = {
#     "name": "group",
#     "size": 423432423,
#     "requires": [
#         "capability 1",
#         "capability 2"
#     ],
#     "requires_resolved": [
#         "package2",
#         "package3"
#     ]
# }
# 
# Node = {
#     "name": "node",
#     "size": 323232,
#     "dependencies": [
#         "node1",
#         "node2",
#     ]
# }



def load_packages(root="/", releasever=None):

    # Look at the system and get a list of all installed RPM packages
    # in the as a list of DNF Package objects
    base = dnf.Base()
    if releasever:
        base.conf.substitutions['releasever'] = releasever
    base.conf.installroot = "/home/fedora/test"
    base.fill_sack(load_available_repos=False)
    query = base.sack.query()
    installed = list(query.installed())

    # Make it into a list of my Package structures
    packages = {}
    for pkg in installed:
        package = {}
        package["name"] = pkg.name
        package["epoch"] = pkg.epoch
        package["version"] = pkg.version
        package["release"] = pkg.release
        package["arch"] = pkg.arch
        package["nevra"] = str(pkg)
        package["size"] = pkg.installsize
        package["requires"] = []
        package["requires_resolved"] = []

        for req in pkg.requires:
            package["requires"].append(str(req))

        deps = query.installed()
        deps = deps.filter(provides=pkg.requires)
        for dep in deps:
            package["requires_resolved"].append(dep.name)

        packages[package["name"]] = package

    return packages



def compute_graph(packages, groups=None):

    graph = {}

    for _, package in packages.items():
        node = {}
        node["name"] = package["name"]
        node["size"] = package["size"]
        node["dependencies"] = package["requires_resolved"]

        graph[node["name"]] = node

    return graph



def graph_to_dot(graph):

    dot = "digraph packages {\n"

    for _, node in graph.items():
        dot += "\"" + node["name"] + "\" -> {"
        dot += "\n"
        for dep in node["dependencies"]:
            dot += "    \"" + dep + "\""
            dot += "\n"
        dot += "};"
        dot += "\n"

    dot += "}"

    return dot



def main():
    packages = load_packages("/home/fedora/test")
    graph = compute_graph(packages)
    dot = graph_to_dot(graph)
    print(dot)

if __name__ == "__main__":
    main()







