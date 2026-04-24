from lib import *
from fileIO import readJson, writeJson

class STI:
    """
    Spatial Temporal Interface
    This object acts as an interface to the rest of the program, allowing ease of use with 
    built-in helper functions:

    - get all data from a player. (x)
    - get all data from a team. (x)
    - get all data at a specific time / range of times / list of times. ()
    - Combining many files (x)
    - getting global settings ()
    - easy way to add data points ()
    - velocity ???? (Highest Probable Velocity) ie. HPV (per player highest mesured velocity.) ()
    - total distance traveled ()
    - max speed ???? ()
    - Visualization prep : making into array (per player) ()
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
        if filename is None:
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
        
    def get_team(self,name) ->Team|None:
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
    
    def combine_files(self,filenames_to_combine : list[str],method = 'A', bayesian = True):
        """
        merges any number of seperate files into this file, using one of the given Methods:
        \n"A" : Arithmetic Mean (Good for most cases)
        \n"G" : Geometric Mean
        \n"GI" : Geometric Iterative
        \n"H" : Historic (Keeps all datapoints and does no math)

        :param filenames_to_combine: List of paths to the files.
        :type filenames_to_combine: list[str]
        :param method: determines the method used to combine.
        :param bayesian: boolean flag for Bayesian confidence updates.
        """
        # no matter the branch, we need to read in the files.
        files : list[Teams_and_Meta] = []
        for filename in filenames_to_combine:
            files.append(readJson(filename))
        
        # now all the files have been collected.
        # we need to check that they are the same Game ie. the game ID Matches
        for file in files:
            if file.meta['game_ID'] != self.parent_object.meta['game_ID']:
                raise Exception(f"At least one file is of a different Game: {file.meta['game_ID']}")


        if method == 'A':
            # Arithmeitic Mean
            # go through each one and combine it with the parent object
            for file in files:
                self.parent_object.combine(file, method='Arithmetic', bayesian=bayesian)
                
        elif method == 'G':
            # Geometric Mean
            for file in files:
                self.parent_object.combine(file, method='Geometric', bayesian=bayesian)

        elif method == 'GI':
            # Geometric Iterative
            for file in files:
                self.parent_object.combine(file, method='GeometricIt', bayesian=bayesian)

        elif method == 'H':
            # Historic Method
            for file in files:
                self.parent_object.combine_historic(file) 
        else:
            raise Exception(f'{method} does not represent a known method.')

    def combine_STI(self,STIs_to_combine : list[STI],method = 'A', bayesian = True):
        """
        merges any number of seperate STIs into this STI, using one of the given Methods:
        \n"A" : Arithmetic Mean (Good for most cases)
        \n"G" : Geometric Mean
        \n"GI" : Geometric Iterative
        \n"H" : Historic (Keeps all datapoints and does no math)

        :param STIs_to_combine: List of STIs.
        :type STIs_to_combine: list[STI]
        :param method: determines the method used to combine.
        :param bayesian: boolean flag for Bayesian confidence updates.
        """
        # check the game IDs
        for sti in STIs_to_combine:
            if sti.parent_object.meta['game_ID'] != self.parent_object.meta['game_ID']:
                raise Exception(f"At least one STI is of a different Game: {sti.parent_object.meta['game_ID']}")
        
        if method == 'A':
            # Arithmeitic Mean
            # go through each one and combine it with the parent object
            for sti in STIs_to_combine:
                self.parent_object.combine(sti.parent_object, method='Arithmetic', bayesian=bayesian)

        elif method == 'G':
            # Geometric Mean
            # First get historic
            for sti in STIs_to_combine:
                self.parent_object.combine(sti.parent_object, method='Geometric', bayesian=bayesian)

        elif method == 'GI':
            # Geometric Iterative
            for sti in STIs_to_combine:
                self.parent_object.combine(sti.parent_object, method='GeometricIt', bayesian=bayesian)

        elif method == 'H':
            # Historic Method
            for sti in STIs_to_combine:
                self.parent_object.combine_historic(sti.parent_object) 
        else:
            raise Exception(f'{method} does not represent a known method.')

    def combine_Teams_and_Meta(self,Teams_and_Meta_to_combine : list[Teams_and_Meta],method = 'A', bayesian = True):
        """
        merges any number of seperate Teams_and_Meta into this STI, using one of the given Methods:
        \n"A" : Arithmetic Mean (Good for most cases)
        \n"G" : Geometric Mean
        \n"GI" : Geometric Iterative
        \n"H" : Historic (Keeps all datapoints and does no math)

        :param Teams_and_Meta_to_combine: List of Teams_and_Meta objects.
        :type Teams_and_Meta_to_combine: list[Teams_and_Meta]
        :param method: determines the method used to combine.
        :param bayesian: boolean flag for Bayesian confidence updates.
        """
        # check the game IDs
        for tm in Teams_and_Meta_to_combine:
            if tm.meta['game_ID'] != self.parent_object.meta['game_ID']:
                raise Exception(f"At least one Teams_and_Meta is of a different Game: {tm.meta['game_ID']}")
        
        if method == 'A':
            # Arithmeitic Mean
            # go through each one and combine it with the parent object
            for tm in Teams_and_Meta_to_combine:
                self.parent_object.combine(tm, method='Arithmetic', bayesian=bayesian)

        elif method == 'G':
            # Geometric Mean
            for tm in Teams_and_Meta_to_combine:
                self.parent_object.combine(tm, method='Geometric', bayesian=bayesian)

        elif method == 'GI':
            # Geometric Iterative
            for tm in Teams_and_Meta_to_combine:
                self.parent_object.combine(tm, method='GeometricIt', bayesian=bayesian)

        elif method == 'H':
            # Historic Method
            for tm in Teams_and_Meta_to_combine:
                self.parent_object.combine_historic(tm) 
        else:
            raise Exception(f'{method} does not represent a known method.')


if __name__ == '__main__':
    sti = STI()
    sti.load('t.json')
    sti.combine_files(["t.json","t.json"],'A')
    sti.save("thing.json")