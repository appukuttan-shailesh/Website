# -*- coding: utf-8 -*-
import csv
import sys
import time



active_csv         = 'active.csv'   #  All reciepts exported, e.g. Export-OCNS-Receipts-475-25-Jun-2015-05-35-34.csv
inactive_csv       = 'inactive.csv'   #  Add to regs..
clean_inactive_csv = 'inactive_clean.csv'
clean_active_csv   = 'active_clean.csv'
duplicate_thresh   = 1.5

def suggest_duplicates(all_rows, criteria=duplicate_thresh):
    from difflib import SequenceMatcher
    duplicates = []
    print "Looking for duplicates..."

    for count, user in enumerate(all_rows):
        ratios       = []
        contact_name = user['Contact Name'].strip().title()
        email        = user['Email'].strip()
        for user in all_rows[count+1:]:
            ratio_1 = SequenceMatcher(None, email, user['Email']).ratio()
            ratio_2 = SequenceMatcher(None, contact_name, user['Contact Name']).ratio()
            ratio   =  ratio_1 + ratio_2
            if ratio > criteria and ratio < 2:
                ratios += [user]

        if len(ratios) > 0:
            print "User %s may be duplicated with: %s" %(contact_name, [user['Contact Name'] for user in ratios])
            duplicates += [contact_name]

    return duplicates


with open(inactive_csv, 'rb') as csvfile:
    
    reader      = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    output_file = open(clean_inactive_csv, 'w')
    writer      = csv.DictWriter(output_file, fieldnames=reader.fieldnames, delimiter=',', quotechar='"')
    writer.writeheader()
    users       = []

    for row in reader:
        for field in reader.fieldnames:
            row[field] = row[field].replace("¿", "")
            row[field] = row[field].replace("â", "")
            row[field] = row[field].replace("é", "")
            row[field] = row[field].replace("®", "é")
            row[field] = row[field].replace("Ã¶", "ö")
            row[field] = row[field].replace('©', "")
            row[field] = row[field].replace('ñ', "ä")
            row[field] = row[field].replace('í', "i")


            if field == 'Contact Name':
                row[field] = row[field].title()

        writer.writerow(row)
        users += [row]

    output_file.close()

    duplicates = suggest_duplicates(users)
    f = open('inactive_duplicates.txt', 'w')
    for user in duplicates:
        f.write('%s\n' %user)
    f.close()


with open(active_csv, 'rb') as csvfile:
    
    reader      = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    output_file = open(clean_active_csv, 'w')
    writer      = csv.DictWriter(output_file, fieldnames=reader.fieldnames, delimiter=',', quotechar='"')
    writer.writeheader()
    users       = []

    for row in reader:
        for field in reader.fieldnames:
            row[field] = row[field].replace("¿", "")
            row[field] = row[field].replace("â", "")
            row[field] = row[field].replace("é", "")
            row[field] = row[field].replace("®", "é")
            row[field] = row[field].replace("Ã¶", "ö")
            row[field] = row[field].replace('©', "")
            row[field] = row[field].replace('ñ', "ä")
            row[field] = row[field].replace('í', "i")


            if field == 'Contact Name':
                row[field] = row[field].title()

        writer.writerow(row)
        users += [row]

    output_file.close()

    duplicates = suggest_duplicates(users)
    f = open('active_duplicates.txt', 'w')
    for user in duplicates:
        f.write('%s\n' %user)
    f.close()
