import json
import boto3
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler():
    cognito_client = boto3.client('cognito-idp')
    user_pool_id = 'eu-west-1_EzjFEAwIm' 
    group_name = 'Team_members'

    try:
        response = cognito_client.list_users_in_group(
            UserPoolId=user_pool_id,
            GroupName=group_name
        )
        users = response['Users']
        logger.info(f"Users fetched successfully: {users}")
        return {
            'statusCode': 200,
            'body': json.dumps([user['Attributes'] for user in users])
        }
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error fetching users: {str(e)}")
        }
