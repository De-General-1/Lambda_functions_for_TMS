# Task Management System - Serverless Functions

This repository contains the AWS Lambda functions that power the Task Management System. The system is built using AWS serverless services like Lambda, API Gateway, DynamoDB, SNS, and Cognito. The purpose of these functions is to handle tasks like creating users, assigning tasks, updating task statuses, and sending notifications.

## Overview

- **Lambda Functions**: These are triggered by API Gateway to perform various operations, including user creation, task creation, task status updates, and sending notifications via SNS.
- **DynamoDB**: Used to store task data and backup user information.
- **SNS**: Used for sending task notifications and reminders.
- **Cognito**: Handles authentication and authorization (Admin vs Team Member).

## Functions

Here is a list of some of the Lambda functions in this project:

### `createUser`

- **Purpose**: Create a new user in the Cognito user pool.
- **Triggered by**: Admin via API endpoint.
- **Input**: User details (username, email, password, etc.).
- **Output**: Success or error message based on the result of the user creation.

### `createTask`

- **Purpose**: Assign a new task to a team member, with a deadline and status.
- **Triggered by**: Admin via API endpoint.
- **Input**: Task details (task name, description, assignee, deadline, etc.).
- **Output**: Task ID and confirmation of task creation.

### `getTaskById`

- **Purpose**: Fetch the details of a task by its unique ID.
- **Triggered by**: Admin or Team Member via API endpoint.
- **Input**: Task ID.
- **Output**: Task details (task name, description, status, assignee, etc.).

### `updateTaskStatus`

- **Purpose**: Update the status of a task (e.g., mark as "completed").
- **Triggered by**: Team Member via API endpoint.
- **Input**: Task ID, updated status.
- **Output**: Confirmation message, and a notification sent to the Admin.

### `sendTaskNotification`

- **Purpose**: Send a task notification to a team member or admin.
- **Triggered by**: Lambda functions that need to notify the user (e.g., after task assignment or status update).
- **Input**: User email, message (task assigned, task completed, reminder, etc.).
- **Output**: SNS message sent to the user.

### `sendTaskReminder`

- **Purpose**: Send a reminder to a team member about an upcoming task deadline.
- **Triggered by**: Scheduled Lambda function.
- **Input**: User email, task deadline.
- **Output**: Reminder notification sent to the user.

## AWS Services Used

- **API Gateway**: For defining and exposing RESTful endpoints to trigger Lambda functions.
- **Lambda**: For running backend logic, such as task management, user management, and notifications.
- **Cognito**: For user authentication and authorization.
- **DynamoDB**: For storing task and user data.
- **SNS**: For sending email and push notifications to users.

  ```

  ```

## Environment Variables

The following environment variables are required for some functions:

- `TASK_TABLE_NAME`: The name of the DynamoDB table for storing tasks.
- `USER_TABLE_NAME`: The name of the DynamoDB table for storing user data (optional for backup).
- `SNS_TOPIC_ARN`: The ARN for the SNS topic used for sending notifications.
- `COGNITO_USER_POOL_ID`: The ID of the Cognito User Pool.
- `COGNITO_APP_CLIENT_ID`: The ID of the Cognito App Client.
