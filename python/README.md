
## AWS Configuration needed to make cognito_access.py work
- Create a user pool
- Create an Identity pool with the user pool as an authenitcation provider
- In the Identity pool Authentication Providers change the `Authenticated role selection` to be `Choose role from token`
- In the user pool, create a group.  Create an IAM role with the permissions required by the group members
- Add a trust relationship to the role to allow cognito-identity to assume the role. Example:
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Federated": "cognito-identity.amazonaws.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "cognito-identity.amazonaws.com:aud": "us-east-1:e2f821f7-29e3-4b96-943a-3449e485b1a3"
        },
        "ForAnyValue:StringLike": {
          "cognito-identity.amazonaws.com:amr": "authenticated"
        }
      }
    }
  ]
}
```
- Create a user and add to group
- Add the appropriate values to .env
- Run cognito_access.py



## References
- https://docs.aws.amazon.com/cognito/latest/developerguide/role-trust-and-permissions.html
- https://bobbyhadz.com/blog/aws-cognito-change-force-change-password
- https://www.educative.io/edpresso/what-is-the-python-code-for-aws-cognito




