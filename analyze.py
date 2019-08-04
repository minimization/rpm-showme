#!/usr/bin/python3

import dnf, json, subprocess, tempfile, argparse


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


def _create_packages_structure(installed, query):
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

def load_packages_from_path(root="/", releasever=None):

    # Look at the system and get a list of all installed RPM packages
    # in the as a list of DNF Package objects
    base = dnf.Base()
    if releasever:
        base.conf.substitutions['releasever'] = releasever
    base.conf.installroot = root
    base.fill_sack(load_available_repos=False)
    query = base.sack.query()
    installed = list(query.installed())

    return _create_packages_structure(installed, query)


def load_packages_from_container_image(image):
    base = dnf.Base()
    
    data = subprocess.check_output(['podman', 'inspect', image])
    #size_bytes = json.loads(data)[0]["Size"]

    # Extract DNF and RPM data
    with tempfile.TemporaryDirectory() as tmp:
        cmd = "mkdir -p /workdir/var/lib && cp -r /var/lib/dnf /workdir/var/lib/ && cp -r /var/lib/rpm /workdir/var/lib/"
        subprocess.run(['podman', 'run', '--rm', '-v', tmp+':/workdir:z', '-v', 'copy.sh:/copy.sh:z', image, '/bin/sh', '-c', cmd])
        base.conf.installroot = tmp
        base.fill_sack()

    query = base.sack.query()
    installed = list(query.installed())

    return _create_packages_structure(installed, query)



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

        

def size(num, suffix='B'):
    for unit in ['','k','M','G']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'T', suffix)


def graph_to_dot(graph, sizes=False):

    dot = "digraph packages {\n"

    if sizes:
        for _, node in graph.items():
            dot += "\"" + node["name"] + " (" + size(node["size"])  + ")\" -> {"
            dot += "\n"
            for dep in node["dependencies"]:
                dot += "    \"" + dep + " (" + size(graph[dep]["size"]) + ")\""
                dot += "\n"
            dot += "};"
            dot += "\n"

    else:
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


def dot_to_svg(dot):

    stage1 = subprocess.run(["sfdp", "-Gstart=3", "-Goverlap=prism"], capture_output=True, input=dot, encoding="UTF-8")

    stage2 = subprocess.run(["gvmap", "-e", "-d", "3"], capture_output=True, input=stage1.stdout, encoding="UTF-8")

    stage3 = subprocess.run(["neato", "-Gstart=3", "-n", "-Ecolor=#44444455", "-Tsvg"], capture_output=True, input=stage2.stdout, encoding="UTF-8")

    svg = str(stage3.stdout)

    javascript = """
<script type="text/javascript"><![CDATA[

document.addEventListener('click', function(e) {
      e = e || window.event;
      var target = e.target || e.srcElement;
          text = target.textContent || text.innerText;   

          console.log("Clicked on: " + text);
          // reset all strokes
          var nodes = document.getElementsByClassName("edge");

          for (index = 0, len = nodes.length; index < len; ++index) {
              //var title = nodes[index].querySelector("title").textContent.split("->");
              id = nodes[index].id;
              document.getElementById(id).querySelector("path").setAttribute("stroke-width", "1");
              document.getElementById(id).querySelector("path").setAttribute("stroke-opacity", "0.5");
              document.getElementById(id).querySelector("path").setAttribute("stroke", "#444444");
              document.getElementById(id).querySelector("polygon").setAttribute("stroke-width", "1");
              document.getElementById(id).querySelector("polygon").setAttribute("stroke-opacity", "0.5");
              document.getElementById(id).querySelector("polygon").setAttribute("stroke", "#444444");
          }
          // reset text highlight
          pkgs = document.getElementsByClassName("node");
          for (index2 = 0, len2 = pkgs.length; index2 < len2; ++index2) {
              target_id = pkgs[index2].id;
              document.getElementById(target_id).querySelector("text").setAttribute("font-weight", "normal");
          }

          // highlight deps
          var nodes = document.getElementsByClassName("edge");
          for (index = 0, len = nodes.length; index < len; ++index) {
            var title = nodes[index].querySelector("title").textContent.split("->");

            if (title[0] == text) {
              id = nodes[index].id;
              //console.log("ID:   " + id);
              document.getElementById(id).querySelector("path").setAttribute("stroke-width", "3");
              document.getElementById(id).querySelector("path").setAttribute("stroke-opacity", "1");
              document.getElementById(id).querySelector("path").setAttribute("stroke", "#aa3333");
              document.getElementById(id).querySelector("polygon").setAttribute("stroke-width", "5");
              document.getElementById(id).querySelector("polygon").setAttribute("stroke-opacity", "1");
              document.getElementById(id).querySelector("polygon").setAttribute("stroke", "#aa3333");

            }
            if (title[1] == text) {
              id = nodes[index].id;
              document.getElementById(id).querySelector("path").setAttribute("stroke-width", "3");
              document.getElementById(id).querySelector("path").setAttribute("stroke-opacity", "1");
              document.getElementById(id).querySelector("path").setAttribute("stroke", "#333377");
              document.getElementById(id).querySelector("polygon").setAttribute("stroke-width", "5");
              document.getElementById(id).querySelector("polygon").setAttribute("stroke-opacity", "1");
              document.getElementById(id).querySelector("polygon").setAttribute("stroke", "#333377");
            }

            if (title[0] == text || title[1] == text) {
              pkgs = document.getElementsByClassName("node");
              for (index2 = 0, len2 = pkgs.length; index2 < len2; ++index2) {
                var pkg_name = pkgs[index2].querySelector("title").textContent;
                if (pkg_name == title[0] || pkg_name == title[1]) {
                  target_id = pkgs[index2].id;
                  document.getElementById(target_id).querySelector("text").setAttribute("font-weight", "bold");
                }
              }
            }
          }


  }, false);

]]></script>
"""

    return svg.split("</svg>")[0] + javascript + "\n</svg>\n"



def main():

    # Usage:
    #
    # $ showme feora:30 graph
    # $ showme / graph

    parser = argparse.ArgumentParser()

    parser.add_argument("what", metavar="WHAT", help="What you want to see")
    parser.add_argument("how", metavar="HOW", choices=["graph", "directed-graph"], help="How you want to see it. Choose from 'graph' or 'directed-graph'")
    parser.add_argument("where", metavar="WHERE", help="Filename of the output")

    args = parser.parse_args()

    # Is it a container image or a path?
    if ":" in args.what:
        # A container image!
        packages = load_packages_from_container_image(args.what)
    else:
        # A file path!
        packages = load_packages_from_path(args.what)

    
    graph = compute_graph(packages)
    dot = graph_to_dot(graph)

    svg = dot_to_svg(dot)

    with open(args.where, "w") as output:
        output.write(svg)

    
    
    




    #base_pkgs = load_data("./container-base-packages.json")

    #base_pkgs = load_packages_from_container_image("fedora:30")
    #httpd_pkgs = load_data("./container-httpd-packages.json")

    #group = packages_to_group("<<fedora:30 base image>>", base_pkgs)

    #graph = compute_graph(httpd_pkgs, [group])
    #graph = compute_graph(base_pkgs)
    #dot = graph_to_dot(graph, sizes=True)

    #print(dot)

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







