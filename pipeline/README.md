# Pipeline

## Setup

1) Create a `.env` and add the following keys:
```
TOKEN=[SPORTMONKS API TOKEN]
...
```

## Files

#### types_map_api.xlsx

The raw mapping file, containing `type_id`s as they are extracted and the statistic names.
This is pulled in inside `transform.py` to build the mapping to relate these to our database.

#### scrape_live_game.py

This file is used for scraping a live game to a series of json files.
They will be saved in a newly created subdirectory `match_{match_id}/`.
To start the process, simply run the script and change the `identify_match` variable to have a value matching the `match_id` from the api, or alternatively a team name (preference is to use match_id - it is more robust).