#!/usr/bin/python3

import dnf, json


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
#     "packages": [
#         "package1",
#         "package2"
#     ],
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
    base.conf.installroot = root
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
        name = package["name"]

        # If package is in a group, add it to the group
        if groups:
            for group in groups:
                if name in group["packages"]:
                    node["name"] = group["name"]
                    node["size"] = group["size"]
                    node["dependencies"] = group["requires_resolved"]

                    graph[node["name"]] = node

        # Otherwise (package is not in a group) just add it to the graph
        if not node:
            node["name"] = package["name"]
            node["size"] = package["size"]

            # If groups are involved, this package might depend on a package that's in a group.
            # If that's the case, the "dependencies" field needs to contain the name of that
            # group instead of a name of the package, because the package is not on the graph. The group is.
            if groups:
                pkg_deps = set(package["requires_resolved"])

                for group in groups:
                    group_pkgs = set(group["packages"])
                    requires_in_group = pkg_deps & group_pkgs

                    if requires_in_group:
                        pkg_deps -= requires_in_group
                        pkg_deps.add(group["name"])

                node["dependencies"] = list(pkg_deps)

            else:
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



def packages_to_group(name, packages):

    group = {}
    group["name"] = name
    group["size"] = 0

    group_packages = set()
    requires = set()
    requires_resolved = set()

    for _, package in packages.items():
        group_packages.add(package["name"])

        for req in package["requires"]:
            requires.add(req)

        for req_pkg in package["requires_resolved"]:
            requires_resolved.add(req_pkg)

        group["size"] += package["size"]

    group["packages"] = list(group_packages)
    group["requires"] = list(requires)
    group["requires_resolved"] = list(requires_resolved - group_packages)

    return group



def dump_data(path, data):
    with open(path, 'w') as file:
        json.dump(data, file)



def load_data(path):
    with open(path, 'r') as file:
        data = json.load(file)

    return data



def main():

    base_pkgs = load_data("./container-base-packages.json")
    httpd_pkgs = load_data("./container-httpd-packages.json")

    group = packages_to_group("<<fedora:30 base image>>", base_pkgs)

    graph = compute_graph(httpd_pkgs, [group])
    dot = graph_to_dot(graph)

    print(dot)

#    packages = load_packages("/home/fedora/installs/cowsay")
#
#    packages.pop("glibc", None)
#
#    group = packages_to_group("COWSAY", packages)
#
#    packages2 = load_packages("/home/fedora/installs/cowsay_beefymiracle")
#
#    graph = compute_graph(packages2, [group])
#    dot = graph_to_dot(graph)
#
#    print(dot)
#



if __name__ == "__main__":
    main()







