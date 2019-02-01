#!/usr/bin/python3
"""
Python script to fetch information from memberclicks using the REST API.

API Documentation:
https://classic.memberclicks.com/hc/en-us/articles/360016335371-User

Note that we use "classic" memberclicks which does not provide the extensive
API that the new version seems to provide.

File: api.py

Copyright 2019 Ankur Sinha
Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>
"""


import requests


def get_token(apikey, username, password):
    """
    Get authorization token from server.

    :apikey: API key to use
    :username: Username to use
    :password: password to use
    :returns: authorization token

    """
    # End point for authorisation
    URL_auth = 'https://ocns.memberclicks.net/services/auth'

    # Initialise to nothing
    api_token = None

    # Case sensitive
    data = {
        'apiKey': apikey,
        'username': username,
        'password': password,
    }
    # set the headers so that we get a json response instead of the default XML
    headers_auth = {
        'Accept': 'application/json'
    }

    # Get the api_token
    r = requests.post(URL_auth, data=data, headers=headers_auth)
    # Check response code
    if r.status_code == 200:
        api_token = r.json()['token']
    else:
        print("Received status code {}".format(r.status_code))
        print("Response: {}".format(r.text))

    return api_token


def check_user_registration(api_token, user_emails, year):
    """
    Check whether these user_emails are registered.

    :api_token: api_token
    :user_emails: list of users to check
    :year: registration year to check for
    :returns: nothing

    """
    group_list = ["OCNS Board", "Student Member", "Faculty Member",
                  "Basic Contact", "Postdoc Member"]

    headers = {
        'Accept': 'application/json',
        'Authorization': api_token
    }
    URL_user = 'https://ocns.memberclicks.net/services/user?searchText='
    for anemail in user_emails:
        url = URL_user + anemail

        # Make the request
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            results = r.json()
            if len(results) >= 1:
                print("\n** {} **".format(anemail))
                print("Accounts found. Checking registration.")
                for auser, userdata in results.items():
                    # check group
                    URL_groups = (
                        'https://ocns.memberclicks.net/services/user/' +
                        userdata['userId'] + '/attribute/453639'
                    )
                    p = requests.get(URL_groups, headers=headers)
                    if p.status_code == 200:
                        group_results = p.json()
                        group = group_results['attData']
                        if group in group_list:
                            print("{} is a valid member of {}.".format(
                                anemail, group
                            ))
                    else:
                        print("Received status code {}".format(r.status_code))
                        print("Response: {}".format(r.text))

                    # check registration
                    URL_registration = (
                        'https://ocns.memberclicks.net/services/user/' +
                        userdata['userId'] + '/attribute/609323'
                    )
                    p = requests.get(URL_registration, headers=headers)
                    if p.status_code == 200:
                        reg_results = p.json()
                        registration = reg_results['attData']
                        if registration == year:
                            print(
                                "{} is registered.".format(anemail)
                            )
                            if group == "Basic Contact":
                                print("They can submit ONE abstract.")
                            else:
                                print("They can submit TWO abstracts.")
                    else:
                        print("Received status code {}".format(r.status_code))
                        print("Response: {}".format(r.text))
            else:
                print("No users found with e-mail {}".format(anemail))
        else:
            print("Received status code {}".format(r.status_code))
            print("Response: {}".format(r.text))


def get_registered_users(api_token, year):
    """
    Get list of users registered for a particular conference year.

    We get the whole user list and count.

    TODO: incomplete. There does not seem to be a way of searching by an
    attribute value.


    :api_token: api_token
    :searchID: searchID of the search
    :returns: Nothing

    """
    headers = {
        'Accept': 'application/json',
        'Authorization': api_token
    }
    # Does not work
    URL_profiles = (
        'https://ocns.memberclicks.net/services/attribute/609323/user'
    )
    r = requests.get(URL_profiles, headers=headers)
    if r.status_code == 200:
        print(r.json())
    else:
        print("Received status code {}".format(r.status_code))
        print("Response: {}".format(r.text))


def get_attribute_list(api_token):
    """
    Get list of attributes.

    :api_token: api_token
    :returns: TODO

    """
    URL_attributes = 'https://ocns.memberclicks.net/services/attribute'
    headers = {
        'Accept': 'application/json',
        'Authorization': api_token
    }
    r = requests.get(URL_attributes, headers=headers)
    if r.status_code == 200:
        print(r.json())
    else:
        print("Received status code {}".format(r.status_code))
        print("Response: {}".format(r.text))


if __name__ == "__main__":
    # credentials
    api_key = ""
    username = ""
    password = ''
    year = "2019"

    # list of users to check
    users = []

    # Do the work
    token = get_token(api_key, username, password)
    check_user_registration(token, users, year)
    get_attribute_list(token)
    #  get_registered_users(token, year)
