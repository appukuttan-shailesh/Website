#!/bin/bash

# Copyright 2019 Ankur Sinha
# Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com> 
# File : 
#


for f in *.pdf
do
    echo "Processing $f"
    fname="$(basename $f .pdf)"
    convert -thumbnail x600 "$f"[0] "thumbnail-$fname.png"
done
