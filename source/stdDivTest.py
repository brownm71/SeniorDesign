import random
import fileIO
from flaw import *
random.seed(42)
if __name__ == '__main__':
    file = fileIO.readJson(r"jimJson.json")
    r = create_reconstructed(file,10,0,15,100,.5)
    fileIO.writeJson("jimmy.json", r)
    print(evaluate(file, r, true_div))


# def std_div_check(actual : Teams_and_Meta, constructed : Teams_and_Meta):
#     res = {}
#     count = 0
#     for i in range(len(actual.teams)):
#         for j in range(len(actual.teams[i].list_of_players)):
#             for time in actual.teams[i].list_of_players[j].times_to_pos.keys():
#                 ax,ay = actual.teams[i].list_of_players[j].times_to_pos[time][0]['LOCATION']
#                 cx, cy = constructed.teams[i].list_of_players[j].times_to_pos[time][0]['LOCATION']
#                 stdDiv = constructed.teams[i].list_of_players[j].times_to_pos[time][0]['SD']
#                 # stdDiv = float(constructed.meta['net_standard_deviation'])
#                 count += 1
#                 if (abs(cx-ax) > stdDiv):
#                     res[(time, actual.teams[i].list_of_players[j].name)] = [actual.teams[i].list_of_players[j].times_to_pos[time], constructed.teams[i].list_of_players[j].times_to_pos[time][0]]
#                 elif (abs(cy-ay) > stdDiv):
#                     res[(time, actual.teams[i].list_of_players[j].name)] = [actual.teams[i].list_of_players[j].times_to_pos[time], constructed.teams[i].list_of_players[j].times_to_pos[time][0]]

#     return res,count

# res, count = std_div_check(file, r)
# print(res)
# print(len(res))
# print(count)
# print((1 - (len(res)/count)) * 100)

