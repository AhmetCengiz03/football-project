# Stop Trigger

A Python script that gets passed a match id at the end of a game, using this match_id it manually deletes the specific schedule using the `boto3` library.

## Overview

This scheduler runs daily to:
- Get passed the match_id by the previous
- Finds schedule with format: `{prefix}-{match_id}-fixtures` and deletes them

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
```

## Configuration

The script uses the following configuration:
- **Schedule Prefix**: `c17-football` (can be modified in the lambda_handler)
- **Fixture Times**: (UTC timezone)

## AWS Lambda Deployment

The script is designed to run as an AWS Lambda function.

## Local Development

To run locally:

`python scheduler.py`

Ensure your `.env` file contains all required environment variables.

## Testing

To test this script run 

`pytest test_stop_trigger.py`

To see coverage use 

`pytest --cov stop_trigger`
