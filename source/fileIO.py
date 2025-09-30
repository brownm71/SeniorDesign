import json,os,time
from lib import Player,Team,Teams_and_Meta

def readJson(filename: str):
    """Read in a Json file, and return a  
    team_and_meta object."""

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
    
    return Teams_and_Meta(teams,json_dict['metadata'])

def writeJson(filepath:str,fileformat : Teams_and_Meta):
    """Takes in teams, and metadata, and creates a new json
    or overwrites and existing file."""
    resultDict = {}
    resultDict['metadata'] = fileformat.meta
    teamDict = {}
    for team in fileformat.teams:
        teamDict[team.name] = team.toDict()
    resultDict['teams/groups'] = teamDict
    with open(filepath,'w') as file:
        json.dump(resultDict,file,indent=4)

def combine_files(filenames: tuple[str,str],output_filename : str,fill = False,method = "Arithmetic",compress = False):
    """Take in files of the same game, and will combine all data between them, using the given method."""
    # read in files.
    file1 = readJson(filenames[0])
    file2 = readJson(filenames[1])
    # TODO maybe compare meta to be sure they should be combined.
    if file1.meta['game_ID'] != file2.meta['game_ID']:
        raise Exception("Files do not share a Game ID.")
    
    if method =='Arithmetic':
        for i in range(len(file1.teams)):
            for j in range(len(file1.teams[i].list_of_players)):
                file1.teams[i].list_of_players[j].combine_arithmetic(file2.teams[i].list_of_players[j])
    if method =="Geometric":
        for i in range(len(file1.teams)):
            for j in range(len(file1.teams[i].list_of_players)):
                file1.teams[i].list_of_players[j].combine_geometric(file2.teams[i].list_of_players[j])
    
    
    
    if fill:
        # we need to interpolate.
        for team in file1.teams:
            for player in team.list_of_players:
                player.basicInterpolateFill(float(file1.meta['time_step']))

    file1.meta['date'] = f'{time.localtime()[1]}/{time.localtime()[2]}/{time.localtime()[0]}' # Cursed way to change the metaData Time
    # print(meta)

    writeJson(output_filename,file1)



if __name__ == '__main__':
    # testing IO
    filename = "SeniorDesign/docs/singleTeamTest.json"
    file1 = readJson(filename)

    fileOutName = 'TestOut.json'
    writeJson(fileOutName,file1)