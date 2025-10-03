import json as j
players = {"Senzu":"Mongolz", "Techno4K":"Mongolz", "910":"Mongolz",
           "Mzinho":"Mongolz", "bLitz":"Mongolz", "rain":"Faze", "broky":"Faze",
           "jcobbb":"Faze", "karrigan":"Faze", "frozen":"Faze"}
with open('jim.csv',"r") as f:
    lines = f.readlines()

Mongolz = {}
Faze = {}

for i in range(lines.__len__()):
    doTing = False
    if (lines[i].split(",")[0] == "Name"):
        name = lines[i].split(",")[1].removesuffix('\n')
    elif (lines[i].split(",")[0] == "X"):
        X = float(lines[i].split(",")[1].removesuffix('\n'))
    elif (lines[i].split(",")[0] == "Y"):
        Y = float(lines[i].split(",")[1].removesuffix('\n'))
    elif (lines[i].split(",")[0] == "Tick"):
        tick = int(lines[i].split(",")[1].removesuffix('\n'))
        doTing = True
    else:
        print(lines[i])
    if (doTing):
        if (players[name] == "Mongolz"):
            if not Mongolz.get(name):
                Mongolz[name] = {}
            Mongolz[name][tick / 64] = [{
                'LOCATION':[X,Y],
                'CONFIDENCE':1,
                'NUMPOINTS':1
            }]
        elif (players[name] == "Faze"):
            if not Faze.get(name):
                Faze[name] = {}
            Faze[name][tick / 64] = [{
                'LOCATION':[X,Y],
                'CONFIDENCE':1,
                'NUMPOINTS':1
            }]
teamDict = {
    "Mongolz":Mongolz,
    "Faze":Faze
}
topDict = {
    "Metadata": {
        "version":0.0,
        "game_ID" : "its a game!",
        "date" : "50/50/99",
        "time_step" : "1"
    },
    "teams/groups": teamDict
}
with open("jimJson.json",  "w") as f:
    j.dump(topDict, f, indent=4)

