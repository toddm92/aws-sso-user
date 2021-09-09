"""

Manage AWS SSO Users

python version: 3.7.0

Reference:
https://docs.aws.amazon.com/singlesignon/latest/developerguide/what-is-scim.html
https://docs.aws.amazon.com/singlesignon/latest/userguide/okta-idp.html

"""

import requests
import ssl
import json
import sys
import boto3
import os
from base64 import b64decode


ENCRYPTED = os.environ.get('Auth')
DECRYPTED = boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED),
            EncryptionContext={'LambdaFunctionName': os.environ.get('AWS_LAMBDA_FUNCTION_NAME')})['Plaintext'].decode('utf-8')

## SCIM header

scim_headers = {'Authorization' : DECRYPTED, 'Content-Type' : 'application/json'}


## SCIM endpoints

scim_user_url  = 'https://scim.us-west-2.amazonaws.com/Nv8dc56f917-e563-4913-a91b-53c17bd89295/scim/v2/Users'
scim_group_url = 'https://scim.us-west-2.amazonaws.com/Nv8dc56f917-e563-4913-a91b-53c17bd89295/scim/v2/Groups'


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


def lambda_handler(event, context):
    """
    Do the work..
    """

    user_name    = event['userName']
    family_name  = event['familyName']
    given_name   = event['givenName']
    display_name = event['displayName']
    work_email   = event['email']
   
    response = create_user(user_name, family_name, given_name, display_name, work_email)

    # Add new user to our existing group
    member_id = response.json().get('id')
    group     = update_group(member_id)

    pretty_json = json.dumps(response.json(), indent=4)
    #print(response.status_code)
    print(pretty_json)

    return

