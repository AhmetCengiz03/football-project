# Report

A Python script that creates an end of match report using statistics collected throughout the game and Open AI's Chat GPT 4.1 Nano model to create the summary text for the report. This report is then created as HTML and then converted into PDF so that it can be uploaded into an S3 bucket.

## Overview

### `report_data.py`
- This script gathers the required data for the entire report it makes a query to the AWS RDS database and gets the data for the relevant match using the match_id.

### `report_commentary.py`
- Using the data gathered from the `report_data.py` script the data is passed into a prompt for Chat GPT 4.1 Nano to analyse the flow of the game, giving an overview for the match, each half and the key events.

### `html_report.py`
- Creates the HTML for the report using the information from the AI response from `report_commentary.py`. 


### `report.py` 
- This converts the HTML to PDF. Then connects to the S3 bucket using `boto3` library, and uploads the PDF file. 

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
DB_NAME=<DATABASE NAME>
DB_HOST=<DATABASE HOST>
DB_USER=<DATABASE USERNAME>
DB_PASSWORD=<DATABASE PASSWORD>
DB_PORT=<DATABASE PORT>

OPENAI_API_KEY=<OPENAI API KEY>
S3_BUCKET=<S3 BUCKET NAME>
AWS_ACCESS_KEY_ID=<AWS ACCESS KEY ID>
AWS_SECRET_ACCESS_KEY=<AWS SECRET ACCESS KEY>
```

## AWS Lambda Deployment

The script is designed to run as an AWS Lambda function.

## Local Development

To run locally:

`python report.py`

Ensure your `.env` file contains all required environment variables.