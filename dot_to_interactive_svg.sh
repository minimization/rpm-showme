#!/bin/sh

START=7; less <&0 | sfdp -Gstart=$START -Goverlap=prism | gvmap -e -d $START | neato -Gstart=$START -n -Ecolor="#44444455" -Tsvg | head -n -1
cat interactive_highlighter.js
echo "</svg>"
