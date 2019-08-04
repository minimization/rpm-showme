# dependency-visualiser

Dependency visualisation of an RPM-based installation (a system, an image, etc.)

## Usage

Just tell the script what you what to show, how you want to see it, and where you want to save it. Like this:

```
$ ./showme WHAT HOW WHERE
```

So, for example:

```
$ ./showme fedora:30 graph output.svg --sizes
```

... produces a graph of all packages in the fedora:30 container image including sizes of all individual packages and some basic clustering. Clicking on a package highlights its relations to other packages.

![Fedora 30 container image graph](https://asamalik.fedorapeople.org/showme/fedora-base-image.jpg)

See the original [Fedora 30 container image graph](https://asamalik.fedorapeople.org/showme/fedora-base-image.svg) and try interacting with it!

### Grouping packages

Graphs can be simplified by merging multiple nodes (packages) into a single node (group). This is useful, for example, when visualizing an *httpd* installation on top of the Fedora base container image.

Example:

```
$ ./showme asamalik/fedora-httpd:f30 graph test.svg --sizes --group-container "Fedora 30 Base Image" fedora:30
```

![httpd on top of the Fedora base image graph](https://asamalik.fedorapeople.org/showme/httpd-simplified.jpg)

See the original [httpd on top of the Fedora base image graph](https://asamalik.fedorapeople.org/showme/httpd-simplified.svg).

### Directed graph

The above example might be better shown as a directed graph:

```
$ ./showme asamalik/fedora-httpd:f30 directed-graph test.svg --sizes --group-container "Fedora 30 Base Image" fedora:30
```

![directed graph of httpd](https://asamalik.fedorapeople.org/showme/httpd-directed-graph.jpg)

See the original [directed graph of httpd](https://asamalik.fedorapeople.org/showme/httpd-directed-graph.jpg). Again, it's interactive!

## Installation

The script has been tested on Fedora 30.

Dependencies:

```
$ sudo dnf install graphviz podman
```
