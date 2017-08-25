# -*- coding: utf-8 -*-
import csv
import sys
import time

inactive_csv       = 'inactive.csv'   #  Add to regs..
clean_inactive_csv = 'inactive_upgraded.csv'

import datetime
now = datetime.datetime.now()


with open(inactive_csv, 'rb') as csvfile:
    
    reader      = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    output_file = open(clean_inactive_csv, 'w')
    writer      = csv.DictWriter(output_file, fieldnames=reader.fieldnames, delimiter=',', quotechar='"')
    writer.writeheader()
    users       = []

    for row in reader:
        if row['Expiration'] != "12/31/%s" %(now.year - 1):
            print row['Contact Name'], row['Expiration']
        row['Expiration'] = '12/31/%s' %now.year
        writer.writerow(row)

    output_file.close()