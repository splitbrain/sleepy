#!/bin/bash

for X in *.svg; do
    BASE=`basename $X .svg`
    convert -background none -density 200 $X -negate -resize 48x48 ../${BASE}.png
done
