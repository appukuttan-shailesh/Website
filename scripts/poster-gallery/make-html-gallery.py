#!/usr/bin/env python3
"""
Generate the HTML code for the gallery.

File: make-html-gallery.py

Copyright 2019 Ankur Sinha
Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>


This must be run in the directory where all the PDF files are. They must be
named `P123.pdf` and so on. The directory should contain the thumbnails in the
`thumbnails` directory. They should be named `thumbnail-P123.png1`.
"""

from os import listdir
from os.path import isfile, join
from natsort import natsorted
from PIL import Image


# Number of columns in tables
num_columns = 2
max_thumbnail_width = 800
max_row_width = 1600
URL_p = "https://ocns.memberclicks.net/assets/CNS_Meetings/CNS2019/Posters/"
URL_t = URL_p + "thumbnails/"
filelist = [f for f in listdir(".") if isfile(join(".", f))]
sorted_list = natsorted(filelist)

# Print table headers
print("""
<table border="1" align="center">
<tbody>
<tr>
""")

counter = 0
row_width = 0
imgwidth = 0
for afile in sorted_list:
    # check thumbnail size. If it's landscape, only put two images on a line
    thumbnail = "thumbnail-" + afile.split(".")[0] + ".png"
    im = Image.open("./thumbnails/" + thumbnail)
    # They are all 800px in height
    thumbnail_width = im.size[0]
    row_width += thumbnail_width

    if thumbnail_width > max_thumbnail_width:
        colspan = 2
        imgwidth = 1200
    else:
        colspan = 1
        imgwidth = 600

    # New row starts
    if counter + colspan > num_columns or row_width > max_row_width:
        print("</tr><tr>")
        counter = 0
        row_width = 0

    # Member clicks does not support figure and figcaption tags.
    print("""
          <td colspan="{}" align="center">
          <a href="{}" target="_blank">
          <img title="{}" src="{}" alt="{}" width="{}">
          </a>
          <br />
          <strong>{}</strong>
          </td>
          """.format(colspan, URL_p + afile,
                     "Poster: " + afile,
                     URL_t + "thumbnail-" + afile.split(".")[0] + ".png",
                     "Poster: " + afile, imgwidth,
                     afile.split(".")[0]
                     )
          )

    counter += colspan
#

# End the table
print("""
</tr>
</tbody>
</table>
""")
