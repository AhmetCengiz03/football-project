DROP TABLE IF EXISTS match_event;
DROP TABLE IF EXISTS match_minute_stats;
DROP TABLE IF EXISTS event_type;
DROP TABLE IF EXISTS match_assignment;
DROP TABLE IF EXISTS match;
DROP TABLE IF EXISTS season;
DROP TABLE IF EXISTS competition;
DROP TABLE IF EXISTS team;

CREATE TABLE team (
    team_id SMALLINT,
    team_name VARCHAR(50) NOT NULL,
    logo_url TEXT NOT NULL,
    PRIMARY KEY (team_id)
);

CREATE TABLE competition (
    competition_id SMALLINT,
    competition_name VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (competition_id)
);

CREATE TABLE season (
    season_id SMALLINT,
    season_name VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (season_id)
);

CREATE TABLE match (
    match_id INT,
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
    FOREIGN KEY (match_id) REFERENCES match(match_id),
    FOREIGN KEY (competition_id) REFERENCES competition(competition_id),
    FOREIGN KEY (season_id) REFERENCES season(season_id)  
);

CREATE TABLE event_type (
    event_type_id SMALLINT NOT NULL UNIQUE,
    type_name VARCHAR(50),
    type_description VARCHAR(100),
    PRIMARY KEY (event_type_id)
);

CREATE TABLE match_minute_stats (
    minute_stat_id INT GENERATED ALWAYS AS IDENTITY,
    match_id INT NOT NULL,
    match_minute SMALLINT,
    half SMALLINT,
    possession_home SMALLINT,
    shots_home SMALLINT,
    shots_away SMALLINT,
    shots_on_target_home SMALLINT,
    shots_on_target_away SMALLINT,
    fouls_home SMALLINT,
    fouls_away SMALLINT,
    corners_home SMALLINT,
    corners_away SMALLINT,
    tackles_home SMALLINT,
    tackles_away SMALLINT,
    attacks_home SMALLINT,
    attacks_away SMALLINT,
    danger_attacks_home SMALLINT,
    danger_attacks_away SMALLINT,
    shots_outside_home SMALLINT,
    shots_outside_away SMALLINT,
    shots_inside_home SMALLINT,
    shots_inside_away SMALLINT, 
    hit_woodwork_home SMALLINT,
    hit_woodwork_away SMALLINT,
    passes_home SMALLINT,
    passes_away SMALLINT,
    successful_passes_home SMALLINT,
    successful_passes_away SMALLINT,
    key_passes_home SMALLINT,
    key_passes_away SMALLINT,
    saves_home SMALLINT,
    saves_away SMALLINT,
    offsides_home SMALLINT,
    offsides_away SMALLINT,
    PRIMARY KEY (minute_stat_id),
    FOREIGN KEY (match_id) REFERENCES match(match_id),
    CONSTRAINT valid_half_value CHECK (half IN (1,2))
);

CREATE TABLE match_event (
    match_event_id INT GENERATED ALWAYS AS IDENTITY,
    minute_stat_id INT NOT NULL,
    event_type_id INT,
    event_description TEXT,
    PRIMARY KEY (match_event_id),
    FOREIGN KEY (minute_stat_id) REFERENCES match_minute_stats(minute_stat_id),
    FOREIGN KEY (event_type_id) REFERENCES event_type(event_type_id)
);


INSERT INTO event_type (event_type_id, type_name, type_description) 
VALUES (1, 'home_goal', 'Goal scored by home team'),
    (2, 'away_goal', 'Goal scored by away team'),
    (3, 'home_yellow', 'Yellow card for home team player'),
    (4, 'away_yellow', 'Yellow card for away team player'),
    (5, 'home_red', 'Red card for home team player'),
    (6, 'away_red', 'Red card for away team player'),
    (7, 'home_sub', 'Substitution for home team player'),
    (8, 'away_sub', 'Substitution for away team player'),
    (9, 'home_penalty_goal', 'Penalty goal by home team player'),
    (10, 'away_penalty_goal', 'Penalty goal by away team player');
