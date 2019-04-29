#!/usr/bin/env python3
"""
Get information about first authors that submitted abstracts and requested
travel awards from Memberclicks.

File: check_confmaster_registrations.py

Copyright 2019 Ankur Sinha
Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>
"""


import pandas as pd
import sys


def check_user_registration(confmaster_submissions, confmaster_users,
                            memberclicks_users):
    """
    Check whether first authors on confmaster are registered on memberclicks.

    :confmaster_submissions: submission data from Confmaster (no e-mails)
    :confmaster_users: User data export from Confmaster (needed for e-mails)
    :memberclicks_users: Conference registration export from memberclicks
    :returns: TODO
    """
    # All users on cm_users
    cm_users = pd.read_csv(confmaster_users)
    print("Confmaster user data: {} rows read".format(len(cm_users.index)))

    # Select from but 'email' is REQUIRED:
    #  (['UserID', 'First Name', 'Last Name', 'Affiliation 1', 'Affiliation 2',
    #  'Country', 'Keywords', 'Author of', 'Dynamic Fields', 'email',
    #  'Tracks'],
    cm_users = cm_users[['email', 'UserID', 'Country']]

    # All submissions on cm_users that requested travel awards
    abs_subs = pd.read_csv(confmaster_submissions)
    # Select from these, but 'ContactAuthor' is REQUIRED since it contains
    # their UserID:
    #  (['PaperID', 'Authors', 'ContactAuthor', 'Paper Type', 'Keywords',
    #  'Avg', 'Misc', 'Title' ])
    abs_subs = abs_subs[['PaperID', 'ContactAuthor']]
    print("Submissions data: {} rows read".format(len(abs_subs)))
    # ContactAuthor column in submissions is in the form:
    # First Name (#userid)
    # So we need to extract the userid
    abs_subs['UserID'] = abs_subs['ContactAuthor'].str.extract('(?P<userid>\d+)')
    abs_subs['UserID'] = abs_subs.UserID.astype(int)

    cm_abs_subs = pd.merge(
        abs_subs, cm_users, left_on='UserID', right_on='UserID'
    )
    print("Confmaster users AND submission data: {} rows".format(len(cm_abs_subs.index)))
    cm_abs_subs.sort_values('UserID', inplace=True)
    cm_abs_subs.to_csv('Confmaster-with-ids-and-emails.csv')
    print("Wrote CM + TA to file")
    print()

    # All registered members from m_users
    m_users = pd.read_csv(memberclicks_users)
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

    m_users = m_users[
        ['Username', 'Contact Name', 'Group', 'Gender', 'Job Title',
         'Institution', 'Dept.', 'Laboratory', 'Country', 'Email'
         ]]
    # intersection of cm_users users and m_users registrants
    # Please note the names of the two e-mail fields
    merged_users_username = pd.merge(
        m_users, cm_abs_subs, how='inner', left_on='Username',
        right_on='email')
    merged_users_email = pd.merge(
        m_users, cm_abs_subs, how='inner', left_on='Email',
        right_on='email')

    merged_users = pd.concat(
        [merged_users_username, merged_users_email]
    ).drop_duplicates().reset_index(drop=True)

    print("CM + Memberclicks: {} rows".format(len(merged_users.index)))
    merged_users.sort_values('UserID', inplace=True)
    merged_users.to_csv('Result.csv')


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
