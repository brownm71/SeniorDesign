import random
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

def create_flawed(file :Teams_and_Meta,chance_of_missing_points = None,max_vary_amount=None,chance_to_vary=None, confidence_multiplier=1.0):
    file = file.copy()
    
    if chance_of_missing_points is not None:
        file = remove_points(file, chance_of_missing_points)
    if chance_to_vary is not None and max_vary_amount is not None:
        file = vary_points(file, max_vary_amount, chance_to_vary, confidence_multiplier)
    return file



if __name__ == "__main__":
    import fileIO
    file = fileIO.readJson(r"Golden.json")
    file2 = create_flawed(file,chance_of_missing_points=100,max_vary_amount=1.5,chance_to_vary=100, confidence_multiplier=0.25)
    fileIO.writeJson('test.json',file2)
    fileIO.writeJson('real.json',file)