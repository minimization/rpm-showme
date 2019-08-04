<script type="text/javascript"><![CDATA[

document.addEventListener('click', function(e) {
      e = e || window.event;
      var target = e.target || e.srcElement,
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
              document.getElementById(id).querySelector("path").setAttribute("stroke-width", "5");
              document.getElementById(id).querySelector("path").setAttribute("stroke-opacity", "1");
              document.getElementById(id).querySelector("path").setAttribute("stroke", "#aa3333");
              document.getElementById(id).querySelector("polygon").setAttribute("stroke-width", "5");
              document.getElementById(id).querySelector("polygon").setAttribute("stroke-opacity", "1");
              document.getElementById(id).querySelector("polygon").setAttribute("stroke", "#aa3333");

            }
            if (title[1] == text) {
              id = nodes[index].id;
              document.getElementById(id).querySelector("path").setAttribute("stroke-width", "5");
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
