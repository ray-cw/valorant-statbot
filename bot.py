import os

# For discord bot
import discord
from dotenv import load_dotenv
from discord import app_commands

import valo_api as vapi

import numpy as np
import pandas as pd

from helper.datacollection import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name = "add-match", description = "Add match to database.", guild=discord.Object(id=GUILD_ID)) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def add_match(interaction, match_id: str, team_a: str, team_b: str, week: str):

    await interaction.response.send_message(f"Looking up [{match_id}]...")

    ## Check for duplicates in the database first
    maps_df = pd.read_csv('data/maps.csv',usecols=[0],names=['match_id'],header=None)

    if maps_df['match_id'].str.contains(match_id).any():
        await interaction.followup.send(f"Match exists in database, termininating operation.")
        return

    ## Fetch match
    try:
        match_response = vapi.get_match_details_v2(match_id)
    except: ## Case of error
        await interaction.followup.send(f"Valorant API Error: Match not found, terminating operation.")
        return

    clean_match_df(match_response, team_b, team_a, week)
    clean_performance_df(match_response, team_b, team_a, week)

    await interaction.followup.send(f"Added match [{match_id}] between {team_a} and {team_b} to database.")

@tree.command(name = "delete-match", description = "Remove match from database.", guild=discord.Object(id=GUILD_ID)) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def delete_match(interaction, match_id: str):

    await interaction.response.send_message(f"Looking up [{match_id}]...")

    ## Check if match exists in database.
    maps_df = pd.read_csv('data/maps.csv',usecols=[0],names=['match_id'],header=None)

    if not maps_df['match_id'].str.contains(match_id).any():
        await interaction.followup.send(f"Match does not exist in database, termininating operation.")
        return

    remove_match(match_id)

    await interaction.followup.send(f"Removed match [{match_id}] from database.")


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f'{client.user} has connected to Discord server!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if 'statbot' in message.content.lower():
        await message.channel.send("Hi, I'm not ready yet so give me some time!")

 

client.run(TOKEN)