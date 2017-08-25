fn = "ReceiptExport.csv"

    
import csv

a={}
a["Hermann Cuntz"] = ["", "ESI and FIAS	", "Frankfurt/Main", "Germany", "Faculty Member"]
a["Nicolas Rougier"] = ["", "INRIA", "Talence", "France", "Faculty Member"]
a["Martin Zapotocky"] = ["", "Institute of Physiology of the Czech Academy of Sciences", "Prague", "Czech Republic", "Faculty Member"]
a["Maurizio DePitta'"] = ["", "The University of Chicago", "Chicago", "United States", "Postdoc Member"]
a["Taro Toyoizumi"] = ["", "RIKEN Brain Science Institute", "Saitama", "Japan", "Faculty Memberr"]
a["Masanori Shimono"] = ["", "Osaka University", "Osaka", "Japan", "Faculty Member"]
a["Leonid Rubchinsky"] = ["", "Indiana University - Purdue University", "Indianapolis", "United States", "Faculty Member"]
a["Jeehyun Kwag"] = ["", "Korea University", "Seoul", "Korea", "Faculty Member"]
a["Daniel Coca"] = ["", "University of Sheffield", "Sheffield", "United Kingdom", "Faculty Member"]
a["Joanna Jedrzejewska-Szmek"] = ["", "The Krasnow Institure for Advanced Study", "Fairfax", "United States", "Postdoc Member"]

template = """

<table border="3" frame="above">
    <tbody>
        <tr valign="middle">
            <td style="border: 0px;"><img style="width: 100px; float: left; margin-right: 10px; margin-left: 10px;" src="%s" alt="" /></td>
            <td style="border: 0px; width: 200px; margin-top: 0px; margin-right: 0px; margin-bottom: 5px; margin-left: 10px; outline-width: 0px; outline-style: initial; outline-color: initial; font-size: 12px; line-height: 18px; padding: 0px;">
                <p><strong>&nbsp;</strong></p>
                <p><strong>&nbsp;<a href="%s" target="_blank">%s</a></strong></p>
                <p><strong>&nbsp;%s</strong></p>
                <p>&nbsp;%s<br />&nbsp;%s<br />&nbsp;%s</p>
                <p><strong>&nbsp;</strong></p>
            </td>
            <td style="border: 0px; margin-top: 0px; margin-right: 0px; margin-bottom: 5px; margin-left: 0px; outline-width: 0px; outline-style: initial; outline-color: initial; font-size: 12px; line-height: 18px; padding: 0px;">
                <p>%s</p>
            </td>
        </tr>
    </tbody>
</table>
<table border="3" frame="below">
    <tbody>
        <tr>
            <td style="border: 0px; width: 10px; float: left; margin-right: 10px; margin-left: 10px;">&nbsp;</td>
            <td style="border: 0px; margin-top: 0px; margin-right: 0px; margin-bottom: 5px; margin-left: 0px; outline-width: 0px; outline-style: initial; outline-color: initial; font-size: 12px; line-height: 18px; padding: 0px;">
                <p><strong>Motivation:</strong>&nbsp;%s</p>
                <p>%s</p>
                <p>%s</p>
            </td>
        </tr>
    </tbody>
</table>
"""

t2='''-------------------------

%s

<p align=left><b>%s</b><br/>
%s&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br/>
%s<br/>
CNS %s</p>

%s

'''

out = open("cand2016.html", "w")
out2 = open("g33.txt", "w")

body = ""
b2=""

with open(fn, 'rb') as csvfile:
    r = csv.reader(csvfile, delimiter=',', quotechar='"')
    v = []
    
    ordered = []
    for n in a.keys():
        ordered.append(n.split(' ')[1])
    ordered.sort()
    
    print ordered
    
    all = {}
    
    for v in r:
     
        if v[0]!="Receipt ID":

            name = v[6]
            
            all[name] = v
            
    print all.keys()
            
    for surname in ordered:
        
            v = all[surname]
            name = v[4]+" "+v[6]

            print name
            
            addr1 =  a[name][1]
            addr2 =  a[name][2]
            addr3 =  a[name][3]
            memb =   a[name][4]
            
            info = v[9]
            
            print info
            
            mot = v[10]
            
            print mot
            
            oth = v[16]
            if len(oth)>1:
                oth = '<strong>Other information:</strong>&nbsp;%s'%oth

            print oth
            
            stars = a[name][0]
            
            att = v[11]
            if att=='none':
                att = '0'
            
            rev = v[12]
            rev = ", was reviewer for %s meetings"%v[12] if v[12] != "none" else ""
            
            year = v[15]
            
            particip = "<strong>OCNS and CNS participation%s:</strong> attended %s CNS meeting(s)%s. OCNS member since %s."%(stars, att, rev, year)
            
            print particip
            
            pic = v[7]
            
            
            print pic
            
            url = v[8]

            print url
            
            body += template%(pic, url, name, memb, addr1, addr2, addr3, info, mot, particip, oth)
            
            b2 +=t2%(name, name, memb, addr3, stars, pic)
            
            print "-------------"
            
out.write(body)
out.close()
out2.write(b2)
out2.close()

print b2