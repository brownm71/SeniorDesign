import json,os,time
from lib import Player,Team

def readJson(filename: str):
    """Read in a Json file, and return its 
    metadata and a list of teams."""

    with open(filename,'r') as f:
        json_dict : dict = json.load(f)
    teams_dict : dict[str,dict] = json_dict['teams/groups']
    teams = []
    teams : list[Team]
    for team_name in teams_dict.keys(): # the overall Team
        t = Team(team_name)
        for player_name in teams_dict[team_name].keys(): # going through each player on the team
            t.add(Player(teams_dict[team_name][player_name],player_name)) # get and add player to Team.
        teams.append(t)
    
    return json_dict['metadata'] , teams

def writeJson(filepath:str,teams : list[Team],metadata : dict):
    """Takes in teams, and metadata, and creates a new json
    or overwrites and existing file."""
    resultDict = {}
    resultDict['metadata'] = metadata
    teamDict = {}
    for team in teams:
        teamDict[team.name] = team.toDict()
    resultDict['teams/groups'] = teamDict
    with open(filepath,'w') as file:
        json.dump(resultDict,file,indent=4)

def combine_files(filenames: tuple[str,str],output_filename : str,fill = False,method = "Arithmetic",compress = False):
    """Take in files of the same game, and will combine all data between them, using the given method."""
    # read in files.
    meta,teams = readJson(filenames[0])
    meta2,teams2 = readJson(filenames[1])
    # TODO maybe compare meta to be sure they should be combined.
    if meta['game_ID'] != meta2['game_ID']:
        raise Exception("Files do not share a Game ID.")
    
    if method =='Arithmetic':
        for i in range(len(teams)):
            for j in range(len(teams[i].list_of_players)):
                teams[i].list_of_players[j].combine_arithmetic(teams2[i].list_of_players[j])
    if method =="Geometric":
        for i in range(len(teams)):
            for j in range(len(teams[i].list_of_players)):
                teams[i].list_of_players[j].combine_geometric(teams2[i].list_of_players[j])
    
    
    
    if fill:
        # we need to interpolate.
        for team in teams:
            for player in team.list_of_players:
                player.basicInterpolateFill(float(meta['time_step']))

    meta['date'] = f'{time.localtime()[1]}/{time.localtime()[2]}/{time.localtime()[0]}' # Cursed way to change the metaData Time
    # print(meta)

    writeJson(output_filename,teams,meta)



if __name__ == '__main__':
    # testing IO
    filename = "SeniorDesign/docs/singleTeamTest.json"
    metaData,teams = readJson(filename)
    print(metaData)
    print(teams)

    fileOutName = 'TestOut.json'
    writeJson(fileOutName,teams,metaData)