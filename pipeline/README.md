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