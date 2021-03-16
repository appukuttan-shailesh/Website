#!/usr/bin/python3
"""
Python script to fetch list of CNS registrants from Memberclicks Oasis based on
the RegistrationYear attribute.

File: oasis-registration-list.py

Copyright 2021 Ankur Sinha
Author: Ankur Sinha <sanjay DOT ankur AT gmail DOT com>
"""


from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
from datetime import datetime


baseurl = 'https://ocns.memberclicks.net/'
# from the get_groups function
# these are the ones we care for in abstract submission
# All members can submit 2 abstracts
# Non members (prospect) can submit 1 abstract
member_types = [
    "Faculty Member/For-profit Employee", "OCNS Board",
    "Postdoc Member/Non-profit Employee", "Student Member"
]


def get_token(client_id, client_secret):
    """
    Get authorization token from server.

    :param client ID: client ID to use
    :param client secret: client secret
    :returns: authorization token

    """
    # End point for authorisation
    URL_auth = baseurl + 'oauth/v1/token'
    auth = HTTPBasicAuth(client_id, client_secret)
    client = BackendApplicationClient(client_id)
    oauth = OAuth2Session(client=client)

    # Initialise to nothing
    api_token = oauth.fetch_token(token_url=URL_auth, auth=auth)

    #  print("API Token received: {}".format(api_token))
    return api_token


def get_groups(client_id, api_token):
    """Get list of groups

    :param client_id: client ID
    :param api_token: API Token
    :returns: TODO
    """
    group_endpoint = baseurl + "api/v1/group"
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer {}".format(api_token)
    }
    client = OAuth2Session(client_id, token=token)
    r = client.get(group_endpoint, headers=headers)
    if r.status_code == 200:
        results = r.json()
        print("Total groups: ", results["totalCount"])
        print("Groups are:")
        for group in results["groups"]:
            print("{}".format(group["name"]))


def get_registered_users(api_token, year):
    """
    Get list of users registered for a particular conference year.

    :param api_token: api_token
    :param year: value of RegistrationYear field to test
    :returns: Nothing

    """
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer {}".format(api_token),
    }
    params = {
        "pageSize": "100"
    }
    data = {
        'RegistrationYear': year,
    }
    # No slash at the start here
    URL_profiles = baseurl + "api/v1/profile/search"
    client = OAuth2Session(client_id, token=token)
    r = client.post(URL_profiles, headers=headers, json=data)
    # https://help.memberclicks.com/hc/en-us/articles/230536427-API-Resources-Profile-Search
    if r.status_code == 201:
        # https://help.memberclicks.com/hc/en-us/articles/230536367#get-a-list-of-profiles-by-search-id
        search_url = r.json()["profilesUrl"]
        print("Received search URL: {}".format(search_url))
        print("Getting profiles")
        URL_profiles = search_url
        client = OAuth2Session(client_id, token=token)
        r = client.get(URL_profiles, headers=headers, params=params)
        if r.status_code == 200:
            results = r.json()
            print("Total profiles found: {}".format(results["totalCount"]))
            print("Iterating pages")
            next_page_url = results["firstPageUrl"]
            now = datetime.now().strftime("%Y%m%d%H%M")
            csv_filename = "{}-cns-2021-registrants.csv".format(now)
            print("Writing to file: {}".format(csv_filename))
            with open(csv_filename, 'w') as f:
                print(
                    "{}, {}, {}, {}, {}, {}, {}, {}".format(
                        "First Name",
                        "Last Name",
                        "E-mail",
                        "Member type",
                        "Job Title",
                        "Organization",
                        "Registration Year",
                        "Number of abstracts permitted"
                    ),
                    file=f
                )
                while True:
                    client = OAuth2Session(client_id, token=token)
                    r = client.get(next_page_url, headers=headers)
                    results = r.json()
                    print("Page: {}/{}".format(results["pageNumber"],
                                               results["totalPageCount"]))

                    for profile in results["profiles"]:
                        # Number of abstracts
                        num_abstracts = 0
                        if profile["[Member Type]"] in member_types:
                            num_abstracts = 2
                        elif profile["[Member Type]"] == "Prospect":
                            num_abstracts = 1

                        # Mark Board members: for printed list
                        if "OCNS Board" in profile["[Group]"]:
                            member_type = "OCNS Board"
                        else:
                            member_type = profile["[Member Type]"]

                        # Mark non-members for printed list
                        if profile["[Member Type]"] == "Prospect":
                            member_type = "Non-member"

                        print(
                            "{}, {}, {}, {}, {}, {}, {}, {}".format(
                                profile["[Name | First]"],
                                profile["[Name | Last]"],
                                profile["[Email | Primary]"],
                                member_type,
                                profile["Job Title"],
                                profile["[Organization]"],
                                profile["RegistrationYear"],
                                num_abstracts
                            ), file=f)

                    next_page_url = results["nextPageUrl"]
                    if not next_page_url:
                        print("Reached last page. Done.")
                        break

    else:
        print("Received status code {}".format(r.status_code))
        print("Response: {}".format(r.text))


if __name__ == "__main__":
    # credentials
    client_id = "client-id"
    client_secret = "client-secret"

    # Must be a string
    year = "2021"

    # Do the work
    token = get_token(client_id, client_secret)
    get_registered_users(token, year)

    #  get_groups(client_id, token)
