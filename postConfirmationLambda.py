import json
import boto3
from botocore.exceptions import ClientError

# Initialize AWS services clients
sns_client = boto3.client('sns')
cognito_client = boto3.client('cognito-idp')
dynamodb_client = boto3.client('dynamodb')

SNS_TOPIC_ARN = "arn:aws:sns:<region>:677276091734:<topic_name>"
USER_POOL_ID = "<region>_EzjFEAwIm"
GROUP_NAME = "Team_members"
USERS_TABLE_NAME = "Users" 

def lambda_handler(event, context):
    """
    This handler is a post confirmation trigger attached to Cognito.
    After the user has been confirmed, this trigger retrieves the user information 
    from the event object, subscribes the user to an SNS topic, adds the user to a group, 
    and saves user data to DynamoDB.
    """

    print(f"event: {event}")

    # Extract user data from the event
    username = event['userName']
    email = event['request']['userAttributes']['email']
    user_id = event['request']['userAttributes']['sub']
    role = "member" 

    filter_policy = {
        'email': [email],
        'group': [GROUP_NAME]
    }

    try:
        # Subscribe the user to the SNS topic
        sns_response = sns_client.subscribe(
            TopicArn=SNS_TOPIC_ARN,
            Protocol='email',
            Endpoint=email,
            Attributes={
                'FilterPolicy': json.dumps(filter_policy)
            }
        )
        print(f"SNS Subscription successful: {sns_response}")

        # Add the user to the specified Cognito group
        cognito_response = cognito_client.admin_add_user_to_group(
            UserPoolId=USER_POOL_ID,
            Username=email,
            GroupName=GROUP_NAME
        )
        print(f"User added to group {GROUP_NAME}: {cognito_response}")

        # Save user data to DynamoDB
        dynamodb_response = save_user_to_dynamodb(user_id, email, role, username)
        print(f"User saved to DynamoDB: {dynamodb_response}")

    except ClientError as e:
        print(f"An error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error processing the request: {str(e)}")
        }

    # Return event to allow Cognito flow to continue
    return event


def save_user_to_dynamodb(user_id, email, role, username):
    """
    Save the user details to the DynamoDB Users table.
    """
    try:
        # Save user data into DynamoDB table
        dynamodb_client.put_item(
            TableName=USERS_TABLE_NAME,
            Item={
                'id': {'S': user_id},
                'email': {'S': email},
                'role': {'S': role},
                'username': {'S': username}
            }
        )
        return {"status": "User added to DynamoDB"}
    except ClientError as e:
        print(f"Error saving user to DynamoDB: {e}")
        raise Exception(f"Error saving user to DynamoDB: {e}")
