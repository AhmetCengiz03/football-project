# Pipeline

An ETL pipeline that is can be triggered each minute throughout a match. The data is extracted from the [Sportmonks API](https://www.sportmonks.com/football-api/). Data is then transformed and uploaded into an AWS RDS instance. 

## Overview

### `extract.py`
- Connects to the API, extracts `statistics`, `periods` and `events` data from the `livescores` end point. Removes unnecessary keys to avoid collecting redundant data and passes this. 


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
BASE_URL=<API_BASE_URL>
DB_HOST=<DATABASE_HOST>
DB_NAME=<DATABASE_NAME>
DB_PASS=<DATABASE_PASSWORD>
DB_PORT=<DATABASE_PORT>
DB_USER=<DATABASE_USERNAME>
TOKEN=<SPORTMONKS API TOKEN?
```

## Files

#### `types_map_api.xlsx`

The raw mapping file, containing `type_id`s as they are extracted and the statistic names.
This is pulled in inside `transform.py` to build the mapping to relate these to our database.

#### `scrape_live_game.py`

This file is used for scraping a live game to a series of json files.
They will be saved in a newly created subdirectory `match_{match_id}/`.
To start the process, simply run the script and change the `identify_match` variable to have a value matching the `match_id` from the api, or alternatively a team name (preference is to use match_id - it is more robust).

## AWS Lambda Deployment

The script is designed to run as an AWS Lambda function.

## Local Development

To run locally:

`python extract.py`

Ensure your `.env` file contains all required environment variables.