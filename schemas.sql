/*
==================================================
Creating databse tables which will be used in the backend
==================================================
*/

CREATE TABLE [Cafe_Player](
    player_id INTEGER PRIMARY KEY,
    player_name VARCHAR(50) NOT NULL,
    player_type VARCHAR(100) NOT NULL,
    CONSTRAINT confirm_player_type CHECK (
        player_type = 'Casual Drop-In'
        OR
        player_type = 'League Regular'
        OR
        player_type = 'Tournament Competitor'
    ),
    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    current_elo INTEGER NOT NULL DEFAULT 1000,
    updated_at_cafe_player TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
);
/*
Create trigger for updated_at in order to automatically update the attribute.
This is whenever any changes is made to a specific Players entry
*/
CREATE TRIGGER updated_at
AFTER UPDATE ON Cafe_Player
BEGIN
    UPDATE Cafe_Player
    SET updated_at_cafe_player = CURRENT_TIMESTAMP
    WHERE player_id = NEW.player_id;
END; 

/*
Event table for all events (type, game_title, capacity and time) within the cafe
*/

CREATE TABLE [Cafe_Event](
    event_id INTEGER PRIMARY KEY,
    event_name VARCHAR(100) NOT NULL UNIQUE,
    event_type VARCHAR(100) NOT NULL,
    CONSTRAINT confirm_event_type CHECK (
        event_type = 'Open Game Night'
        OR
        event_type = 'Ranked League Match'
        OR 
        event_type = 'Tournament Match'
    ),
    game_title VARCHAR(100) NOT NULL,
    event_capacity INTEGER NOT NULL,
    CONSTRAINT max_event_capacity CHECK (
        event_capacity > 0 AND event_capacity <= 100
    ),
    event_date TEXT NOT NULL, /* TEXT is SQLLite equivalent of DATE */
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at_cafe_event TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
);

CREATE TRIGGER updated_at_cafe_event 
AFTER UPDATE ON Cafe_Event
BEGIN
    UPDATE Cafe_Event
    SET updated_at_cafe_event = CURRENT_TIMESTAMP
    WHERE event_id = NEW.event_id;
END; 

/* 
Match table to see match times 
*/
CREATE TABLE [Cafe_Match] (
    match_id INTEGER PRIMARY KEY,
    event_id INTEGER NOT NULL,
    FOREIGN KEY (event_id) REFERENCES Cafe_Event(event_id) ON DELETE CASCADE,
    schedule_match_time DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at_cafe_match TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
);

CREATE TRIGGER updated_at_cafe_match
AFTER UPDATE ON Cafe_Match
BEGIN
    UPDATE Cafe_Match
    SET updated_at_cafe_match = CURRENT_TIMESTAMP
    WHERE match_id = NEW.match_id;
END; 

/*
Juncture table of many-to-many players and matches relationship.
Results are also listed in this table from 1st to 8th place
*/

CREATE TABLE [Cafe_Match_Players] (
    player_id INT NOT NULL,
    match_id INT NOT NULL,
    PRIMARY KEY(player_id, match_id),
    FOREIGN KEY (player_id) REFERENCES Cafe_Player(player_id) ON DELETE CASCADE,
    FOREIGN KEY (match_id) REFERENCES Cafe_Match(match_id) ON DELETE CASCADE,
    match_result VARCHAR(100),
    CONSTRAINT confirm_match_result CHECK (
        match_result = '1st Place'
        OR
        match_result = '2nd Place'
        OR 
        match_result = '3rd Place'
        OR 
        match_result = '4th Place'
        OR
        match_result = '5th Place'
        OR
        match_result = '6th Place'
        OR 
        match_result = '7th Place'
        OR 
        match_result = '8th Place'
    ),
    attendance VARCHAR(100) NOT NULL,
    CONSTRAINT confirm_attendance CHECK (
        attendance = 'Attended'
        OR
        attendance = 'No-Show'
        OR attendance = 'Cancelled'
    ),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at_cafe_match_players TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
);

CREATE TRIGGER updated_at_cafe_match_players
AFTER UPDATE ON Cafe_Match_Players
BEGIN 
    UPDATE Cafe_Match_Players
    SET updated_at_cafe_match_players = CURRENT_TIMESTAMP
    WHERE player_id = NEW.player_id AND match_id = NEW.match_id;  
END;
