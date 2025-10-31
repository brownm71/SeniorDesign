import math
from flaw import *
def similarity_calc(m1:dict[str,tuple|float], m2:dict[str,tuple|float]):
    pt1 = m1['LOCATION']
    pt2 = m2['LOCATION']
    xdot = pt1[0] * pt2[0]
    ydot = pt1[1] * pt2[1]
    dot_total = xdot + ydot
    similarity = dot_total / max(norm_L2(pt1), norm_L2(pt2))**2
    similarity = (similarity + 1) / 2 # Transforms from -1 to 1 into 0 to 1
    return similarity

def norm_test(m1:dict[str,tuple|float], m2:dict[str,tuple|float], p:int):
    pt1 = m1['LOCATION']
    pt2 = m2['LOCATION']
    norm_pt1 = general_Norm(pt1, p)
    norm_pt2 = general_Norm(pt2, p)
    norm_average = (norm_pt1 + norm_pt2) / 2
    similarity = norm_average / max(norm_pt1, norm_pt2)
    return similarity

def norm_L2(pt):
    return math.sqrt(pt[0]**2 + pt[1]**2) 

def general_Norm(pt, p):
    return (abs(pt[0])**p + abs(pt[1])**p)**(1/p)



if __name__ == "__main__":

    def test_combine(file1:Teams_and_Meta, file2:Teams_and_Meta, func):
        for i in range(len(file1.teams)):
            for j in range(len(file1.teams[i].list_of_players)):
                combine_arithmetic_test(file1.teams[i].list_of_players[j],file2.teams[i].list_of_players[j],file1.meta['allowable_distance'], func)

    def combine_arithmetic_test(player1, player2,allowable_distance = 0, conf_updoot = None):
            """Combine two player objects into one player using weighted arithmetic mean on confidence and nuber of points."""
            if not isinstance(player2,Player):
                raise Exception('Must combine with a player.')
            if (player1.name != player2.name):
                raise Exception("Must combine players that are the same.")
            newTtoP :dict[float,list[dict[str, tuple|float]]]= {}
            
            shared_times = set()
            for time in player1.times_to_pos.keys():
                shared_times.add(time)
            for time in player2.times_to_pos.keys():
                shared_times.add(time)
            
            # check if either needs to be compressed:
            for time in shared_times:
                if len(player1.times_to_pos.get(time,[])) > 1:
                    # self needs to be commpressed.
                    print("selfCompress")
                    player1.compress()
                if len(player2.times_to_pos.get(time,[])) > 1:
                    # other needs to be commpressed.
                    print("otherCompress")
                    player2.compress()



            # sharedTimes contains all unique time values
            for time in shared_times:
                current_data = player1.times_to_pos.get(time)
                new_data = player2.times_to_pos.get(time)
                if (current_data is None or len(current_data)==0):
                    newTtoP[time] = new_data
                    continue
                elif (new_data is None or len(new_data)==0):
                    newTtoP[time] = current_data
                    continue


                newTtoP[time] = [{}]

                total_points = player1.times_to_pos.get(time)[0]['NUMPOINTS'] + player2.times_to_pos.get(time)[0]['NUMPOINTS']
                self_weight = player1.times_to_pos.get(time)[0]['NUMPOINTS']
                other_weight = player2.times_to_pos.get(time)[0]['NUMPOINTS']

                self_confidence = player1.times_to_pos.get(time)[0]['CONFIDENCE']
                other_confidence = player2.times_to_pos.get(time)[0]['CONFIDENCE']
                similarity = conf_updoot(player1.times_to_pos.get(time)[0], player2.times_to_pos.get(time)[0])
                if (similarity < 0.45):
                    new_confidence = ((self_confidence + other_confidence) / 2) * (similarity / 0.45) # Scale with how statistically different they are. 0.5 is just enough to count as different so just average them.
                else:
                    largest = (max(self_confidence ,other_confidence))
                    smallest = min(self_confidence,other_confidence)
                    new_confidence = largest + (1-largest) * smallest
                
                newTtoP[time][0]['CONFIDENCE'] = new_confidence

                self_weighted_location_x = self_weight * self_confidence * player1.times_to_pos.get(time)[0]['LOCATION'][0]
                self_weighted_location_y = self_weight * self_confidence * player1.times_to_pos.get(time)[0]['LOCATION'][1]
                other_weighted_location_x = other_weight * other_confidence * player2.times_to_pos.get(time)[0]['LOCATION'][0]
                other_weighted_location_y = other_weight * other_confidence * player2.times_to_pos.get(time)[0]['LOCATION'][1]

                new_x_location = ((self_weighted_location_x + other_weighted_location_x) / (self_confidence*self_weight + other_confidence*other_weight))
                new_y_location = ((self_weighted_location_y + other_weighted_location_y) / (self_confidence*self_weight + other_confidence*other_weight))
                
                newTtoP[time][0]['LOCATION'] = []
                newTtoP[time][0]['LOCATION'].append(new_x_location)
                newTtoP[time][0]['LOCATION'].append(new_y_location)
                
                newTtoP[time][0]['NUMPOINTS'] = player1.times_to_pos.get(time)[0]['NUMPOINTS'] + player2.times_to_pos.get(time)[0]['NUMPOINTS']
            player1.times_to_pos = newTtoP

    import fileIO
    
    file = fileIO.readJson(r"jimJson.json")
    file.compress()

    number_of_flawed = 5
    chance_of_missing_points = 0
    max_vary_amount = 500
    chance_to_vary = 100
    confidence_multiplier = .66

    functionList = []
    for p in range(1):
        functionList.append(lambda x, y: norm_test(x, y, p+1))
    functionList.append(similarity_calc)

    results = {}
    outputFiles = []
    for j in range(functionList.__len__()):
        random.seed(42)
        flawed_files : list[Teams_and_Meta] = []
        for i in range(number_of_flawed):
            flaw = create_flawed(file,chance_of_missing_points,max_vary_amount,chance_to_vary,confidence_multiplier)
            flawed_files.append(flaw)
        for i in range(len(flawed_files)-1):
            test_combine(flawed_files[0], flawed_files[i+1], functionList[j])
        fileModified = flawed_files[0]
        err = evaluate(file, fileModified, true_div)
        outputFiles.append(fileModified)
        results[j+1] = err
        print(f"{j+1} / {functionList.__len__()}")
    with open(r"SimilarityTest.json", 'w') as v:
        import json
        json.dump(results, v, indent=4)

    for i in range(len(outputFiles)):
        fileIO.writeJson(f'{i}.json',outputFiles[i])