import json,os
from lib import Player,Team

def readJson(filename: str):
    """Read in a Json file, and return its 
    metadata and a list of teams."""

    with open(filename,'r') as f:
        json_dict : dict = json.load(f)
    teams_dict : dict[str,dict] = json_dict['teams/groups']
    teams = []
    for team_name in teams_dict.keys(): # the overall Team
        t = Team(team_name)
        for player_name in teams_dict[team_name].keys(): # going through each player on the team
            t.add(Player(teams_dict[team_name][player_name],player_name)) # get and add player to Team.
        teams.append(t)
    
    return json_dict['metadata'] , teams


if __name__ == '__main__':
    # testing IO
    filename = "SeniorDesign/docs/FORMAT.json"
    result = readJson(filename)
    print(result[0])
    print(result[1])