DROP TABLE IF EXISTS match_;
DROP TABLE IF EXISTS match_minute_stats;
DROP TABLE IF EXISTS even_types;
DROP TABLE IF EXISTS match_event;
DROP TABLE IF EXISTS team;
DROP TABLE IF EXISTS competition_assignment;
DROP TABLE IF EXISTS competition;
DROP TABLE IF EXISTS season;

CREATE TABLE team (
    team_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    team_name VARCHAR(50) NOT NULL,
    PRIMARY KEY (team_id)
);

CREATE TABLE competition (
    competition_id SMALLINT GENERATED ALWAYS AS IDENTITY,
    competition_name VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (competition_id)
);

CREATE TABLE season (
    season_id SMALLINT NOT NULL,
    season_name VARCHAR(10) NOT NULL UNIQUE,
    PRIMARY KEY (season_id),
);

CREATE TABLE match (
    match_id INT NOT NULL,
    home_team_id INT NOT NULL,
    away_team_id INT NOT NULL,
    competition_id INT NOT NULL,
    match_date TIMESTAMP,
    PRIMARY KEY (match_id),
    FOREIGN KEY (home_team_id) REFERENCES team(team_id),
    FOREIGN KEY (away_team_id) REFERENCES team(away_team_id),
    FOREIGN KEY (competition_id) REFERENCES competition(competition_id)
);
