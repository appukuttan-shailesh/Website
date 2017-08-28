# -*- coding: utf-8 -*-
import csv
import sys
import time



active_csv          = 'active_clean.csv'   #  All reciepts exported, e.g. Export-OCNS-Receipts-475-25-Jun-2015-05-35-34.csv
inactive_csv        = 'inactive_clean.csv'   #  Add to regs..
update_inactive_csv = 'inactive_update.csv'
update_active_csv   = 'active_update.csv'
sutdent_threshold   = 5
postdoc_threshold   = 5
to_write            = ['Username', 'Elapsed Time', 'Email', 'First Name', 'Last Name', 'Gender', 'Salutation', 'Group']

need_to_be_updated = {'Student' : 0, 'Postdoc' : 0}

with open(inactive_csv, 'rb') as csvfile:
    
    reader      = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    output_file = open(update_inactive_csv, 'w')
    writer      = csv.DictWriter(output_file, fieldnames=to_write, delimiter=',', quotechar='"')
    writer.writeheader()
    users       = []

    for row in reader:

        member_type = row['Group'].replace(' Member', '') 
        date = time.strptime(row['Created On Date'], '%m/%d/%Y %H:%M:%S')
        to_update = False
    
        time_diff = time.localtime().tm_year - date.tm_year

        if member_type == 'Student' and (time_diff >= sutdent_threshold):
            to_update = True
            need_to_be_updated['Student'] += 1
        elif member_type == 'Postdoc' and (time_diff >= postdoc_threshold):
            to_update = True
            need_to_be_updated['Postdoc'] += 1

        if to_update:
            data = {}
            for item in to_write:
                if item != 'Elapsed Time':
                    data[item] = row[item]

            data['Elapsed Time'] = time_diff

            writer.writerow(data)

    output_file.close()
    print need_to_be_updated

with open(active_csv, 'rb') as csvfile:
    
    reader      = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    output_file = open(update_active_csv, 'w')
    writer      = csv.DictWriter(output_file, fieldnames=to_write, delimiter=',', quotechar='"')
    writer.writeheader()
    users       = []

    for row in reader:

        member_type = row['Group'].replace(' Member', '') 
        date = time.strptime(row['Created On Date'], '%m/%d/%Y %H:%M:%S')
        to_update = False
    
        time_diff = time.localtime().tm_year - date.tm_year

        if member_type == 'Student' and (time_diff > sutdent_threshold):
            to_update = True
            need_to_be_updated['Student'] += 1
        elif member_type == 'Postdoc' and (time_diff > postdoc_threshold):
            to_update = True
            need_to_be_updated['Postdoc'] += 1

        if to_update:
            data = {}
            for item in to_write:
                if item != 'Elapsed Time':
                    data[item] = row[item]

            data['Elapsed Time'] = time_diff

            writer.writerow(data)

    output_file.close()
    print need_to_be_updated



"""
Dear user

You registered as a %s Member for the OCNS organization. We would like to remind you that you should notify us if your status has been updated (Student, PostDoc, Faculty). 

Note that OCNS is a non-profit organization, and 
