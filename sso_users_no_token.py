"""

Manage AWS SSO Users

python version: 3.7.0
boto version: ...

Reference:
https://docs.aws.amazon.com/singlesignon/latest/developerguide/what-is-scim.html
https://docs.aws.amazon.com/singlesignon/latest/userguide/okta-idp.html

"""

import requests
import ssl
import json
import sys


## SCIM header

scim_headers = {'Authorization' : 'Bearer {token}', 'Content-Type' : 'application/json'}


## SCIM endpoints

scim_user_url  = 'https://scim.us-west-2.amazonaws.com/Nv8dc56f917-e563-4913-a91b-53c17bd89295/scim/v2/Users'
scim_group_url = 'https://scim.us-west-2.amazonaws.com/Nv8dc56f917-e563-4913-a91b-53c17bd89295/scim/v2/Groups'


def test():
    """
    for testing..
    """

    response = requests.get('http://api.open-notify.org/astros.json')

    return response


def list_users():
    """
    GET /Users
    """

    response = requests.get(scim_user_url, headers=scim_headers)

    return response


def create_user(user_name, family_name, given_name, display_name, work_email):
    """
    POST /Users
    """

    scim_url = scim_user_url
    data = {
             'userName': user_name,
             'name': {
                       'familyName': family_name,
                       'givenName': given_name
             },
             'displayName': display_name,
             'userType': 'Employee',
             'locale': 'en-US',
             'active': 'true',
             'emails': [
                         {
                           'value': work_email,
                           'type': 'work',
                           'primary': 'true'
                         }
             ]
           }

    response = requests.post(scim_url, json=data, headers=scim_headers)

    return response


def update_group(member_id):
    """
    PATCH /Groups
    """

    group_id = '9267707bc4-f5402b43-4ea7-49d5-9463-66a6f5f02c69'
    scim_url = scim_group_url + '/' + group_id
    data = {
             'schemas': [
                          'urn:ietf:params:scim:api:messages:2.0:PatchOp'
                        ],
             'Operations': [
                             {
                               'op':'add',
                               'path':'members',
                               'value':[
                                         {
                                           'value': member_id
                                         }
                               ]
                             }
                           ]
           }

    response = requests.patch(scim_url, json=data, headers=scim_headers)

    return response


def main(user_name, family_name, given_name, display_name, work_email, argv):
    """
    Do the work..
    """

    if len(argv) < 2:
        print('Sorry.')
        exit()

    if argv[1] == 'list':
        response = list_users()

    elif argv[1] == 'create':
        response = create_user(user_name, family_name, given_name, display_name, work_email)

        # Add new user to our existing group
        member_id = response.json().get('id')
        group = update_group(member_id)

    else:
        print('Nope.')
        exit()

    pretty_json = json.dumps(response.json(), indent=4)
    #print(response.status_code)
    print(pretty_json)

    return


if __name__ == "__main__":

    main(
         user_name    = 'testUser@murchison.net',
         family_name  = 'User',
         given_name   = 'Test',
         display_name = 'Test User',
         work_email   = 'testUser@murchison.net',
         argv         = sys.argv
        )

