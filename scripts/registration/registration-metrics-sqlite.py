#!/usr/bin/env python3
"""
Generate registration metrics from Memberclicks data.

To make the data easier to query, we first import it into a simple sqlite
database.

The following tables will be created

> .tables
add_extras             registration_master    registration_receipts
add_to_registration    registration_profiles

File: registration-metrics-sqlite.py

Copyright 2019 Ankur Sinha
Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>
"""


import sys
import sqlite3
import os
import textwrap
import subprocess


class Metrics():

    """Generate metrics for the yearly CNS conference"""

    def __init__(self):
        """Initialise"""
        self.common_data = '"Email"'
        self.metrics_fn = "Registration-metrics.txt"
        self.tabs = {
            "RegReceipts": "registration_receipts",
            "RegProfiles": "registration_profiles",
            "AddToRegs": "add_to_registration",
            "AddExtras": "add_extras",
            "Master": "registration_master"


        }
        self.db_name = "CNS2019.sqlite"

    def usage(self):
        """Print usage instructions
        :returns: nothing

        """
        print("Usage: {} db_name | raw_files".format(os.path.basename(__file__)), file=sys.stderr)
        print(file=sys.stderr)
        print(textwrap.dedent(
            """\
            If using the first form, the database must be populated using
            this script so that the table names match.
            """), file=sys.stderr)
        print(textwrap.dedent(
            """\
            If using the second form, the following 4 files musbe be
            provided in the right order:
            """), file=sys.stderr)

        print("1. Registration profile export csv", file=sys.stderr)
        print("2. Registration receipts export csv", file=sys.stderr)
        print("3. Add to registrations export csv", file=sys.stderr)
        print("4. Add extras csv", file=sys.stderr)

    def setup_new_db(self, filenames):
        """
        Import csv files into sqlite3 database.

        :filenames: list of files names
        :returns: TODO
        """
        if os.path.isfile(self.db_name):
            print("{} exists. Removing and re importing".format(self.db_name))
            subprocess.run(["rm", "-fv", self.db_name], check=True)

            self.__import_from_csv(filenames)
            self.__create_master_table()
            self.__populate_master_table()
            self.__add_extras()

    def __import_from_csv(self, filenames):
        """
        Import data from csv to the tables.
        :returns: nothing

        """
        print("Loading CSV data", file=sys.stderr)

        sqlite_init = textwrap.dedent(
            """\
            .open {}
            .mode csv
            .separator ,
            .import {} {}
            .import {} {}
            .import {} {}
            .import {} {}
            .quit \n

            """.format(
                self.db_name,
                filenames[1], self.tabs["RegProfiles"],
                filenames[2], self.tabs["RegReceipts"],
                filenames[3], self.tabs["AddToRegs"],
                filenames[4], self.tabs["AddExtras"],
            ))

        subprocess.run(["sqlite3"], input=sqlite_init, text=True, check=True)

    def __create_master_table(self):
        """
        Create the master table
        :returns: nothing

        """

        print("Creating master table", file=sys.stderr)

        sqlite_create_table = textwrap.dedent(
            """\
            CREATE TABLE {} (\
            "Email" TEXT PRIMARY KEY,\
            "First Name" TEXT,\
            "Middle Name" TEXT,\
            "Last Name" TEXT,\
            "Gender" TEXT,\
            "Institution" TEXT,\
            "Country" TEXT,\
            "OCNS Member" TEXT,\
            "Invitation Letter" TEXT,\
            "Registration Group" TEXT,\
            "Main meeting Registration" TEXT,\
            "Workshop Registration" TEXT,\
            "Tutorial Registration" TEXT,\
            "Banquet Tickets" INT,\
            "Special Meal" TEXT,\
            "Shirt S" INT,\
            "Shirt M" INT,\
            "Shirt L" INT,\
            "Shirt XL" INT,\
            "Payment Type" TEXT,\
            "Payment Total" REAL,\
            "Balance" REAL,\
            "Discount Code" TEXT\
            )
            """
        ).format(self.tabs["Master"])

        conn = self.__get_db_conn()
        cur = conn.cursor()
        cur.execute(sqlite_create_table)
        conn.commit()

    def __populate_master_table(self):
        """
        Parse data and populate the master table
        :returns: nothing

        """
        query = textwrap.dedent(
            """\
            SELECT * from {};

            """
        ).format(self.tabs["RegReceipts"])

        read_conn = self.__get_db_conn()
        read_cur = read_conn.cursor()
        write_conn = self.__get_db_conn()
        write_cur = write_conn.cursor()
        for row in read_cur.execute(query):
            #  print(row.keys())
            reg_grp = ""
            member = "N"
            reg_mm = "N"
            reg_tut = "N"
            reg_ws = "N"
            banquet_tickets = 0

            reg_nm = row["Reg Fee (Non-Member)"]
            reg_f = row["Reg Fee (Faculty)"]
            reg_p = row["Reg Fee (Postdoc)"]
            reg_s = row["Reg Fee (Student)"]
            reg_b = row["Reg Fee (Board)"]

            if len(reg_f) > 0:
                reg_grp = "Faculty"
                member = "Y"
            elif len(reg_p) > 0:
                reg_grp = "Postdoc"
                member = "Y"
            elif len(reg_s) > 0:
                reg_grp = "Student"
                member = "Y"
            elif len(reg_b) > 0:
                reg_grp = "Board"
                member = "Y"
            elif len(reg_nm) > 0:
                member = "N"
                reg_grp = row["Registration Type"]
            else:
                print("Registration type not found!", file=sys.stderr)

            registrations = (
                row["Reg Fee (Non-Member)"] +
                row["Reg Fee (Faculty)"] +
                row["Reg Fee (Postdoc)"] +
                row["Reg Fee (Student)"] +
                row["Reg Fee (Board)"]
            )

            # Not elif because they are not mutually exclusive here
            if 'Main Meeting' in registrations:
                reg_mm = "Y"
            if 'Tutorial' in registrations:
                reg_tut = "Y"
            if 'Workshops' in registrations:
                reg_ws = "Y"

            banquet_tickets = (
                int(row["BanquetTickets"]) +
                int(row["ExtraBanquetTickets"])
            )

            insert_query = textwrap.dedent(
                """\
                INSERT INTO {} (\
                "Email",\
                "First Name",\
                "Middle Name",\
                "Last Name",\
                "Gender",\
                "Institution",\
                "Country",\
                "OCNS Member",\
                "Registration Group",\
                "Invitation Letter",\
                "Main meeting Registration",\
                "Workshop Registration",\
                "Tutorial Registration",\
                "Banquet Tickets",\
                "Special Meal",\
                "Shirt S",\
                "Shirt M",\
                "Shirt L",\
                "Shirt XL",\
                "Payment Type",\
                "Payment Total",\
                "Balance",\
                "Discount Code"\
                )\
                VALUES (\
                "{}","{}","{}","{}","{}","{}","{}","{}",\
                "{}","{}","{}","{}","{}",{},"{}",{},\
                {},{},{},"{}",{},{},"{}"\
                )
                """
            ).format(
                self.tabs["Master"],
                row["Email"],
                row["First Name"],
                row["Middle Name"],
                row["Last Name"],
                row["Gender"],
                row["Institution"],
                row["Country"],
                member,
                reg_grp,
                row["Invitation Letter"],
                reg_mm,
                reg_ws,
                reg_tut,
                banquet_tickets,
                ("" if
                 (not row["Special Meal"] or row["Special Meal"] == "None")
                 else row["Special Meal"]),
                int(row["Shirt S"]),
                int(row["Shirt M"]),
                int(row["Shirt L"]),
                int(row["Shirt XL"]),
                row["Payment Type"],
                float(row["Payment Total"]),
                float(row["Balance"]),
                ("" if
                 (not row["Discount Code"] or row["Discount Code"] == "None")
                 else row["Discount Code"]),
            )
            #  print(insert_query)
            try:
                write_cur.execute(insert_query)
            except sqlite3.Error as e:
                print("ERROR: ", e.args[0], file=sys.stderr)
                print("Query was: ", insert_query, file=sys.stderr)

        write_conn.commit()
        write_conn.close()

    def __add_extras(self):
        """
        Add extra registrations, either workshops and tutorials that were added
        later, or banquet tickets and t-shirts

        :returns: nothing

        """
        print("Adding extras:")

        read_conn = self.__get_db_conn()
        read_cur = read_conn.cursor()
        read_conn_1 = self.__get_db_conn()
        read_cur_1 = read_conn_1.cursor()
        query = textwrap.dedent(
            """\
            SELECT * from {};

            """
        ).format(self.tabs["AddToRegs"])

        read_cur.execute(query)
        rows = read_cur.fetchall()
        for row in rows:
            new_reg_mm = "N"
            new_reg_ws = "N"
            new_reg_tut = "N"
            reg_mm = "N"
            reg_ws = "N"
            reg_tut = "N"
            registrations = (
                row["Reg Fee (Non-Member)"] +
                row["Reg Fee (Faculty)"] +
                row["Reg Fee (Postdoc)"] +
                row["Reg Fee (Student)"] +
                row["Reg Fee (Board)"]
            )
            payment = float(row["Payment Total"])

            # Not elif because they are not mutually exclusive here
            if 'Main Meeting' in registrations:
                reg_mm = "Y"
            if 'Workshops' in registrations:
                reg_ws = "Y"
            if 'Tutorial' in registrations:
                reg_tut = "Y"

            check_query = textwrap.dedent(
                """\
                SELECT * FROM {} WHERE "Email"=="{}"
                """
            ).format(self.tabs["Master"], row["Email"])
            # There should only be one entry, but let's check them all anyway.
            read_cur_1.execute(check_query)
            newrows = read_cur_1.fetchall()
            for newrow in newrows:
                initial_reg_mm = newrow["Main meeting Registration"]
                initial_reg_ws = newrow["Workshop Registration"]
                initial_reg_tut = newrow["Tutorial Registration"]
                initial_payment = newrow["Payment Total"]

                new_reg_mm = ("Y" if
                              (reg_mm == "Y" or initial_reg_mm == "Y")
                              else "N")
                new_reg_ws = ("Y" if
                              (reg_ws == "Y" or initial_reg_ws == "Y")
                              else "N")
                new_reg_tut = ("Y" if
                               (reg_tut == "Y" or initial_reg_tut == "Y")
                               else "N")
                new_payment = initial_payment + payment

            print("{}: {}{}{} + {}{}{} = {}{}{}".format(
                newrow["Email"], initial_reg_mm, initial_reg_ws,
                initial_reg_tut, reg_mm, reg_ws, reg_tut, new_reg_mm,
                new_reg_ws, new_reg_tut))

            update_query = textwrap.dedent(
                """\
                UPDATE {}\
                SET "Main meeting Registration" = "{}",\
                "Workshop Registration" = "{}",\
                "Tutorial Registration" = "{}",\
                "Payment Total" = "{}"\
                WHERE "Email"=="{}"
                """
            ).format(self.tabs["Master"], new_reg_mm, new_reg_ws, new_reg_tut,
                     new_payment, row["Email"])
            #  print(update_query)
            write_conn = self.__get_db_conn()
            write_cur = write_conn.cursor()
            write_cur.execute(update_query)
            write_conn.commit()
            write_conn.close()

        # banquet tickets and and t-shirts
        query = textwrap.dedent(
            """\
            SELECT * from {};

            """
        ).format(self.tabs["AddExtras"])

        read_cur.execute(query)
        rows = read_cur.fetchall()
        for row in rows:
            new_banquet_tickets = 0
            new_special_meal = ""
            banquet_tickets = int(row["BanquetTickets"])
            special_meal = ("" if (not row["Special Meal"] or
                                   row["Special Meal"] == "None")
                            else row["Special Meal"])
            extra_banquet_tickets = int(row["ExtraBanquetTickets"])
            payment = float(row["Payment Total"])

            new_t_s_s = 0
            new_t_s_m = 0
            new_t_s_l = 0
            new_t_s_xl = 0
            t_s_s = int(row["Shirt S"])
            t_s_m = int(row["Shirt M"])
            t_s_l = int(row["Shirt L"])
            t_s_xl = int(row["Shirt XL"])

            check_query = textwrap.dedent(
                """\
                SELECT * FROM {} WHERE "Email"=="{}"
                """
            ).format(self.tabs["Master"], row["Email"])

            # There should only be one entry, but let's check them all anyway.
            read_cur_1.execute(check_query)
            newrows = read_cur_1.fetchall()
            for newrow in newrows:
                initial_banquet_tickets = newrow["Banquet Tickets"]
                initial_special_meal = newrow["Special Meal"]
                initial_t_s_s = newrow["Shirt S"]
                initial_t_s_m = newrow["Shirt M"]
                initial_t_s_l = newrow["Shirt L"]
                initial_t_s_xl = newrow["Shirt XL"]
                initial_payment = newrow["Payment Total"]

                new_banquet_tickets = (initial_banquet_tickets +
                                       banquet_tickets + extra_banquet_tickets)
                new_special_meal = initial_special_meal + special_meal
                new_t_s_s = initial_t_s_s + t_s_s
                new_t_s_m = initial_t_s_m + t_s_m
                new_t_s_l = initial_t_s_l + t_s_l
                new_t_s_xl = initial_t_s_xl + t_s_xl
                new_payment = initial_payment + payment

            update_query = textwrap.dedent(
                """\
                UPDATE {}\
                SET "Banquet Tickets" = "{}",\
                "Special Meal" = "{}",\
                "Shirt S" = "{}",\
                "Shirt M" = "{}",\
                "Shirt L" = "{}",\
                "Shirt XL" = "{}",\
                "Payment Total" = "{}"\
                WHERE "Email"=="{}"
                """
            ).format(self.tabs["Master"], new_banquet_tickets,
                     new_special_meal, new_t_s_s, new_t_s_m, new_t_s_l,
                     new_t_s_xl, new_payment, row["Email"])
            #  print(update_query)
            write_conn = self.__get_db_conn()
            write_cur = write_conn.cursor()
            write_cur.execute(update_query)
            write_conn.commit()
            write_conn.close()

    def __get_db_conn(self, db_name=None):
        """Connect to sqlite3 database

        :db_name: name of sqlite database
        :returns: connection to the db

        """
        if not db_name:
            db_name = self.db_name
        conn = sqlite3.connect(db_name)
        conn.row_factory = sqlite3.Row

        return conn

    def generate_metrics(self):
        """Generate metrics.

        :returns: nothing
        """
        conn = self.__get_db_conn()
        cur = conn.cursor()
        with open("2019-metrics.txt", 'w') as fh:
            # Overall numbers
            print("** OVERALL METRICS**", file=fh)
            query = textwrap.dedent(
                """\
                SELECT COUNT(*) from {};\
                """
            ).format(self.tabs["Master"])
            cur.execute(query)
            total_registrants = cur.fetchone()[0]

            print("Total registrants: {}".format(total_registrants),
                  file=fh)

            # Main meeting
            query = textwrap.dedent(
                """\
                SELECT COUNT(*) from {}\
                WHERE "Main meeting Registration"=="Y";
                """
            ).format(self.tabs["Master"])
            cur.execute(query)
            total_registrants = cur.fetchone()[0]

            print("Total registrants (main meeting): {}".format(
                total_registrants), file=fh)

            # Workshops
            query = textwrap.dedent(
                """\
                SELECT COUNT(*) from {}\
                WHERE "Workshop Registration"=="Y";
                """
            ).format(self.tabs["Master"])
            cur.execute(query)
            total_registrants = cur.fetchone()[0]

            print("Total registrants (workshops): {}".format(
                total_registrants), file=fh)

            # Tutorials
            query = textwrap.dedent(
                """\
                SELECT COUNT(*) from {}\
                WHERE "Tutorial Registration"=="Y";
                """
            ).format(self.tabs["Master"])
            cur.execute(query)
            total_registrants = cur.fetchone()[0]

            print("Total registrants (tutorials): {}".format(
                total_registrants), file=fh)

            # Overall breakdown by groups
            print("\nGroup metrics:", file=fh)
            query = textwrap.dedent(
                """\
                SELECT "Registration Group", COUNT(*) from {}\
                GROUP BY "Registration Group"\
                ORDER BY COUNT(*) ASC;\
                """
            ).format(self.tabs["Master"])
            cur.execute(query)
            rows = cur.fetchall()
            for group, numbers in rows:
                print("{}: {}".format(group, numbers), file=fh)

            # Overall breakdown by gender
            print("\nGender metrics:", file=fh)
            query = textwrap.dedent(
                """\
                SELECT "Gender", COUNT(*) FROM {}\
                GROUP BY "Gender";\
                """
            ).format(self.tabs["Master"])
            cur.execute(query)
            rows = cur.fetchall()
            for group, numbers in rows:
                print("{}: {}".format(group, numbers), file=fh)

            # Overall breakdown by country
            print("\nLocation metrics:", file=fh)
            query = textwrap.dedent(
                """\
                SELECT "Country", COUNT(*) FROM {}\
                GROUP BY "Country"\
                ORDER BY COUNT(*) ASC;\
                """
            ).format(self.tabs["Master"])
            cur.execute(query)
            rows = cur.fetchall()
            for group, numbers in rows:
                print("{}: {}".format(group, numbers), file=fh)

            # Shirts
            print("\nShirts requested:", file=fh)
            totalshirts = 0
            for shirtsize in ["S", "M", "L", "XL"]:
                query = textwrap.dedent(
                    """\
                    SELECT SUM("Shirt {}") from {};\
                    """
                ).format(shirtsize, self.tabs["Master"])
                cur.execute(query)
                shirts = cur.fetchone()[0]
                totalshirts += shirts

                print("Shirts ({}): {}".format(
                    shirtsize, shirts), file=fh)
            print("Shirts (total): {}".format(totalshirts), file=fh)

            # Banquet tickets
            query = textwrap.dedent(
                """\
                SELECT SUM("Banquet Tickets") from {};\
                """
            ).format(self.tabs["Master"])
            cur.execute(query)
            banquet_tickets = cur.fetchone()[0]
            print("\nBanquet tickets purchased: {}".format(banquet_tickets),
                  file=fh)

            # Members
            print("\n** MEMBER METRICS**", file=fh)
            query = textwrap.dedent(
                """\
                SELECT COUNT(*) from {}\
                WHERE "OCNS Member"=="Y";\
                """
            ).format(self.tabs["Master"])
            cur.execute(query)
            total_registrants = cur.fetchone()[0]
            print("OCNS members registered: {}".format(total_registrants),
                  file=fh)

            # Members breakdown
            query = textwrap.dedent(
                """\
                SELECT "Registration Group", COUNT(*) from {}\
                WHERE "OCNS Member"=="Y"\
                GROUP BY "Registration Group"\
                ORDER BY COUNT(*) ASC;\
                """
            ).format(self.tabs["Master"])
            cur.execute(query)
            rows = cur.fetchall()
            for group, numbers in rows:
                print("{}: {}".format(group, numbers), file=fh)

            # Overall breakdown by gender
            print("\nGender metrics:", file=fh)
            query = textwrap.dedent(
                """\
                SELECT "Gender", COUNT(*) FROM {}\
                WHERE "OCNS Member"=="Y"\
                GROUP BY "Gender";\
                """
            ).format(self.tabs["Master"])
            cur.execute(query)
            rows = cur.fetchall()
            for group, numbers in rows:
                print("{}: {}".format(group, numbers), file=fh)

            print("\nLocation metrics:", file=fh)
            query = textwrap.dedent(
                """\
                SELECT "Country", COUNT(*) FROM {}\
                WHERE "OCNS Member"=="Y"\
                GROUP BY "Country"\
                ORDER BY COUNT(*) ASC;\
                """
            ).format(self.tabs["Master"])
            cur.execute(query)
            rows = cur.fetchall()
            for group, numbers in rows:
                print("{}: {}".format(group, numbers), file=fh)

            # Non-Members
            print("\n** NON-MEMBER METRICS**", file=fh)
            query = textwrap.dedent(
                """\
                SELECT COUNT(*) from {}\
                WHERE "OCNS Member"=="N";\
                """
            ).format(self.tabs["Master"])
            cur.execute(query)
            total_registrants = cur.fetchone()[0]
            print("Non members registered: {}".format(total_registrants),
                  file=fh)

            # Members breakdown
            query = textwrap.dedent(
                """\
                SELECT "Registration Group", COUNT(*) from {}\
                WHERE "OCNS Member"=="N"\
                GROUP BY "Registration Group"\
                ORDER BY COUNT(*) ASC;\
                """
            ).format(self.tabs["Master"])
            cur.execute(query)
            rows = cur.fetchall()
            for group, numbers in rows:
                print("{}: {}".format(group, numbers), file=fh)

    def dump_all_data(self):
        """
        Dump data to files.

        :returns: TODO
        """

        # Full table dump
        query = textwrap.dedent(
            """\
            SELECT * FROM {}\
            ORDER BY "Email";
            """
        ).format(self.tabs['Master'])
        self.__dump_data("2019-Registration-master.csv", query, "csv")
        self.__dump_data("2019-Registration-master.html", query, "html")

        # Full table dump selected fields
        query = textwrap.dedent(
            """\
            SELECT "First Name",\
            "Middle Name",\
            "Last Name",\
            "Email",\
            "Main meeting Registration",\
            "Workshop Registration",\
            "Tutorial Registration",\
            "Shirt S",\
            "Shirt M",\
            "Shirt L",\
            "Shirt XL",\
            "Banquet Tickets",\
            "Special Meal"\
            FROM {}\
            ORDER BY "Email";
            """
        ).format(self.tabs['Master'])
        self.__dump_data("2019-Registration-all.csv", query, "csv")
        self.__dump_data("2019-Registration-all.html", query, "html")

        # Main meeting attendees
        query = textwrap.dedent(
            """\
            SELECT * FROM {}\
            WHERE "Main meeting Registration"=="Y"\
            ORDER BY "Email";
            """).format(self.tabs['Master'])
        self.__dump_data("2019-Main-meeting-attendees.csv", query, "csv")
        self.__dump_data("2019-Main-meeting-attendees.html", query, "html")

        # Workshop
        query = textwrap.dedent(
            """\
            SELECT *\
            FROM {}\
            WHERE "Workshop Registration"=="Y"\
            ORDER BY "Email";
            """).format(self.tabs['Master'])
        self.__dump_data("2019-Workshop-attendees.csv", query, "csv")
        self.__dump_data("2019-Workshop-attendees.html", query, "html")

        # Tutorials
        query = textwrap.dedent(
            """\
            SELECT *\
            FROM {}\
            WHERE "Tutorial Registration"=="Y"\
            ORDER BY "Email";
            """).format(self.tabs['Master'])
        self.__dump_data("2019-Tutorial-attendees.csv", query, "csv")
        self.__dump_data("2019-Tutorial-attendees.html", query, "html")

        # Banquets
        query = textwrap.dedent(
            """\
            SELECT \
            "First Name",\
            "Middle Name",\
            "Last Name",\
            "Email",\
            "Banquet Tickets",\
            "Special Meal"\
            FROM {}\
            WHERE not "Banquet Tickets"==0\
            ORDER BY "Email";
            """).format(self.tabs['Master'])
        self.__dump_data("2019-Banquet-attendees.csv", query, "csv")
        self.__dump_data("2019-Banquet-attendees.html", query, "html")

        # T-shirts
        query = textwrap.dedent(
            """\
            SELECT *\
            FROM {}\
            WHERE \
            not "Shirt S"== 0 OR\
            not "Shirt M"== 0 OR\
            not "Shirt L"== 0 OR\
            not "Shirt XL"== 0\
            ORDER BY "Email";
            """).format(self.tabs['Master'])

        self.__dump_data("2019-shirts.csv", query, "csv")
        self.__dump_data("2019-shirts.html", query, "html")

    def __dump_data(self, output_filename, query, output_format="csv"):
        """
        Dump results of query to a file.

        Uses SQlite's imbuilt import functions for simplicity

        :output_filename: File to dump data to
        :query: SQL query to execute
        :output_format: what format to output in. html, csv, tabs
        :returns: TODO

        """
        commands = textwrap.dedent(
            """\
            .open {}
            .headers on
            .mode {}
            .separator ,
            .output {}
            {}
            .quit \n
            """.format(
                self.db_name, output_format, output_filename, query))

        subprocess.run(["sqlite3"], input=commands, text=True, check=True)


if __name__ == "__main__":
    new_gen = Metrics()

    if len(sys.argv) == 5:
        print("Loading csv data to table", file=sys.stderr)
        new_gen.setup_new_db(sys.argv)

    new_gen.generate_metrics()
    new_gen.dump_all_data()
