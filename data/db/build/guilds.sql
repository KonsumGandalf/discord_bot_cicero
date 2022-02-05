CREATE TABLE IF NOT EXISTS Guilds (
    GuildID integer PRIMARY KEY,
    Prefix varchar(3) DEFAULT '!',
    LogChannelID int,
    ModChannelID int,
    NoURLChannelIDs text
);



