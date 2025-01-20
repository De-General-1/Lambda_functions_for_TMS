import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Tasks')

# Initialize SNS client
sns = boto3.client('sns')
SNS_TOPIC_ARN = 'arn:aws:sns:<region>:677276091734:<topic_name>'

ADMIN_EMAIL = "aboagyefafa12@gmail.com" 

def update_task(task_id, title, description, status, start_date, due_date, assigned_to):
    response_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
    }
    try:
        # Update task in DynamoDB
        response = table.update_item(
            Key={'id': task_id},
            UpdateExpression="SET title = :title, description = :description, #status = :status, "
                             "start_date = :start_date, due_date = :due_date, assigned_to = :assigned_to",
            ExpressionAttributeNames={
                '#status': 'status'  # Use alias for the reserved keyword 'status'
            },
            ExpressionAttributeValues={
                ':title': title,
                ':description': description,
                ':status': status,
                ':start_date': start_date,
                ':due_date': due_date,
                ':assigned_to': assigned_to
            },
            ReturnValues="ALL_NEW"
        )

        # If the status is 'Completed', send a notification to the admin
        if status == "Completed":
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
            'body': json.dumps(f"Error updating task: {str(e)}")
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
        title = body.get('title')
        description = body.get('description')
        status = body.get('status')
        start_date = body.get('start_date')
        due_date = body.get('due_date')
        assigned_to = body.get('assigned_to')

        # Validate input
        if not task_id or not title or not description or not status or not start_date or not due_date or not assigned_to:
            return {
                'statusCode': 400,
                "headers": response_headers,
                'body': json.dumps("Missing required fields in the request")
            }

        return update_task(task_id, title, description, status, start_date, due_date, assigned_to)
    except Exception as e:
        return {
            'statusCode': 500,
            "headers": response_headers,
            'body': json.dumps(f"Error processing request: {str(e)}")
        }
