import numpy as np
import pandas as pd

## For a given match_id, generate a match_dict for performances

def get_performance_data(match_response):
    
    ## Calculate location in the kill list
    kill_ctr = 0 
    
    j = 0
    
    match_dict = {}

    for player in match_response.players.all_players:

        try:
            headshot_percentage = 100 * player.stats.headshots / (player.stats.headshots + player.stats.bodyshots + player.stats.legshots)
        except ZeroDivisionError:
            headshot_percentage = 0
    
        
        player_dict = {"Name": player.name,
                       "Agent": player.character,
                       "ACS": player.stats.score / match_response.metadata.rounds_played,
                       "Kills": player.stats.kills,
                       "Deaths": player.stats.deaths,
                       "Assists": player.stats.assists,
                       "KAST": 0,
                       "ADR": player.damage_made / match_response.metadata.rounds_played,
                       "HS%": headshot_percentage,
                       "FK": 0,
                       "FD": 0,
                       "Team": player.team,
                       "Judge Kills": 0,
                       "OP Kills": 0,
                       "1v2s":0,
                       "1v2s won":0,
                       "1v3s":0,
                       "1v3s won":0,
                       "1v4s":0,
                       "1v4s won":0,
                       #"1v5s":0,
                       #"1v5s won":0,
                       "Match ID": match_response.metadata.matchid}

        match_dict[player.puuid] = player_dict

    ## Calculating first deaths / first kills / KAST

    for rd in match_response.rounds:
        
        earliest_kill_time = 10000000

        kill_events = []
        
        j += 1
        
        for player in rd.player_stats:

            for kill_event in player.kill_events: 

                kill_events.append(kill_event)

                ## Identify FK / FD

                if kill_event.kill_time_in_round < earliest_kill_time:

                    earliest_kill_time = kill_event.kill_time_in_round
                    first_killer = kill_event.killer_puuid
                    first_victim = kill_event.victim_puuid
                    
                ## Calculate Operator
                if kill_event.damage_weapon_name == 'Operator':
                    match_dict[kill_event.killer_puuid]['OP Kills'] += 1
                    
                 ## Calculate judge kills
                if kill_event.damage_weapon_name == 'Judge':
                    match_dict[kill_event.killer_puuid]['Judge Kills'] += 1
            
        clutch_player = None
        clutch_case = 'Undecided'
        
        ## here we are using match_response.kills because it is ordered correctly: 
        
        ## Red team alive
        red_team = match_response.players.red.copy()
        
        # Blue team alive
        blue_team = match_response.players.blue.copy()
        
        for i in range(len(kill_events)):
            
            kill_event = match_response.kills[kill_ctr]
            kill_ctr += 1
            
            if kill_event.victim_team == 'Blue':
                
                    ## Loop through current blue team members
                for player in blue_team:
                        
                    ## If member ID matches victim ID
                    if player.puuid == kill_event.victim_puuid:
                        ## Remove victim from living members
                        blue_team.remove(player)
            else:
                for player in red_team:
                        
                    ## If member ID matches victim ID
                    if player.puuid == kill_event.victim_puuid:
                        ## Remove victim from living members
                        red_team.remove(player)
                    
                ## Check if Blue team only has one survivor at this point
                
            if len(blue_team) == 1 and clutch_case == 'Undecided':
                clutch_case = f'1v{len(red_team)}'
                clutch_player = blue_team[0]
                match_dict[clutch_player.puuid]


            if len(red_team) == 1 and clutch_case == 'Undecided':
                clutch_case = f'1v{len(blue_team)}'
                clutch_player = red_team[0]
        
        ## Check if the team clutched the round
        if clutch_player != None:
             
            if clutch_case == '1v2':
                match_dict[clutch_player.puuid]['1v2s'] += 1
                match_dict[clutch_player.puuid]['1v2s won'] += (clutch_player.team == rd.winning_team)
                    
            if clutch_case == '1v3':
                match_dict[clutch_player.puuid]['1v3s'] += 1
                match_dict[clutch_player.puuid]['1v3s won'] += (clutch_player.team == rd.winning_team)
                    
            if clutch_case == '1v4':
                match_dict[clutch_player.puuid]['1v4s'] += 1
                match_dict[clutch_player.puuid]['1v4s won'] += (clutch_player.team == rd.winning_team)
                        

        for player in rd.player_stats: ## Checking for KAST

            KAST = False
            survived = True

            if player.kills > 0: ## If player has kills:
                KAST = True

            for kill_event in kill_events: ## Check if player has assists

                for assistant in kill_event.assistants:
                    if player.player_puuid == assistant.assistant_puuid:
                        KAST = True
                        break

            for kill_event in kill_events: ## Identify the player's killer

                if kill_event.victim_puuid == player.player_puuid:

                    survived = False

                    killer = kill_event.killer_puuid
                    killtime = kill_event.kill_time_in_round

                    for kill_event in kill_events: ## Check if that killer got killed 5 seconds after the time
                        if (kill_event.victim_puuid == killer and kill_event.kill_time_in_round < killtime + 5000):
                            KAST = True

            if survived:
                KAST = True

            if KAST:
                match_dict[player.player_puuid]['KAST'] += 1 / match_response.metadata.rounds_played



        ## Update player dictionary with FK / FD information

        match_dict[first_killer]['FK'] += 1
        match_dict[first_victim]['FD'] += 1
        
        ## Check if the team won the round with man advantage
   
    return match_dict

