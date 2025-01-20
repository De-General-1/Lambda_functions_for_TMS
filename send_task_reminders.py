import boto3
import json

sns = boto3.client('sns')

def lambda_handler(event, context):
    """Send a reminder email for an upcoming task."""
    try:
        print('From the try block')
        print(event)
        print(context)
        task = event
        
        message = (
            f"Reminder: You have an upcoming task deadline.\n\n"
            f"Title: {task['title']}\n"
            f"Due Date: {task['due_date']}\n\n"
            f"Please complete your task before the deadline."
        )
        subject = f"Task Reminder: {task['title']}"
        emails = task['assigned_emails']

        # Send email via SNS
        for email in emails:
        # Publish the message to SNS topic for each user individually
            sns.publish(
            TopicArn='arn:aws:sns:<region>:677276091734:<topic_name>',
            Subject=subject,
            Message=message,
            MessageAttributes={
                'email': {
                    'DataType': 'String',
                    'StringValue': email 
                },
                'group': {
                    'DataType': 'String',
                    'StringValue': 'Team_members'
                }
            }
        )
    except Exception as e:
        print('From the catch block')
        print(f"An unhandled error occured: {e}")
