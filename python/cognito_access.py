#!/usr/bin/env python3
# Cognito test - Login via Cognito and access an S3 bucket

import os
import sys
import json
import boto3
from dotenv import load_dotenv, find_dotenv


def login():
    client = boto3.client("cognito-idp", region_name="us-east-1")
    response = client.initiate_auth(
        ClientId=os.getenv("COGNITO_USER_CLIENT_ID"),
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": os.getenv("USERNAME"), "PASSWORD": os.getenv("PASSWORD")},
    )
    id_token = response["AuthenticationResult"]["IdToken"]
    return id_token


def get_credentials(id_token):
    client = boto3.client('cognito-identity', region_name="us-east-1")
    response = client.get_id(AccountId=os.getenv("AWS_ACCOUNT_ID"), IdentityPoolId=os.getenv("IDENTITY_POOL_ID"),
                             Logins={f'cognito-idp.us-east-1.amazonaws.com/{os.getenv("USER_POOL_ID")}': id_token}
                             )
    identity_id = response["IdentityId"]
    response = client.get_credentials_for_identity(IdentityId=identity_id,
                                                   Logins={
                                                       f'cognito-idp.us-east-1.amazonaws.com/{os.getenv("USER_POOL_ID")}': id_token}
                                                   )
    credentials = response["Credentials"]
    return credentials


def create_session(credentials):
    session = boto3.session.Session(
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretKey"],
        aws_session_token=credentials["SessionToken"]
    )
    return session


def get_s3(session):
    client = session.client('s3')
    response = client.list_buckets()
    print(response)


def main():
    load_dotenv(find_dotenv())
    id_token = login()
    credentials = get_credentials(id_token)
    session = create_session(credentials)
    # print(session.client('sts').get_caller_identity())
    get_s3(session)


if __name__ == '__main__':
    main()
