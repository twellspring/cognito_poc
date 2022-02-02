#!/usr/bin/env python3
# Cognito test - Login via Cognito and access an S3 bucket

import os
import json
from typing import Tuple
import boto3
from dotenv import load_dotenv, find_dotenv
import base64


def dump(d: dict) -> None:
    print(json.dumps(d, indent=4, default=str))


def jwt_decode(token: str) -> Tuple[dict, dict, bytes]:
    """
    jwt has 3 uuencoded parts: header, payload, signature
    The signature is a bytestring that can not be converted to an object
    """
    results = []
    for part in str(token).rsplit('.'):
        part_padded = part + "="*divmod(len(part), 4)[1]
        part_byte = base64.b64decode(part_padded)
        try:
            part_json_string = part_byte.decode("utf-8")
            part_obj = json.loads(part_json_string)
            results.append(part_obj)
        except UnicodeDecodeError:
            results.append(part_byte)
    return results[0], results[1], results[2]


def login() -> str:
    client = boto3.client("cognito-idp", region_name="us-east-1")
    response = client.initiate_auth(
        ClientId=os.getenv("COGNITO_USER_CLIENT_ID"),
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": os.getenv("USERNAME"), "PASSWORD": os.getenv("PASSWORD")},
    )
    id_token = response["AuthenticationResult"]["IdToken"]
    return id_token


def get_credentials(id_token: str) -> dict:
    client = boto3.client('cognito-identity', region_name="us-east-1")
    response = client.get_id(AccountId=os.getenv("AWS_ACCOUNT_ID"), IdentityPoolId=os.getenv("IDENTITY_POOL_ID"),
                             Logins={f'cognito-idp.us-east-1.amazonaws.com/{os.getenv("USER_POOL_ID")}': id_token}
                             )
    identity_id = response["IdentityId"]
    cognito_url = f'cognito-idp.us-east-1.amazonaws.com/{os.getenv("USER_POOL_ID")}'
    response = client.get_credentials_for_identity(IdentityId=identity_id,
                                                   Logins={
                                                       cognito_url: id_token}
                                                   )
    credentials = response["Credentials"]
    return credentials


def create_session(credentials: dict) -> boto3.session.Session:
    session = boto3.session.Session(
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretKey"],
        aws_session_token=credentials["SessionToken"]
    )
    return session


def print_s3(session: boto3.session.Session) -> None:
    client = session.client('s3')
    dump(client.list_buckets())


def main():
    load_dotenv(find_dotenv())
    id_jwt = login()
    # header, payload, signature = jwt_decode(id_jwt)
    credentials = get_credentials(id_jwt)
    session = create_session(credentials)
    print(session.client('sts').get_caller_identity())
    print_s3(session)


if __name__ == '__main__':
    main()
