#!/usr/bin/python3
"""
Generate the HTML page for director candidates.

The inputs this script requires are:
- export of director candidate form
- export of "active members"

Please ensure that the names of the exported files match the names set in this
script below.
"""

import csv

year = 2021
fn = "ReceiptExport.csv"
active_members = "active.csv"
output_file = "candidates_{}.html".format(year)
template = """
<br/>
<table border="1" frame="above" id="{}">
    <tbody>
        <tr valign="middle"  style="background : #eff8fd">
            <td style="border: 0px; width:125px"><img style="width: 100px; float: left; margin-right: 10px; margin-left: 10px;" src="{}" alt="Picture of {}" /></td>
            <td style="border: 0px; width:175px; margin-top: 0px; margin-right: 10px; margin-bottom: 5px; margin-left: 10px; padding-left: 10px; padding-top: 10px; outline-width: 0px; outline-style: initial; outline-color: initial; line-height: 18px;">
                <p><strong><a href="{}" target="_blank">{}</a></strong></p>
                <address>{}</address>
                <address>{}<br />{}<br />{}</address>
            </td>
            <td style="width:400px; border: 0px; margin-top: 0px; margin-right: 0px; margin-bottom: 5px; margin-left: 0px; outline-width: 0px; outline-style: initial; outline-color: initial; line-height: 18px; padding: 10px;">
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
                {}
            </td>
        </tr>
    </tbody>
</table>
<br/>
"""

body = ""
candidates = {}

with open(fn, 'r') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')

    for row in reader:
        candidates["{} {}".format(row['Name | Last'].title(), row['Name | First'].title())] = row

    ordered = []
    for n in list(candidates.keys()):
        ordered.append(n)
    ordered.sort()

with open(active_members, 'r') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')

    for row in reader:
        name = "{} {}".format(row['[Name | Last]'].title(), row['[Name | First]'].title())
        if name in candidates:
            for key in ['[Group]', '[Address | Preferred | City]', '[Organization]', '[Address | Preferred | Country]']:
                candidates[name][key] = row[key].title()

for surname in ordered:

    row = candidates[surname]
    name = row['Name | First'] + " " + row['Name | Last']

    # SHOULD BE RETRIEVED FROM VALID MEMBERS
    if '[Address | Preferred | Country]' in row:
        addr1 = row['[Organization]']
        addr2 = row['[Address | Preferred | City]']
        addr3 = row['[Address | Preferred | Country]']
        memb = row['[Group]']
    else:
        print(surname, "is not a valid member: details should be manually provided")
        addr1 = ''
        addr2 = ''
        addr3 = ''
        memb = ''

    info = row['Biography']
    mot = row['Motivation']
    oth = row['Other activities']
    if len(oth) > 1 and oth != "Please mention any other contributions you have made/are making to the computational neuroscience community (400 characters maximum, extra text will be removed).":
        oth = '<p><h2>Other information:</h2>{}</p>'.format(oth)
    else:
        oth = ""

    att = row['Attend CNS']
    if att == 'none':
        att = '0'

    rev = "<strong>Programme Committee/Local Organizing Committee member:</strong> {} ".format("Yes (" + row['Member PC or LO'] + ")" if row['Member PC or LO'] != "never" else "No")

    member_year = row['Member start']

    particip = "<h2>OCNS and CNS participation:</h2><p><strong># of CNS meetings attended: </strong>{}</p><p>{}</p><p><strong>OCNS member since:</strong> {}</p>".format(att, rev, member_year)

    pic = "https://ocns.memberclicks.net/assets/images/Elections/{}/{}.jpg".format(year, row['Name | Last'])
    url = row['URL']

    body += template.format(name, pic, name, url, name, memb, addr1, addr2, addr3,
                            info, mot, particip, oth)

with open(output_file, "w") as outfile:
    outfile.write(body)
