import boto3
import json

sns = boto3.client('sns')

def lambda_handler(event, context):
    """Send a reminder email for an upcoming task."""
    try:
        print('From the catch block')
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

        # Send email via SNS
        sns.publish(
            TopicArn='arn:aws:sns:**********:**********:<topic_name>',
            Subject=subject,
            Message=message
        )
    except Exception as e:
        print('From the catch block')
        print(f"An unhandled error occured: {e}")
