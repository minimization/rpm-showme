#!/usr/bin/python3


# Use it as:
#   ./dot-to-graph input.dot output.svg
#
# On Fedora, these are the dependencies you need:
# $ sudo dnf install graphviz 
#
# Enjoy!
#
#
# Copyright (c) 2021 Adam Samalik <asamalik@redhat.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 
# 

import dnf, json, subprocess, tempfile, argparse

def _add_javascript_to_svg(svg):
    javascript = """
<script type="text/javascript"><![CDATA[

document.addEventListener('click', function(e) {
      e = e || window.event;
      var target = e.target || e.srcElement;
      text = target.parentElement.querySelector("title").textContent;

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


def dot_to_graph_svg(dot):

    stage1 = subprocess.check_output(["sfdp", "-Gstart=3", "-Goverlap=prism"], input=dot, encoding="UTF-8")

    stage2 = subprocess.check_output(["gvmap", "-e", "-d", "3"], input=stage1, encoding="UTF-8")

    stage3 = subprocess.check_output(["neato", "-Gstart=3", "-n", "-Ecolor=#44444455", "-Tsvg"], input=stage2, encoding="UTF-8")

    svg = str(stage3)

    return _add_javascript_to_svg(svg)



def main():

    parser = argparse.ArgumentParser(description="Makes a pretty interactive output out of a dot file. Run it as './dot-to-graph input.dot output.svg' and then open the output.svg in your web browser.", formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("dot_file", help="Path to the dot file to be used as an input.")
    parser.add_argument("output", help="Where to save the resulting SVG file.")

    args = parser.parse_args()


    with open(args.dot_file, "r") as infile:
        input = infile.read()
        svg = dot_to_graph_svg(input)

    with open(args.output, "w") as outfile:
        outfile.write(svg)


if __name__ == "__main__":
    main()