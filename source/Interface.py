from lib import *
from fileIO import readJson, writeJson

class STI:
    """
    Spacial Temporal Interface
    This object acts as an interface to the rest of the program, allowing ease of use with 
    built-in helper functions:

    - get all data from a player.
    - get all data from a team.
    - get all data at a specific time / range of times / list of times.
    - Combining many files
    - getting global settings
    - easy way to add data points
    - velocity ???? (Highest Probable Velocity) ie. HPV (per player highest mesured velocity.)
    - total distance traveled
    - max speed ????
    - Visualization prep : making into array (per player)
    """
    parent_object : Teams_and_Meta
    filename : str 

    def __init__(self):
        self.parent_object = None
        self.filename = None

    def __str__(self):
        if self.parent_object is not None:
            return f'{self.filename} : {self.parent_object.meta['game_ID']}'
        else:
            return f'STI: No Parent'
    def load(self,filename):
        """Reads in a file, and sets it to be the edited object."""
        self.parent_object = readJson(filename)
        self.filename  = filename

    def save(self,filename = None):
        """Saves current File to the given Filename, if no filename is passed, it will Override the loaded file."""
        if filename == None:
            # use saved filename
            filename = self.filename
        writeJson(filename,self.parent_object)

    def get_player(self,name,teamname = None) -> Player|None:
        """
        Search through the given team, or every team in None are passed, 
        looking for a player with the given name.
        
        returns None if not found.

        **MAY CAUSE ISSUES WITH NAME COLLISIONS of seperate teams**
        """
        # TODO add teamname useage
        for team in self.parent_object.teams:
            for player in team.list_of_players:
                if player.name == name:
                    return player
        
    def get_team(self,name)-> Team|None:
        """Finds and returns the team with the given name."""
        for team in self.parent_object.teams:
            if team.name == name:
                return team
        return None
    
    def get_team_names(self) ->list[str]:
        """Goes through all the Teams and returns there names."""
        res = []
        for team in self.parent_object.teams:
            res.append(team.name)
        return res
    
if __name__ == '__main__':
    sti = STI()
    sti.load('t.json')
    sti.get_teams()