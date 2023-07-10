# Valorant Stat Bot
A Valorant Discord bot designed to automate adding match data to a stats database.

## How It Works
The purpose of this bot is to assist in the stat collection of amateur tournament series.

The bot makes use of the [Unofficial Valorant API](https://github.com/Henrik-3/unofficial-valorant-api) provided by user Henrik-3, specifically it's 
[Python wrapper](https://github.com/raimannma/ValorantAPI) by user raimannma. While active, the bot takes a single match ID, name of team A and the
name of team B, then updates two csv files - one for individual player peformances (10 rows per map), and one for the maps itself. Each row on player
peformances contain data akin to what can be seen on websites such as tracker.gg, such as:

- Kills, Deaths, Assists
- ACS
- Headshot percentage
- Operator and judge kills per game
- Number of clutch situations (win or loss)

Once collected, this data can be aggregated for individual players, to see average stats across a season.

## To Be Implemented
Stats to be added:

- Sheriff vs Rifle winrate
- Thrifties
- Retake/postplant winrate
- Retake/postplant K/D
- 'True' FK/FD (untraded)

## Limitations
Can only fetch 'recent' matches though this threshold is unclear, from testing it seems matches more than 3 months ago can no longer be obtained.
