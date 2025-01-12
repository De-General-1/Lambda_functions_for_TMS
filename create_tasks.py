import json
import boto3
from datetime import datetime, timedelta

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
tasks_table = dynamodb.Table('Tasks')
# Initialize EventBridge and SNS clients
eventbridge = boto3.client('events')
sns = boto3.client('sns')
SNS_TOPIC_ARN = 'arn:aws:sns:<region>:************:<function>'

ADMIN_EMAIL = "**********@gmail.com"

def schedule_deadline_reminder(task_id, title, due_date, assigned_emails):
    """Schedule a reminder for task deadline."""
    lambda_client = boto3.client('lambda')
    
    # Calculate reminder time (1 day before due date)
    reminder_time = datetime.strptime(due_date, '%Y-%m-%d') - timedelta(days=1)
    reminder_time_iso = reminder_time.strftime('%Y-%m-%dT%H:%M:%S') + "Z"

    # Generate unique rule name
    rule_name = f"TaskReminder_{task_id}"
 
    # Create EventBridge rule
    eventbridge.put_rule(
        Name=rule_name,
        ScheduleExpression=f"cron(0 8 {reminder_time.day} {reminder_time.month} ? {reminder_time.year})",
        State='ENABLED'
    )

    # Add the Lambda function as the target
    eventbridge.put_targets(
        Rule=rule_name,
        Targets=[{
            'Id': f"ReminderTarget_{task_id}",
            'Arn': 'arn:aws:lambda:eu-west-1:************:function:sendReminders',
            'Input': json.dumps({
                'task_id': task_id,
                'title': title,
                'due_date': due_date,
                'assigned_emails': assigned_emails
            })
        }]
    )

def create_task_id():
    """Generates a new task ID in the format T_XXXX."""
    import random
    task_id = "T_" + str(random.randint(1000, 9999))
    return task_id

def send_task_notification(emails, admin_email, title, start_date, due_date):
    """Sends notifications via SNS to all users and CCs the admin."""
    
    message = (
        f"You have been assigned a new task:\n\n"
        f"Title: {title}\n"
        f"Start Date: {start_date}\n"
        f"Due Date: {due_date}\n\n"
        f"Please check the system for more details."
    )
    subject = f"New Task Assigned: {title}"

    
    all_emails = emails + [admin_email]
    email_string = emails
    email_string = ','.join(emails)

    print(f"Emails_string: {email_string}")
    print(f"Admin_Email: {admin_email}")
    print(f"Emails: {emails}")
    print(f"All Emails: {all_emails}")

    # Publish the message to SNS topic as a broadcast
    for email in emails:
        # Publish the message to SNS topic for each user individually
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=message,
            MessageAttributes={
                'email': {
                    'DataType': 'String',
                    'StringValue': email 
                }
            }
        )
    
    # Log the sent notification
    print(f"Notification sent to {email_string}")


def lambda_handler(event, context):
    body = json.loads(event.get('body', '{}'))

    # Create the task item
    task_id = create_task_id()
    task_item = {
        'id': task_id,
        'title': body['title'],
        'description': body.get('description', ''),
        'files': [],
        'status': 'not-started',
        'start_date': body['startDate'],
        'due_date': body['dueDate'],
        'assigned_to': body['assigned_to'],
        'completed_by': []
    }

    response_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,GET,POST",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
    }

    try:
        # Save the task to the database
        tasks_table.put_item(Item=task_item)

        # Get the emails directly from the request body
        assigned_emails = body['assigned_emails'] 
        print(f"Assigned Emails: {assigned_emails}")

        # Send notifications
        if assigned_emails:
            send_task_notification(
                emails=assigned_emails,
                admin_email=ADMIN_EMAIL,
                title=body['title'],
                start_date=body['startDate'],
                due_date=body['dueDate']
            )

        # Schedule deadline reminders
        schedule_deadline_reminder(task_id, body['title'], body['dueDate'], assigned_emails)

        return {
            'statusCode': 200,
            "headers": response_headers,
            'body': json.dumps(f"Task {task_id} added successfully and notifications sent!")
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            "headers": response_headers,
            'body': json.dumps(f"Error adding task or sending notifications: {str(e)}")
        }
