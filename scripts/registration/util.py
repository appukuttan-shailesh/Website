#!/usr/bin/python3
"""
Python script to fetch information from memberclicks using the REST API.

API Documentation:
https://classic.memberclicks.com/hc/en-us/articles/360016335371-User

Note that we use "classic" memberclicks which does not provide the extensive
API that the new version seems to provide.

File: util.py

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


def check_user_registration(api_token, user_search_terms, year):
    """
    Check whether these user_search_terms are registered.

    :api_token: api_token
    :user_search_terms: list of users to check
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
    for aterm in user_search_terms:
        url = URL_user + aterm + '#'

        # Make the request
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            results = r.json()
            # returns a list if more than one result, otherwise results a
            # single dict. So we always convert it to a list for simplcity.
            if not isinstance(results['user'], list):
                presults = [results['user']]
            else:
                presults = results['user']
            print("\n** {} **".format(aterm))
            print("{} accounts found. Fetching information.".format(
                len(presults)))
            for userdata in presults:
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
                        print("\n{} is a valid member of {}.".format(
                            userdata['userName'], group
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
                    if 'attData' not in reg_results:
                        print("{} does not contain attribute".format(
                            userdata['userName']))
                    else:
                        registration = reg_results['attData']
                        if registration == year:
                            print(
                                "{} is registered.".format(
                                    userdata['userName']))
                            if group == "Basic Contact":
                                print("They can submit ONE abstract.")
                            else:
                                print("They can submit TWO abstracts.")
                        else:
                            print("{} has not yet registered for {}.".format(
                                userdata['userName'], year
                            ))
                else:
                    print("Received status code {}".format(r.status_code))
                    print("Response: {}".format(r.text))
        elif r.status_code == 204:
            print("No users found with search term {}".format(aterm))
            print("Received status code {}".format(r.status_code))
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
    :returns: nothing

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


def get_user_info(api_token, user_search_terms, active):
    """
    Get information from the database about a list of users.

    Currently, the API does not seem to return inactive users even when the
    parameter is given.

    :api_token: api_token
    :user_search_terms: list of usernames
    :active: whether or not user is active
    :returns: nothing

    """
    if active == "true":
        print("Looking in active users")
    else:
        print("Looking in inactive users")

    URL_user = (
        'https://ocns.memberclicks.net/services/user?pageSize=100&searchText='
    )
    headers = {
        'Accept': 'application/json',
        'Authorization': api_token
    }
    for aterm in user_search_terms:
        url = URL_user + aterm + '&active={}'.format(active) + '#'
        print(url)

        # Make the request
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            results = r.json()
            # returns a list if more than one result, otherwise results a
            # single dict. So we always convert it to a list for simplcity.
            if not isinstance(results['user'], list):
                presults = [results['user']]
            else:
                presults = results['user']
            print("\n** {} **".format(aterm))
            print("{} accounts found. Fetching information.".format(
                len(presults)))
            for userdata in presults:
                # fetch all attributes
                URL_attributes = (
                    'https://ocns.memberclicks.net/services/user/' +
                    userdata['userId'] + '?includeAtts=true'
                )
                p = requests.get(URL_attributes, headers=headers)
                if p.status_code == 200:
                    profile_info = p.json()
                    print("\n{}\n".format(profile_info))
                else:
                    print("Received status code {}".format(r.status_code))
                    print("Response: {}".format(r.text))
        elif r.status_code == 204:
            print("No users found with search term {}".format(aterm))
            print("Received status code {}".format(r.status_code))
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
    users = ['a.sinha2@herts.ac.uk']

    # Do the work
    token = get_token(api_key, username, password)
    check_user_registration(token, users, year)
    #  get_user_info(token, users)
    #  get_attribute_list(token)
    #  get_registered_users(token, year)
