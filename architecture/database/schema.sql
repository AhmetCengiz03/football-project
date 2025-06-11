DROP TABLE IF EXISTS match_event;
DROP TABLE IF EXISTS match_minute_stats;
DROP TABLE IF EXISTS event_type;
DROP TABLE IF EXISTS match_assignment;
DROP TABLE IF EXISTS match_;
DROP TABLE IF EXISTS season;
DROP TABLE IF EXISTS competition;
DROP TABLE IF EXISTS team;

CREATE TABLE team (
    team_id INT GENERATED ALWAYS AS IDENTITY,
    team_name VARCHAR(50) NOT NULL,
    logo_url TEXT NOT NULL,
    PRIMARY KEY (team_id)
);

CREATE TABLE competition (
    competition_id INT GENERATED ALWAYS AS IDENTITY,
    competition_name VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (competition_id)
);

CREATE TABLE season (
    season_id INT NOT NULL,
    season_name VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (season_id)
);

CREATE TABLE match_ (
    match_id INT GENERATED ALWAYS AS IDENTITY,
    home_team_id INT NOT NULL,
    away_team_id INT NOT NULL,
    match_date TIMESTAMP,
    PRIMARY KEY (match_id),
    FOREIGN KEY (home_team_id) REFERENCES team(team_id),
    FOREIGN KEY (away_team_id) REFERENCES team(team_id)
);

CREATE TABLE match_assignment (
    match_assignment_id INT GENERATED ALWAYS AS IDENTITY,
    match_id INT NOT NULL,
    competition_id INT NOT NULL,
    season_id INT NOT NULL,
    PRIMARY KEY (match_assignment_id),
    FOREIGN KEY (match_id) REFERENCES match_(match_id),
    FOREIGN KEY (competition_id) REFERENCES competition(competition_id),
    FOREIGN KEY (season_id) REFERENCES season(season_id)
    
);

CREATE TABLE event_type (
    event_type_id INT GENERATED ALWAYS AS IDENTITY,
    type_name VARCHAR(50),
    type_description VARCHAR(100),
    PRIMARY KEY (event_type_id)
);

CREATE TABLE match_minute_stats (
    minute_stat_id INT GENERATED ALWAYS AS IDENTITY,
    match_id INT NOT NULL,
    match_minute INT,
    half INT,
    possession_home INT,
    shots_home INT,
    shots_away INT,
    shots_on_target_home INT,
    shots_on_target_away INT,
    fouls_home INT,
    fouls_away INT,
    corners_home INT,
    corners_away INT,
    tackles_home INT,
    tackles_away INT,
    attacks_home INT,
    attacks_away INT,
    danger_attacks_home INT,
    danger_attacks_away INT,
    shots_outside_home INT,
    shots_outside_away INT,
    shots_inside_home INT,
    shots_inside_away INT, 
    hit_woodwork_home INT,
    hit_woodwork_away INT,
    passes_home INT,
    passes_away INT,
    successful_passes_home INT,
    successful_passes_away INT,
    key_passes_home INT,
    key_passes_away INT,
    saves_home INT,
    saves_away INT,
    offsides_home INT,
    offsides_away INT,
    PRIMARY KEY (minute_stat_id),
    FOREIGN KEY (match_id) REFERENCES match_(match_id)
);

CREATE TABLE match_event (
    match_event_id INT GENERATED ALWAYS AS IDENTITY,
    minute_stat_id INT NOT NULL,
    event_type_id INT NOT NULL,
    event_description TEXT NOT NULL,
    PRIMARY KEY (match_event_id),
    FOREIGN KEY (minute_stat_id) REFERENCES match_minute_stats(minute_stat_id),
    FOREIGN KEY (event_type_id) REFERENCES event_type(event_type_id)
);
