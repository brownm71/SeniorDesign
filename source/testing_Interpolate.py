import time
from lib import *
from fileIO import *
file1 = readJson("SeniorDesign/docs/singleTeamTest.json")
# print(teams)
teams : list[Team]
for team in file1.teams:
    for player in team.list_of_players:
        # print(player.times_to_pos)
        player.basicInterpolateFill(1)
        # print((player.times_to_pos))

file1.meta['date'] = f'{time.localtime()[1]}/{time.localtime()[2]}/{time.localtime()[0]}' # Cursed way to change the metaData Time
# print(meta)
writeJson('TestOut.json',file1)