def get_match_data(match_response):

    match_dict = {
        "Match ID": match_response.metadata.matchid,
        "Map": match_response.metadata.map,
        "Total Rounds": match_response.metadata.rounds_played,
        "Team Blue Rounds": match_response.teams.blue.rounds_won,
        "Team Red Rounds": match_response.teams.red.rounds_won,
        "Team Blue Win?": match_response.teams.blue.has_won,
        "Team Blue Attack Rounds":0,
        "Team Blue Defense Rounds":0,
        "Team Red Attack Rounds":0,
        "Team Red Defense Rounds":0,
        "Team Blue 5v4s":0,
        "Team Blue 4v5s":0,
        "Team Blue 5v4s won":0,
        "Team Blue 4v5s won":0,
        "Team Red 5v4s":0,
        "Team Red 4v5s":0,
        "Team Red 5v4s won":0,
        "Team Red 4v5s won":0
    }
    
    ## From the API, red team always starts on attack
    
    for count, rnd in enumerate(match_response.rounds):
        
        if count < 12: ## For the first half, red team is attackers
            if rnd.winning_team == 'Red':
                match_dict['Team Red Attack Rounds'] += 1
            else:
                match_dict['Team Blue Defense Rounds'] += 1
        else:
            if rnd.winning_team == 'Red':
                match_dict['Team Red Defense Rounds'] += 1
            else:
                match_dict['Team Blue Attack Rounds'] += 1
                
                
        ## Identify which team secured first kill - and see if they convered it
        
        earliest_kill_time = 10000000
        kill_events = []

        for player in rnd.player_stats:

            for kill_event in player.kill_events: 
                
                kill_events.append(kill_event)
                
                if kill_event.kill_time_in_round < earliest_kill_time:

                    earliest_kill_time = kill_event.kill_time_in_round
                    fk_team = kill_event.killer_team
                
        if fk_team == 'Blue':    
            match_dict['Team Blue 5v4s'] += 1
            match_dict['Team Red 4v5s'] += 1    
            
            if rnd.winning_team == 'Blue':
                match_dict['Team Blue 5v4s won'] += 1
            else:
                match_dict['Team Red 4v5s won'] += 1
        
        else:
            match_dict['Team Blue 4v5s'] += 1
            match_dict['Team Red 5v4s'] += 1    
            
            if rnd.winning_team == 'Blue':
                match_dict['Team Blue 4v5s won'] += 1
            else:
                match_dict['Team Red 5v4s won'] += 1
        
    return match_dict


def clean_performance_df(match_response, team_blue, team_red): 
    
    ## Extract performance data and place it into a dataframe
    df = pd.DataFrame.from_dict(get_performance_data(match_response), orient='index')
    df.index = df.index.set_names('player_id')
    
    ## Rename 'blue' and 'red' to proper team names
    
    df['Team'] = df['Team'].apply(lambda x: team_blue if x == 'Blue' else team_red)
    
    ## Conver KAST to percentage
    
    df['KAST'] = df['KAST'] * 100
    
    ## Round
    
    df = df.round(1)
    
    ## Write down performance data
    df.to_csv('data/performances.csv', mode='a', header=False)


def clean_match_df(match_response, team_blue, team_red):
    
    ## Get dict
    match_dict = get_match_data(match_response)
    
    ## Data cleaning
    match_dict['Team Red'] = team_red
    match_dict['Team Blue'] = team_blue
    match_dict['Winner'] = team_blue if match_dict['Team Blue Win?'] else team_red
    match_dict.pop('Team Blue Win?')
    
    ## Write general match data to CSV
      
    with open('data/maps.csv', 'a') as csv_file:  
        
        for key, value in match_dict.items():
        
            csv_file.write(f"{str(value)},")
        csv_file.write("\n")
    
