class Player:
    """Represents a player throughout the game."""
    times_to_pos : dict[float,dict[str,tuple|float]] # (5,7)=x[1.2]['LOCATION']
    
    def __str__(self):
        return f'Player: {self.name}'
    def __repr__(self):
        return self.__str__()
    
    def __init__(self,player_dict : dict = {},name = 'default'):
        self.times_to_pos = {}
        self.name = name
        for time in player_dict.keys():
            # Do things with time????
            self.times_to_pos[time] = player_dict[time]
    
    def toDict(self):
        result = {}
        for time in self.times_to_pos.keys():
            # do things with time??
            result[time] = self.times_to_pos[time]
        return result
            
class Team:
    """A List of Players"""
    list_of_players :list[Player]
    name : str

    def __str__(self):
        return f'{self.name} = {self.list_of_players}\n'
    def __repr__(self):
        return self.__str__()

    def __init__(self,name):
        self.list_of_players = []
        self.name = name
    
    def add(self,player : Player):
        """Add a player to the team."""
        self.list_of_players.append(player)

    def toDict(self):
        result = {}
        for player in self.list_of_players:
            result[player.name] = player.toDict()
        return result