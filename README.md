# rpm-showme

Dependency visualisation of an RPM-based installation (a system, an image, etc.)

## Usage

The script requires the following dependencies on your system:

```
$ sudo dnf install graphviz podman python3-jinja2
```

Just tell the script what you what to show, how you want to see it, and where you want to save it. Like this:

```
$ ./rpm-showme WHAT HOW WHERE
```

### Looking at container images

To look at the Fedora 30 container base image, run:

```
$ ./rpm-showme fedora:30 graph output.svg --sizes
```

... which produces a graph of all packages in the fedora:30 container image including sizes of all individual packages and some basic clustering. Clicking on a package highlights its relations to other packages.

![Fedora 30 container image graph](https://asamalik.fedorapeople.org/showme/fedora-base-image-min.jpg)

See the original [Fedora 30 container image graph](https://asamalik.fedorapeople.org/showme/fedora-base-image.svg) and try interacting with it!


### Looking at file paths

To look at your own Fedora system, run:

```
$ ./rpm-showme / graph output.svg
```

You can also look at an arbitrary DNF installation:

```
$ mkdir /tmp/cowsay
$ sudo dnf --installroot /tmp/cowsay --releasever 30 install cowsay
$ ./rpm-showme ./ graph output.svg
```

### Grouping packages

Graphs can be simplified by merging multiple nodes (packages) into a single node (group). This is useful, for example, when visualizing an *httpd* installation on top of the Fedora base container image.

Example:

```
$ ./rpm-showme asamalik/fedora-httpd:f30 graph test.svg --sizes --group-container "Fedora 30 Base Image" fedora:30
```

![httpd on top of the Fedora base image graph](https://asamalik.fedorapeople.org/showme/httpd-simplified-min.jpg)

See the original [httpd on top of the Fedora base image graph](https://asamalik.fedorapeople.org/showme/httpd-simplified.svg).

### Directed graph

The above example might be better shown as a directed graph:

```
$ ./rpm-showme asamalik/fedora-httpd:f30 directed-graph test.svg --sizes --group-container "Fedora 30 Base Image" fedora:30
```

![directed graph of httpd](https://asamalik.fedorapeople.org/showme/httpd-directed-graph-min.jpg)

See the original [directed graph of httpd](https://asamalik.fedorapeople.org/showme/httpd-directed-graph.svg). Again, it's interactive!

### List

A simple list of packages in the standard output:

```
$ ./rpm-showme fedora:30 list
acl
alternatives
audit-libs
basesystem
bash
...
```

### Size

Just print out the total size of all packages:

```
$ ./rpm-showme fedora:30 size
274.2 MB
```

### Report

An HTML table comparing multiple installations:

```
$ ./rpm-showme fedora:30 report report.html --name "Fedora 30 base image" --add "httpd" httpd:f30 
```

See the [report.html](https://asamalik.fedorapeople.org/showme/report.html) and [report-sizes.html](https://asamalik.fedorapeople.org/showme/report-sizes.html) generated with the `--sizes` option.



