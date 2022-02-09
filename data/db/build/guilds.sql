CREATE TABLE IF NOT EXISTS Guilds (
    GuildID integer PRIMARY KEY,
    Prefix varchar(3) DEFAULT '!',
    LogChannelID int,
    EloChannelID int,
    InfoChannelID int,
    ModChannelID int,
    NoURLChannelIDs text ,
    NoIMGChannelIDs text ,
    ReactChannelID int,
    RolesChannelID int,
    BotCatID int,
    LadderActive int DEFAULT 0
);

CREATE TABLE IF NOT EXISTS Admins (
    UserID integer PRIMARY KEY,
    rank int
)



