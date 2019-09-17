#!/bin/bash

# Copyright 2019 Ankur Sinha
# Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com> 
# File : 
#


for i in *.pdf
do
    filename="$i"
    newfilename="$(echo $i | sed 's/\(P.*\) -.*pdf/\1.pdf/')"
    mv -v "$filename" "$newfilename"
done
