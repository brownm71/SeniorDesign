import matplotlib.pyplot as plt
from fileIO import *
from flaw import *


def std_div_check(actual : Teams_and_Meta, constructed : Teams_and_Meta):
    res = {}
    count = 0
    for i in range(len(actual.teams)):
        for j in range(len(actual.teams[i].list_of_players)):
            for time in actual.teams[i].list_of_players[j].times_to_pos.keys():
                ax,ay = actual.teams[i].list_of_players[j].times_to_pos[time][0]['LOCATION']
                cx, cy = constructed.teams[i].list_of_players[j].times_to_pos[time][0]['LOCATION']
                # stdDiv = constructed.teams[i].list_of_players[j].times_to_pos[time][0]['SD']
                stdDiv = float(constructed.meta.get('net_standard_deviation',0))
                count += 1
                if (abs(cx-ax) > stdDiv):
                    res[(time, actual.teams[i].list_of_players[j].name)] = [actual.teams[i].list_of_players[j].times_to_pos[time], constructed.teams[i].list_of_players[j].times_to_pos[time][0]]
                elif (abs(cy-ay) > stdDiv):
                    res[(time, actual.teams[i].list_of_players[j].name)] = [actual.teams[i].list_of_players[j].times_to_pos[time], constructed.teams[i].list_of_players[j].times_to_pos[time][0]]

    return res,count

def calc_avrg_conf(actual):
    conf = []
    for i in range(len(actual.teams)):
        for j in range(len(actual.teams[i].list_of_players)):
            for time in actual.teams[i].list_of_players[j].times_to_pos.keys():
                conf.append(actual.teams[i].list_of_players[j].times_to_pos[time][0]["CONFIDENCE"])
    return (sum(conf)/len(conf))    

file = readJson(r"jimJson.json")

result = {}
r2 = {}

def randomThing():
    return random.randint(40,70) / 100

for i in range(15):
    random.seed(42)
    r = create_reconstructed(file,i+1,0,15,100,randomThing)
    # fileIO.writeJson("jimmy.json", r)
    result[i+1] = calc_avrg_conf(r)
    std_check_res, std_count = std_div_check(file, r)


    r2[i+1] = ((1 - (len(std_check_res)/std_count)))

x_values = list(result.keys())
y_values = list(result.values())

y_val_2 = list(r2.values())

plt.figure(figsize=(10, 6))
plt.plot(x_values, y_values,label = 'Confidence', marker='o', linestyle='-')
plt.plot(x_values, y_val_2 ,label = 'Actual % Pass', marker='x', linestyle='--')
plt.title('Average Confidence and Pass Rate vs. Number of Combined Files')
plt.xlabel('Number of Flawed Files Combined')
plt.ylabel('Value / Percentage')
plt.xticks(x_values)
plt.legend()
plt.grid(True)
plt.show()