import json
import boto3

# Initialize DynamoDB client
dynamodb_client = boto3.client('dynamodb')

USERS_TABLE_NAME = "Users" 

def lambda_handler(event):
    print(event)
    # Extract the userId from query parameters (ensure it's the sub)
    user_id = event.get('queryStringParameters', {}).get('userId')
    print(f"User ID: {user_id}")

    try:
        # Query DynamoDB to get user details based on userId (which corresponds to 'sub' in Cognito)
        response = dynamodb_client.get_item(
            TableName=USERS_TABLE_NAME,
            Key={
                'id': {'S': user_id}  
            }
        )
        
        # Check if user is found in the table
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps(f"User with userId {user_id} not found.")
            }

        # Extract the user data from the response
        user_data = {key: value['S'] for key, value in response['Item'].items()}
        
        # Return user data as JSON
        return {
            'statusCode': 200,
            'body': json.dumps(user_data)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error fetching user: {str(e)}")
        }
