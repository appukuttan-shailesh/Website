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

year = 2022
fn = "ReceiptExport.csv"
active_members = "active.csv"
output_file = "candidates_{}.html".format(year)
template = """
<br/>
<table border="1" frame="above" id="{}" width="100%">
    <tbody>
        <tr valign="middle"  style="background : #eff8fd">
            <td style="border: 0px; width:125px"><img style="width: 100px; float: left; margin-right: 10px; margin-left: 10px;" src="{}" alt="Picture of {}" /></td>
            <td style="border: 0px; width:175px; margin-top: 0px; margin-right: 10px; margin-bottom: 5px; margin-left: 10px; padding-left: 10px; padding-top: 10px; outline-width: 0px; outline-style: initial; outline-color: initial;">
                <p><strong><a href="{}" target="_blank">{}</a></strong></p>
                <address>{}</address>
                <br/>
                <address>{}<br />{}, {}</address>
            </td>
            <td style="width:400px; border: 0px; margin-top: 0px; margin-right: 0px; margin-bottom: 5px; margin-left: 0px; outline-width: 0px; outline-style: initial; outline-color: initial; padding: 10px;">
                <p align="justify">{}</p>
            </td>
        </tr>
    </tbody>
</table>
<table border="1" frame="below" width="100%">
    <tbody>
        <tr>
            <td style="border: 0px; width: 10px; float: left; margin-right: 10px; margin-left: 10px;">&nbsp;</td>
            <td style="border: 0px; margin-top: 0px; margin-right: 0px; margin-bottom: 1px; margin-left: 0px; outline-width: 0px; outline-style: initial; outline-color: initial; padding: 0px;">
                <br/>
                <p><span style="font-weight:bold; font-size:18px; color:#495677;">Research Interests:</span><br/>{}</p>
                <p><span style="font-weight:bold; font-size:18px; color:#495677;">Past Experience:</span><br/>
                <i><span style="color:#495677">Describe your past contributions or participation in computational neuroscience.</span></i><br/>{}</p>
                <p><span style="font-weight:bold; font-size:18px; color:#495677;">Motivation:</span><br/>
                <i><span style="color:#495677">Please explain why you want to become an OCNS director.</span></i><br/>{}<br/><br/></p>
                <p>{}</p>
            </td>
        </tr>
        <tr><br/></tr>
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
            for key in ['[Member Type]', '[Address | Preferred | City]', '[Organization]', '[Address | Preferred | Country]']:
                candidates[name][key] = row[key].title()

for surname in ordered:

    row = candidates[surname]
    name = row['Name | First'] + " " + row['Name | Last']

    # SHOULD BE RETRIEVED FROM VALID MEMBERS
    if '[Address | Preferred | Country]' in row:
        addr1 = row['[Organization]']
        addr2 = row['[Address | Preferred | City]']
        addr3 = row['[Address | Preferred | Country]']
        memb = row['[Member Type]']
    else:
        print(surname, "is not a valid member: details should be manually provided")
        addr1 = ''
        addr2 = ''
        addr3 = ''
        memb = ''

    def check_unspecifed_set_default(val):
        if val == "":
            return "<i> - no info provided - </i>"
        return val
    
    introduction = check_unspecifed_set_default(row['Brief_Intro'])
    research = check_unspecifed_set_default(row['Research_Interests'])
    experience = check_unspecifed_set_default(row['Text']) # Past Experience
    motivation = check_unspecifed_set_default(row['Motivation'])

    cns_attend = row['Attend CNS']
    if cns_attend == 'none':
        cns_attend = '0'

    reviews = row['Review CNS']
    pc_or_lo = row['Member PC or LO']
    member_year = row['Member start']
    board_member = row['Member board']

    stats = "<span style='font-weight:bold; font-size:18px; color:#495677;'>OCNS and CNS participation:</span>"
    stats += "<p><strong># of CNS meetings attended: </strong>{}</p>".format(cns_attend)
    stats += "<p><strong>Review service for CNS meeting: </strong>{}</p>".format(reviews)
    stats += "<p><strong>Programme Committee / Local Organizing Committee member: </strong>{}</p>".format(pc_or_lo)
    stats += "<p><strong>Member of OCNS Board of Directors: </strong>{}</p>".format(board_member)
    stats += "<br/>"

    pic = "https://ocns.memberclicks.net/assets/images/Elections/{}/{}.jpg".format(year, row['Name | Last'])
    url = row['URL']

    body += template.format(name, pic, name, url, name, memb, addr1, addr2, addr3,
                            introduction, research, experience, motivation, stats)

with open(output_file, "w") as outfile:
    outfile.write(body)
