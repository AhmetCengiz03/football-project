# Match Seeding Data Pipeline

This pipeline is responsible for extracting, validating, transforming, and loading master match data into a PostgreSQL RDS database


## extract_transform.py

Validates and transforms the incoming match event data.

### Key Functions:
- validate_required_values(): Ensures required top-level keys exist.
- validate_team_data(): Ensures exactly two teams are included.
- validate_timestamp(): Confirms the timestamp is in accepted UTC format.
- fetch_entity_name_from_api(): Uses the Sportmonks API to retrieve entity names (team, league, season).
- get_entity_name_if_exists(): Checks if an entity already exists in the DB.
- validate_and_transform_data(): Main entry point function to process the full dictionary.

Requires `.env` file containing:
- DB_NAME
- DB_USER
- DB_PASSWORD
- DB_HOST
- DB_PORT
- SPORTMONKS_API_TOKEN


## load_data.py

Loads the match data into the PostgreSQL database.

### Key Functions:

- insert_team(), insert_competition(), insert_season(), insert_match(), insert_match_assignment(): Inserts the data into their respective tables

- load_master_data(): Runs the entire load phase using the above functions.


## handler.py

This script is the entry point for the match data seeding pipeline, used by AWS Lambda to process and seed football match data into a PostgreSQL database.

### Key Steps

- Receives a match event (from a scheduler).
- Validates and checks if data exists already in the database regarding the match, if not retrieves missing data from the SportMonks API.
- Inserts the match, teams, competition, and season into your database (if they don't already exist)


### How to Run (manually):

- Ensure you have setup your `.env` file including the above credentials (see `extract_transform.py` info)
- Add an event dictionary in the `if __name__=="__main__"` block inside the `handler.py` file, along with `load_dotenv()` and call the functions like in the example below:
    - """
    if __name__ == "__main__":

        """
        load_dotenv()

        mock_event = {
            "match_id": 19367875,
            "league_id": 1034,
            "season_id": 25044,
            "fixture_name": "Gwangju vs Seoul",
            "start_time": "2025-06-13 10:30:00",
            "team_data": [
                {
                    "team_1_team_id": 4370,
                    "team_1_name": "Gwangju",
                    "team_1_code": None,
                    "team_1_image": "https://cdn.sportmonks.com/images/soccer/teams/18/4370.png",
                    "team_1_location": "home"
                },
                {
                    "team_2_team_id": 672,
                    "team_2_name": "Seoul",
                    "team_2_code": None,
                    "team_2_image": "https://cdn.sportmonks.com/images/soccer/teams/0/672.png",
                    "team_2_location": "away"
                }
            ]
        }
        transformed_data = validate_and_transform_data(mock_event)
        load_master_data(transformed_data)
        print("Match successfully seeded.")
        """

- Run `python3 handler.py`


 
