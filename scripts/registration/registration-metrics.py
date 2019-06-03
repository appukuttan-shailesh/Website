#!/usr/bin/env python3
"""
Generate registration metrics from Memberclicks data.

To make the data easier to query, we first import it into a simple sqlite
database. Please use the following commands to do so. The table names are
important, since we need them to run the queries from python here.

When importing the receipts tables, please drop the uneeded information such as
the receipt id and so on. These cause errors in the import.

$ sqlite3
> .open database.db
> .separator ","
> .import <registration profiles csv> registration_profiles
> .import <registration receipts csv> registration_profiles
> .import <extras receipts> registration_extras
> .import <extras events recipts> registration_extra_events

If imported correctly the .tables command would return this:

> .tables
registration_extra_events  registration_profiles
registration_extras        registration_receipts


File: registration-metrics.py

Copyright 2019 Ankur Sinha
Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>
"""


import sys
import sqlite3


class Metrics():

    """Generate metrics for the yearly CNS conference"""

    def __init__(self):
        """Initialise"""
        self.common_data = '"Email"'
        self.metrics_fn = "Registration-metrics.txt"

    def __connect_to_db(self, db_name):
        """Connect to sqlite3 database

        :db_name: name of sqlite database
        :returns: nothing

        """
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()

    def generate_metrics(self, db_name):
        """Generate metrics using sqlite3 database.

        :db_name: name of database file
        :returns: nothing

        """
        self.metrics_fh = open(self.metrics_fn, 'w')
        self.__connect_to_db(db_name)
        #  self.__get_registrant_metrics()
        #  self.__get_banquet_information()
        self.__get_t_shirt_requests()

        self.metrics_fh.close()

    def __get_registrant_metrics(self):
        """Get registration metrics.

        :conn: data base connection self.cursor object
        :returns: nothing

        """
        print("** Registrants information **", file=self.metrics_fh)
        print(file=self.metrics_fh)

        groups = ['Postdoc Member', 'Student Member', 'Faculty Member',
                  "OCNS Board", "OCNS Member Approval", "Basic Contact"]
        total_count = 0
        for group in groups:
            group_count = 0
            query = ('SELECT {} from registration_profiles where "Group" == "{}" ORDER BY "Email"'.format(self.common_data, group))
            with open("Registrants-from-profiles-{}.txt".format(group), 'w') as fh:
                for row in self.cur.execute(query):
                    print(row, file=fh)
                    total_count += 1
                    group_count += 1
            print("{}: {}".format(group, group_count), file=self.metrics_fh)
        print("Total: {}".format(total_count), file=self.metrics_fh)

        # For basic contacts, the recipts contain the group information. These
        # are not groups on Memberclicks. They are groups in the registration
        # form to implement the pricing structure.
        groups = ['Student', 'Faculty', 'Postdoc']
        for group in groups:
            query = ('SELECT {} from registration_receipts where "Registration Type" == "{}" ORDER BY "Email"'.format(self.common_data, group))
            with open("Registrants-from-receipts-{}.txt".format(group), 'w') as fh:
                for row in self.cur.execute(query):
                    print(row, file=fh)
        query = ('SELECT {} from registration_receipts where "Registration Type" == "" ORDER BY "Email"'.format(self.common_data))
        with open("Registrants-from-receipts-members.txt".format(group), 'w') as fh:
            for row in self.cur.execute(query):
                print(row, file=fh)

        print("** Gender breakdown **", file=self.metrics_fh)
        genders = ['M', 'F', 'Prefer not to say']
        for gender in genders:
            query = ('SELECT COUNT (*) from registration_profiles WHERE "Gender" == "{}"'.format(gender))
            self.cur.execute(query)
            print("- {}: {}".format(gender, self.cur.fetchone()[0]),
                  file=self.metrics_fh)

    def __get_banquet_information(self):
        """Get information for the banquet

        :returns: nothing

        """
        total_banquet_tickts = 0
        banquet_list = open("Banquet-registrants.txt", 'w')
        for row in self.cur.execute('SELECT  "Email", "BanquetTickets", "Special Meal" from registration_receipts where not "BanquetTickets" == "0" and not "BanquetTickets" == "None"'):
            if row:
                print("{}".format(row), file=banquet_list)
                total_banquet_tickts += int(row[1])
        for row in self.cur.execute('SELECT  "Email", "ExtraBanquetTickets", "Special Meal" from registration_receipts where not "ExtraBanquetTickets" == "0" and not "ExtraBanquetTickets" == "None"'):
            if row:
                print("{}".format(row), file=banquet_list)
                total_banquet_tickts += int(row[1])
        for row in self.cur.execute('SELECT "Email", "BanquetTickets", "Special Meal" from registration_extras where not "BanquetTickets" == "0" and not "BanquetTickets" == "None"'):
            if row:
                print("{}".format(row), file=banquet_list)
                total_banquet_tickts += int(row[1])
        for row in self.cur.execute('SELECT "Email", "ExtraBanquetTickets", "Special Meal" from registration_extras where not "ExtraBanquetTickets" == "0" and not "ExtraBanquetTickets" == "None"'):
            if row:
                print("{}".format(row), file=banquet_list)
                total_banquet_tickts += int(row[1])
        banquet_list.close()

        print("Total banquet tickets requested: {}".format(total_banquet_tickts), file=self.metrics_fh)

        # Special diets
        special_meal_list = open("Banquet-special-meal-list.txt", 'w')
        for row in self.cur.execute('SELECT "Email", "Special Meal" from registration_receipts where not "Special Meal" == "None"'):
            print("{}".format(row), file=special_meal_list)
        for row in self.cur.execute('SELECT "Email", "Special Meal" from registration_extras where not "Special Meal" == "None"'):
            print("{}".format(row), file=special_meal_list)


    def __get_t_shirt_requests(self):
        """Extract t-shirt request data
        :returns: TODO

        """
        print(file=self.metrics_fh)
        sizes = ['Shirt S', 'Shirt M', 'Shirt L', 'Shirt XL']
        t_shirt_list = open("T-shirt-list.txt", 'w')
        for asize in sizes:
            counter = 0
            print("\n** {} **".format(asize), file=t_shirt_list)
            for row in self.cur.execute('SELECT "Email", "{}" from registration_receipts where not "{}" == "0"'.format(asize, asize)):
                data = row
                if data is not None:
                    print("{}".format(data), file=t_shirt_list)
                    counter += int(data[-1])
            # Also check the extras
            for row in self.cur.execute('SELECT "Email", "{}" from registration_extras where not "{}" == "0"'.format(asize, asize)):
                data = row
                if data is not None:
                    print("{}".format(data), file=t_shirt_list)
                    counter += int(data[-1])
            print("** Total {}: {} **".format(asize, counter), file=t_shirt_list)

        t_shirt_list.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("sqite database name is required.")
        sys.exit(-1)
    else:
        new_gen = Metrics()
        new_gen.generate_metrics(sys.argv[1])
