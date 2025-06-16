DROP TABLE IF EXISTS player_match_event;
DROP TABLE IF EXISTS player;
DROP TABLE IF EXISTS match_event;
DROP TABLE IF EXISTS match_minute_stats;
DROP TABLE IF EXISTS event_type;
DROP TABLE IF EXISTS match_assignment;
DROP TABLE IF EXISTS match;
DROP TABLE IF EXISTS season;
DROP TABLE IF EXISTS competition;
DROP TABLE IF EXISTS team;

CREATE TABLE team (
    team_id INT NOT NULL,
    team_name VARCHAR(50) NOT NULL,
    team_code VARCHAR(10),
    logo_url TEXT,
    PRIMARY KEY (team_id)
);

CREATE TABLE competition (
    competition_id INT NOT NULL,
    competition_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (competition_id)
);

CREATE TABLE season (
    season_id INT NOT NULL,
    season_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (season_id)
);

CREATE TABLE match (
    match_id INT NOT NULL,
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
    event_type_id SMALLINT NOT NULL,
    type_name VARCHAR(50),
    PRIMARY KEY (event_type_id)
);

CREATE TABLE match_minute_stats (
    match_minute_stats_id INT GENERATED ALWAYS AS IDENTITY,
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
    big_chances_created_home SMALLINT,
    big_chances_created_away SMALLINT,
    big_chances_missed_home SMALLINT,
    big_chances_missed_away SMALLINT,
    successful_dribbles_home SMALLINT,
    successful_dribbles_away SMALLINT,
    dribbled_attempts_home SMALLINT,
    dribbled_attempts_away SMALLINT,
    duels_won_home SMALLINT,
    duels_won_away SMALLINT,
    free_kicks_home SMALLINT,
    free_kicks_away SMALLINT,
    interceptions_home SMALLINT,
    interceptions_away SMALLINT,
    offsides_home SMALLINT,
    offsides_away SMALLINT,
    shots_blocked_home SMALLINT, 
    shots_blocked_away SMALLINT, 
    successful_headers_home SMALLINT,
    successful_headers_away SMALLINT,
    total_crosses_home SMALLINT,
    total_crosses_away SMALLINT,
    PRIMARY KEY (match_minute_stats_id),
    FOREIGN KEY (match_id) REFERENCES match(match_id),
    CONSTRAINT valid_half_value CHECK (half IN (1,2,3,4,5))
);

CREATE TABLE match_event (
    match_event_id INT NOT NULL,
    match_minute_stats_id INT NOT NULL,
    event_type_id SMALLINT,
    team_id INT,
    PRIMARY KEY (match_event_id),
    FOREIGN KEY (match_minute_stats_id) REFERENCES match_minute_stats(match_minute_stats_id) ON DELETE CASCADE,
    FOREIGN KEY (event_type_id) REFERENCES event_type(event_type_id),
    FOREIGN KEY (team_id) REFERENCES team(team_id)
);

CREATE TABLE player (
    player_id INT NOT NULL,
    player_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (player_id)
);

CREATE TABLE player_match_event (
    player_match_event_id INT GENERATED ALWAYS AS IDENTITY,
    player_id INT NOT NULL,
    related_player_id INT,
    match_event_id INT NOT NULL,
    PRIMARY KEY (player_match_event_id),
    FOREIGN KEY (player_id) REFERENCES player(player_id),
    FOREIGN KEY (related_player_id) REFERENCES player(player_id),
    FOREIGN KEY (match_event_id) REFERENCES match_event(match_event_id) ON DELETE CASCADE,
    CONSTRAINT unique_event UNIQUE (match_event_id, player_id)
);

INSERT INTO event_type (event_type_id, type_name) VALUES
(10, 'var'),
(14, 'goal'),
(15, 'owngoal'),
(16, 'penalty'),
(17, 'missed_penalty'),
(18, 'substitution'),
(19, 'yellowcard'),
(20, 'redcard');