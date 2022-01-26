CREATE TABLE IF NOT EXISTS exp (
    UserID integer PRIMARY KEY,
    Elo integer DEFAULT 0,
    Level integer DEFAULT 0,
    EloTime text DEFAULT CURRENT_TIMESTAMP
);