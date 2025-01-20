import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Tasks')

# Initialize SNS client
sns = boto3.client('sns')
SNS_TOPIC_ARN = 'arn:aws:sns:<region>:677276091734:<topic_name>'

ADMIN_EMAIL = "**********@gmail.com" 

def update_status(task_id, new_status):
    response_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
    }
    try:
        response = table.update_item(
            Key={'id': task_id},
            UpdateExpression="SET #statusAttr = :statusValue",
            ExpressionAttributeNames={
                '#statusAttr': 'status'
            },
            ExpressionAttributeValues={
                ':statusValue': new_status 
            },
            ReturnValues="ALL_NEW"
        )

        # If status is completed, send a notification to the admin
        if new_status == "Completed":
            send_admin_notification(task_id)

        return {
            'statusCode': 200,
            "headers": response_headers,
            'body': json.dumps(response['Attributes'])
        }
    except Exception as e:
        return {
            'statusCode': 500,
            "headers": response_headers,
            'body': json.dumps(f"Error updating status: {str(e)}")
        }

def send_admin_notification(task_id):
    """Send a notification email to the admin when the task is marked as completed."""
    try:
        message = f"Task {task_id} has been marked as completed. Please review it."
        subject = f"Task {task_id} Completed Notification"
        
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message,
            MessageAttributes={
                'emails': {
                    'DataType': 'String',
                    'StringValue': ADMIN_EMAIL
                }
            }
        )
        print(f"Admin notification sent for task {task_id}.")
    except Exception as e:
        print(f"Error sending notification: {str(e)}")

def lambda_handler(event):
    response_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
    }

    try:
        body = json.loads(event.get('body', '{}'))
        task_id = body.get('id')
        new_status = body.get('status')

        if not task_id or not new_status:
            return {
                'statusCode': 400,
                "headers": response_headers,
                'body': json.dumps("Missing 'id' or 'status'")
            }

        return update_status(task_id, new_status)
    except Exception as e:
        return {
            'statusCode': 500,
            "headers": response_headers,
            'body': json.dumps(f"Error processing request: {str(e)}")
        }
