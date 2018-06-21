# -*- coding: utf-8 -*-
import csv
import sys
import time
import os

from docx import Document
from docx.shared import Pt

document = Document()

from collections import OrderedDict

registered_email         = OrderedDict()
registered_fullname      = OrderedDict()
conf_year                = 2018
conf_place               = "Seattle, USA"
main_registrations_csv   = 'Main2018.csv'   #  All reciepts exported, e.g. Export-OCNS-Receipts-475-25-Jun-2015-05-35-34.csv
confmaster_file          = "confmaster.csv"
display                  = True

members = {'faculty' : 0,
           'postdoc' : 0,
           'student' : 0}

non_members = {'faculty' : 0,
               'postdoc' : 0,
               'student' : 0}

def find_best_user(row, registered_email):
    print('%s is not found in the main registration! Trying to auto guess...' %email)
    from difflib import SequenceMatcher
    best_ratio  = 0
    last_name   = row['Last Name'].strip().title()
    middle_name = row['Middle Name'].strip()
    first_name  = row['First Name'].strip().title()
    full_name   = '%s %s'%(last_name, first_name)

    for user in registered_email.keys():
        ratio_1 = SequenceMatcher(None, email, registered_email[user]['email']).ratio()
        ratio_2 = SequenceMatcher(None, full_name, registered_email[user]['full_name']).ratio()
        ratio   =  ratio_1 + ratio_2
        if ratio > best_ratio:
            best_user  = user
            best_ratio = ratio
    print('Best match found for %s is user %s' %(email, best_user))
    return best_user

with open(main_registrations_csv, 'rb') as csvfile:

    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')

    for count, row in enumerate(reader):
   
        user = {}
        user['email'] = row['Email']

        if display:
            print('Handling registration for %s'%user['email'])

        last_name     = row['Last Name'].strip().title()
        middle_name   = row['Middle Name'].strip()
        first_name    = row['First Name'].strip().title()
        user['name']  = ('<b>%s</b> %s %s'%(last_name, first_name, middle_name)).strip()
        user['full_name']   = '%s %s'%(last_name, first_name)
        user['first_name']  = '%s' %first_name
        user['middle_name'] = '%s' %middle_name
        user['last_name']   = '%s' %last_name
                
        date         = row['Submit Date']
        user['date'] = time.strptime(date, '%m/%d/%Y %H:%M:%S')

        reg_nm = row['Reg Fee (Non-Member)']
        reg_f  = row['Reg Fee (Faculty)']
        reg_p  = row['Reg Fee (Postdoc)']
        reg_s  = row['Reg Fee (Student)']
        reg_type = row['Registration Type']

        user['type'] = 'Non member' if len(reg_nm)>0 else ('Faculty' if len(reg_f)>0 else ('Postdoc' if len(reg_p)>0 else 'Student'))
        payment_info = reg_nm+reg_f+reg_p+reg_s

        if user['type'] in ['Faculty', 'Postdoc', 'Student']: 
            members[user['type'].lower()] +=1
        elif reg_type in ['Faculty', 'Postdoc', 'Student']:
            non_members[reg_type.lower()] += 1
        else:
            print('Problem at line %d with user %s %s %s'%(count, user['email'], user['type'], reg_type))
            print('Press f/p/s if you know Faculty/Postdoc/student, q to quit')
            key = ''
            while key not in ['f', 'p', 's', 'q']:
                key = raw_input('').lower()

            if key == "q":
                sys.exit()
            elif key == 's':
                non_members['student'] += 1
                reg_type = 'Student'
            elif key == 'f':
                non_members['faculty'] += 1
                reg_type = 'Faculty'
            elif key == 'p':
                non_members['postdoc'] += 1
                reg_type = 'Postdoc'

        user['type0'] = '%s %s'%(user['type'], reg_type if len(reg_type)>0 else 'Member')
        user['paid']  = ''

        registered_email[user['email']] = user
        registered_fullname[user['full_name']] = user


with open(confmaster_file, 'rb') as csvfile:

    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    output = open('poster_students.csv', 'w')

    for count, row in enumerate(reader):
        last_name     = row['ContactAuthor_LastName'].strip().title()
        first_name    = row['ContactAuthor_FirstName'].strip().title()
        email         = row['ContactAuthor_eMail']
        label         = row['Label']
        full_name    = '%s %s'%(last_name, first_name)
        if full_name in registered_fullname.keys():
            if registered_fullname[full_name]['type'] == 'Student':
                output.write('%s\t%s\t%s\t%s\n'%(first_name, last_name, email, label))
    output.close()

print('Processed %d Main Registrations' %len(registered_email))