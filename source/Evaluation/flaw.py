import random
from lib import *
def remove_points(file : Teams_and_Meta,chance_to_remove:float) -> Teams_and_Meta:
    """This will go through each point of each player on each team and remove them {chance_to_remove}% of the time."""
    for team in file.teams:
        for player in team.list_of_players:
            for time in player.times_to_pos.keys():
                kept_points = []
                for point in player.times_to_pos[time]:
                    if random.random() < chance_to_remove:
                        kept_points.append(point)
                player.times_to_pos[time] = kept_points

    return file

def vary_points(file,max_amount_to_vary : float,chance_to_vary : float):
    """Go through each point and change it {chance_to_vary} % it a random amount up to the {max_amount_to_vary} """
    pass