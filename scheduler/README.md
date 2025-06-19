# Fixture Scheduler

A Python script that automatically creates AWS EventBridge schedules for football matches happening the next day. The script fetches fixture data from the SportMonks API and creates individual schedules for each match.

## Overview

This scheduler runs daily to:
- Fetch tomorrow's football fixtures from SportMonks API
- Dynamically create AWS EventBridge schedules for each match
- Creates daily schedule groups with format: `{prefix}-{date}-fixtures`
- Keeps current day and tomorrow's groups
- Deletes older schedule groups to prevent accumulation- Schedule events to run during match times (with 3-hour maximum duration)

## Required Dependencies
- Create a virtual environment
    - `python -m venv .venv`
- Activate venv
    - On Mac/Linux
        - `source .venv/bin/activate`
    - On Windows
        - `.\.venv\Scripts\activate.bat`
- Install dependencies
    - `pip3 install -r requirements.txt`

## Environment Variables

Create a `.env` file or set the following environment variables:

```
AWS_ACCESS_KEY_ID=<your_aws_access_key>
AWS_SECRET_ACCESS_KEY=<your_aws_secret_key>
AWS_SESSION_TOKEN=<your_aws_session_token>
API_KEY=<your_sportmonks_api_key>
TARGET_ARN=<arn:aws:lambda:region:account:function:target-function>
ROLE_ARN=<arn:aws:iam::account:role/target-function-role>
```

## Configuration

The script uses the following configuration:
- **Schedule Prefix**: `c17-football` (can be modified in the lambda_handler)
- **Fixture Window**: Tomorrow's matches (UTC timezone)
- **Schedule Duration**: 3 hours per match
- **Schedule Expression**: `cron(* * * * ? *)` (every minute during match window)

## AWS Lambda Deployment

The script is designed to run as an AWS Lambda function.

## Local Development

To run locally:

`python scheduler.py

Ensure your `.env` file contains all required environment variables.
