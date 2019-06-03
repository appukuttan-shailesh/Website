#!/usr/bin/env python3
"""
Verify that authors from Confmaster submissions have registered for the
conference on Memberclicks.

File: check_confmaster_registrations.py

Copyright 2019 Ankur Sinha
Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>
"""


import pandas as pd
import sys
import re


def check_user_registration(confmaster_submissions, confmaster_users,
                            memberclicks_users):
    """
    Check whether first authors on confmaster are registered on memberclicks.

    I had initially used pandas, but using dataframes doesn't work too well
    when you have a table with variable number of columns which we do here
    because a submission can have any number of co-authors. That needs a list
    within the dataframe, and a "join" with the IDs of that list. This isn't
    simple to do with  Pandas. Much simpler to do manually like a db.

    :confmaster_submissions: submission data from Confmaster (no e-mails)
    :confmaster_users: User data export from Confmaster (needed for e-mails)
        Note that this must be the "saved member profile search", and not the
        receipt-export. The receipt-export only specifies the username-email,
        not the contact-email which we need to check against.
    :memberclicks_users: Conference registration export from memberclicks
    :returns: TODO
    """
    # Set up files
    registered_fname = "2019-Registered.txt"
    not_registered_fname = "2019-Not-Registered.txt"

    registered_fd = open(registered_fname, 'w')
    not_registered_fd = open(not_registered_fname, 'w')

    # Registered users on memberclicks
    m_users = pd.read_csv(memberclicks_users)
    m_users['Email'] = m_users['Email'].str.lower()
    print("Memberclicks data: {} rows read".format(len(m_users.index)))
    # Select from, but 'Username' and 'Email' are REQUIRED
    # (['Username', 'Expiration', 'Contact Name', 'Email', 'Group',
    #  'First Name', 'Middle Name', 'Last Name', 'Salutation', 'Gender',
    #  'Birthday', 'Job Title', 'Institution', 'Dept.', 'Laboratory',
    #  'Address', 'City', 'State', 'Postal code', 'Country', 'URL',
    #  'Work Phone', 'Work Fax', 'Main areas of research', 'Research Interest',
    #  'Research Interest Other', 'PhD Advisor', 'PhD University',
    #  'Postdoc 1 Advisor', 'Postdoc 1 Institution', 'Postdoc 2 Advisor',
    #  'Postdoc 2 Institution', 'Postdoc 3 Advisor', 'Postdoc 3 Institution',
    #  'IM', 'Skype IM', 'Twitter', 'NeuroNetwork profile',
    #  'Link to publication list', 'Bylaws Agreement', 'Date of Approval',
    #  'Highest Degree Inst', 'Highest Degree', 'Highest Degree Date',
    #  'Status', 'Electronic Mail', 'Highest Degree Year', 'Picture',
    #  'MembershipTypeWhenApplied', 'Electronic Mail Non-Member',
    #  'Years Dues Paid', 'RegistrationYear'],

    # We only need e-mails to check for registration
    m_users = m_users['Email'].values

    # All users on Confmaster
    cm_users = pd.read_csv(confmaster_users)
    print("Confmaster user data: {} rows read".format(len(cm_users.index)))

    # Select from but 'email' is REQUIRED:
    #  (['UserID', 'First Name', 'Last Name', 'Affiliation 1', 'Affiliation 2',
    #  'Country', 'Keywords', 'Author of', 'Dynamic Fields', 'email',
    #  'Tracks'],
    cm_users = cm_users[['email', 'UserID']]
    # Convert to a dict
    # { 'userid' : 'email' }
    cm_users = cm_users.values
    cm_users_dict = {}
    for user in cm_users:
        cm_users_dict[str(user[1])] = user[0]

    # All submissions on cm_users that requested travel awards
    abs_subs = pd.read_csv(confmaster_submissions)
    # Select from these, but 'ContactAuthor' is REQUIRED since it contains
    # their UserID:
    #  (['PaperID', 'Authors', 'ContactAuthor', 'Paper Type', 'Keywords',
    #  'Avg', 'Misc', 'Title' ])
    abs_subs = abs_subs[['PaperID',  'Authors', 'ContactAuthor']]
    print("Submissions data: {} rows read".format(len(abs_subs)))
    # Convert to numpy so I can iterate
    abs_subs = abs_subs.values

    correct_submissions = []
    incorrect_submissions = []

    for row in abs_subs:
        paperid = row[0]
        authors = row[1]
        first_author = row[2]

        first_author = get_author_info(first_author)
        # Fetch e-mail from user list
        # Only one first author here
        for author in first_author:
            userid = [*author][0]
            if userid in cm_users_dict:
                email = cm_users_dict[[*author][0]].lower()
                author[userid]['email'] = email
                if email in m_users:
                    correct_submissions.append(paperid)
                    print("\n** Paper ID: {} **".format(paperid),
                          file=registered_fd)
                    print("First author {} ({}) is registered".format(
                        author[userid]['name'], author[userid]['email']),
                          file=registered_fd)

                # else, check other authors
                else:
                    incorrect_submissions.append(paperid)
                    print("\n** Paper ID: {} **".format(paperid),
                          file=not_registered_fd)
                    print("First author {} ({}) is NOT registered".format(
                        author[userid]['name'], author[userid]['email']),
                          file=not_registered_fd)

                    print("Other authors status:", file=not_registered_fd)

                    # First author is repeated here, so remove it
                    authors = get_author_info(authors)
                    del authors[0]

                    for author in authors:
                        userid = [*author][0]
                        if userid in cm_users_dict:
                            email = cm_users_dict[[*author][0]].lower()
                            author[userid]['email'] = email
                            if email in m_users:
                                print("{} ({}) is registered".format(
                                    author[userid]['name'],
                                    author[userid]['email']),
                                      file=not_registered_fd)
                            else:
                                print("{} ({}) is not registered".format(
                                    author[userid]['name'],
                                    author[userid]['email']),
                                      file=not_registered_fd)
    registered_fd.close()
    not_registered_fd.close()


def get_author_info(authorlist):
    """Get author names and ids from a confmaster list

    :authorlist: string containing list of authors each of form '<name> (#id)'
    :returns: dict
    """
    author_regex = r'[\w#() 0-9\-\.]+'
    authorinfo = re.findall(author_regex, authorlist)
    result = []
    for author in authorinfo:
        authorinfo_dict = {}
        tokens = re.findall(r'[\.\w-]+', author)
        name = tokens[:-1]
        userid = tokens[-1]
        authorinfo_dict[str(userid)] = {'name': name}
        result.append(authorinfo_dict)

    return result


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: {} {} {} {}".format(
            "check_confmaster_registrations.py",
            "<confmaster submission data csv file>",
            "<confmaster user data csv file>",
            "<memberclicks user data csv file>"
        ))
        sys.exit(-1)
    else:
        check_user_registration(sys.argv[1], sys.argv[2], sys.argv[3])
