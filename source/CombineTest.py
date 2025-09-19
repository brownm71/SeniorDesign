import time
from lib import *
from fileRead import *
meta,teams = readJson("SeniorDesign/docs/singleTeamTest.json")
meta2,teams2 = readJson("SeniorDesign/docs/singleTeamTest2.json")
# print(teams)
teams : list[Team]
teams2 : list[Team]
for i in range(len(teams)):
    for j in range(len(teams[i].list_of_players)):
        teams[i].list_of_players[j].combine(teams2[i].list_of_players[j])

meta['date'] = f'{time.localtime()[1]}/{time.localtime()[2]}/{time.localtime()[0]}' # Cursed way to change the metaData Time
# print(meta)
writeJson('TestOut.json',teams,meta)