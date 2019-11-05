#!/usr/bin/python3
"""
Generate the HTML page for director candidates.

The inputs this script requires are:
- export of director candidate form
- export of "active members"
- export of "inactive members"

Please ensure that the names of the exported files match the names set in this
script below.
"""

import csv

year = 2019
fn = "ReceiptExport.csv"
active_members = "active.csv"
inactive_members = "inactive.csv"
output_file = "candidates_{}.html".format(year)
template = """

<table border="1" frame="above" id="{}">
    <tbody>
        <tr valign="middle"  style="background : #eff8fd">
            <td style="border: 0px; width:100px"><img style="width: 100px; float: left; margin-right: 10px; margin-left: 10px;" src="{}" alt="" /></td>
            <td style="border: 0px; width:200px; margin-top: 0px; margin-right: 10px; margin-bottom: 5px; margin-left: 10px; outline-width: 0px; outline-style: initial; outline-color: initial; line-height: 18px; padding: 0px;">
                <p><strong><a href="{}" target="_blank">{}</a></strong></p>
                <address>{}</address>
                <address>{}<br />{}<br />{}</address>
            </td>
            <td style="width:400px; border: 0px; margin-top: 0px; margin-right: 0px; margin-bottom: 5px; margin-left: 0px; outline-width: 0px; outline-style: initial; outline-color: initial; line-height: 18px; padding: 0px;">
                <p>{}</p>
            </td>
        </tr>
    </tbody>
</table>
<table border="1" frame="below">
    <tbody>
        <tr>
            <td style="border: 0px; width: 10px; float: left; margin-right: 10px; margin-left: 10px;">&nbsp;</td>
            <td style="border: 0px; margin-top: 0px; margin-right: 0px; margin-bottom: 1px; margin-left: 0px; outline-width: 0px; outline-style: initial; outline-color: initial; line-height: 18px; padding: 0px;">
                <p><h2>Motivation:</h2>{}</p>
                <p>{}</p>
                <p>{}</p>
            </td>
        </tr>
    </tbody>
</table>
"""

out = open(output_file, "w")
body = ""
candidates = {}

with open(fn, 'r') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')

    for row in reader:
        candidates["{} {}".format(row['Last Name'].title(), row['First Name'].title())] = row

    ordered = []
    for n in list(candidates.keys()):
        ordered.append(n)
    ordered.sort()

with open(active_members, 'r') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')

    for row in reader:
        name = "{} {}".format(row['Last Name'].title(), row['First Name'].title())
        if name in candidates:
            for key in ['Group', 'City', 'Institution', 'Country']:
                candidates[name][key] = row[key].title()

with open(inactive_members, 'r') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')

    for row in reader:
        name = "{} {}".format(
            row['Last Name'].title(), row['First Name'].title())

        if name in candidates:
            for key in ['Group', 'City', 'Institution', 'Country']:
                candidates[name][key] = row[key].title()

for surname in ordered:

    row = candidates[surname]
    name = row['First Name'] + " " + row['Last Name']

    # SHOULD BE RETRIEVED FROM VALID MEMBERS
    if 'Country' in row:
        addr1 = row['Institution']
        addr2 = row['City']
        addr3 = row['Country']
        memb = row['Group']
    else:
        print(surname, "is not a valid member: details should be manually provided")
        addr1 = ''
        addr2 = ''
        addr3 = ''
        memb = ''

    info = row['Biography']
    mot = row['Motivation']
    oth = row['Other activities']
    if len(oth) > 1:
        oth = '<h2>Other information:</h2>{}'.format(oth)

    att = row['Attend CNS']
    if att == 'none':
        att = '0'

    rev = ", was reviewer for {} meetings".format(
        row['Review CNS'] if row['Review CNS'] != "none" else "")

    year = row['Member start']

    particip = "<h2>OCNS and CNS participation:</h2>Attended {} CNS meeting(s){}. OCNS member since {}.".format(att, rev, year)

    pic = row['File Attachment']
    url = row['URL']

    body += template.format(name, pic, url, name, memb, addr1, addr2, addr3,
                            info, mot, particip, oth)

out.write(body)
out.close()
