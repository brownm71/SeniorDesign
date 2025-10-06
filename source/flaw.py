import random

random.seed(42)

from lib import *
def remove_points(file : Teams_and_Meta,chance_to_remove:float) -> Teams_and_Meta:
    """This will go through each point of each player on each team and remove them {chance_to_remove}% of the time."""
    for team in file.teams:
        for player in team.list_of_players:
            for time in player.times_to_pos.keys():
                kept_points = []
                for point in player.times_to_pos[time]:
                    if random.random() > (chance_to_remove / 100.0):
                        kept_points.append(point)
                player.times_to_pos[time] = kept_points

    return file

def vary_points(file: Teams_and_Meta,max_amount_to_vary : float,chance_to_vary : float, confidence_multiplier : float):
    """Go through each point and change it {chance_to_vary} % it a random amount up to the {max_amount_to_vary} """
    for team in file.teams:
        for player in team.list_of_players:
            for time in player.times_to_pos.keys():
                for point in player.times_to_pos[time]:
                    if random.random() < (chance_to_vary / 100.0):
                        # vary the point
                        location = point.get('LOCATION')
                        if location and isinstance(location, list):
                            new_location = []
                            for coordinate in location:
                                variation = random.uniform(-max_amount_to_vary, max_amount_to_vary)
                                new_location.append(round(coordinate + variation,5))
                            point['LOCATION'] = new_location
                            if 'CONFIDENCE' in point and isinstance(point['CONFIDENCE'], (int, float)):
                                point['CONFIDENCE'] *= confidence_multiplier
                                point['CONFIDENCE'] = round(point['CONFIDENCE'],4) # to make the values more readable.
    return file

def create_flawed(file : Teams_and_Meta,chance_of_missing_points = None,max_vary_amount=None,chance_to_vary=None, confidence_multiplier=1.0):
    file = file.copy()
    
    if chance_of_missing_points is not None:
        file = remove_points(file, chance_of_missing_points)
    if chance_to_vary is not None and max_vary_amount is not None:
        file = vary_points(file, max_vary_amount, chance_to_vary, confidence_multiplier)
    return file

def evaluate(perfect_file: Teams_and_Meta,constructed_file: Teams_and_Meta,method = sum):
    """Takes a perfect_file and calculates the difference between the constructed_file."""
    diff = []
    missing_times = []
    for i in range(len(perfect_file.teams)):
        # compare number of players on team  
        if len(perfect_file.teams[i].list_of_players) != len(constructed_file.teams[i].list_of_players):
            raise Exception('Missing player')
        for j in range(len(perfect_file.teams[i].list_of_players)):
            
            pp = (perfect_file.teams[i].list_of_players[j])
            cp = (constructed_file.teams[i].list_of_players[j])
            for time in pp.times_to_pos.keys():
                px,py = pp.times_to_pos[time][0]['LOCATION']
                if cp.times_to_pos[time] is not None and len(cp.times_to_pos[time])!=0:
                    cx,cy = cp.times_to_pos[time][0].get('LOCATION',[0,0])
                else:
                    missing_times.append((time,pp))
                    cx = px
                    cy = py
                diff.append((px - cx) + (py - cy))

    return method(diff),missing_times

def abs_add(itter):
        total = 0
        for i in itter:
            total += abs(i)
        return total
    

if __name__ == "__main__":
    import fileIO
    file = fileIO.readJson(r"SeniorDesign\docs\singleTeamTest.json")
    file2 = create_flawed(file,chance_of_missing_points=100,max_vary_amount=1.5,chance_to_vary=50,confidence_multiplier=0.8)
    file3 = create_flawed(file,chance_of_missing_points=75,max_vary_amount=1.5,chance_to_vary=50,confidence_multiplier=0.8)
    file4 = create_flawed(file,chance_of_missing_points=75,max_vary_amount=1.5,chance_to_vary=50,confidence_multiplier=0.8)

    file2.combine(file3)
    file2.combine(file4)

    file.compress() # this is the final step
    file2.compress()
    # file2.interpolate() # this currently is broken # TODO
    fileIO.writeJson('t.json',file2)
    # fileIO.writeJson('test.json',file2)
    # fileIO.writeJson('real.json',file)
    x = evaluate(file,file2,abs_add)
    print(x)