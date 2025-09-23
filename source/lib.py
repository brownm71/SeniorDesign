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
            self.times_to_pos[float(time)] = player_dict[time]
    
    def toDict(self):
        result = {}
        for time in self.times_to_pos.keys():
            # do things with time??
            result[time] = self.times_to_pos[time]
        return result
    
    def basicInterpolateFill(self, timestep = 1):
        """Take all the points, and fill in missing ones using Interpolation."""
        # assumes Initial positions are accurate and there.

        sorted_times = sorted(self.times_to_pos.keys())
        start_time = float(sorted_times[0])
        end_time = float(sorted_times[-1])

        current_time = start_time
        while current_time <= end_time:
            if current_time not in self.times_to_pos:
                # Add a placeholder for the missing time
                self.times_to_pos[current_time] = {'LOCATION': None, 'CONFIDENCE': -1.0}
            current_time += timestep

        # make sure the times are sorted.
        sorted_times = sorted(self.times_to_pos.keys())
        points = []
        for time in sorted_times:
            confidence = self.times_to_pos[time]['CONFIDENCE']
            if confidence < 0:
                # this is a point to fill in.
                points.append(None)
            else:
                points.append(self.times_to_pos[time]['LOCATION'])
        # we have collected the points, now we fill in the gaps
        for i in range(len(points)):
            if points[i] is None:
                # This is a point to fill in.
                # find the closest point to the left.
                left_index = -1
                for j in range(i - 1, -1, -1):
                    if points[j] is not None:
                        left_index = j
                        break
                # find the closest point to the right.
                right_index = -1
                for j in range(i + 1, len(points)):
                    if points[j] is not None:
                        right_index = j
                        break
                # if we have a point on both sides, we can interpolate
                if left_index != -1 and right_index != -1:
                    left_point = points[left_index]
                    right_point = points[right_index]

                    total_steps = float(right_index - left_index)
                    current_step = float(i - left_index)
                    # Assuming LOCATION is [x, y] currently
                    if isinstance(left_point, list) and isinstance(right_point, list):
                        interpolated_point = []
                        for dim in range(len(left_point)): # so that any number of dimentions can be used.
                            val = left_point[dim] + (right_point[dim] - left_point[dim]) * (current_step / total_steps)
                            interpolated_point.append(val)

                        points[i] = list(interpolated_point)

        # Now we update the original dictionary with the interpolated points
        for i, time in enumerate(sorted_times):
            if points[i] is not None and self.times_to_pos[time]['CONFIDENCE'] < 0:
                self.times_to_pos[time]['LOCATION'] = points[i]
                self.times_to_pos[time]['CONFIDENCE'] = 0.1 # Mark as interpolated 
                self.times_to_pos[time]['NUMPOINTS'] = 0 # TODO What to do here?? 

    def combine(self, other):
        """Combine two player objects into one player with updated confidence levels and positions."""
        if not isinstance(other,Player):
            raise Exception('Must combine with a player.')
        if (self.name != other.name):
            raise Exception("Must combine players that are the same.")
        newTtoP :dict[float,dict[str, tuple|float]]= {}
        sharedTimes = set()
        for time in self.times_to_pos.keys():
            sharedTimes.add(time)
        for time in other.times_to_pos.keys():
            sharedTimes.add(time)
        
        # sharedTimes contains all unique time values
        for time in sharedTimes:
            currentData = self.times_to_pos.get(time)
            newData = other.times_to_pos.get(time)
            if (currentData is None):
                newTtoP[time] = newData
                continue
            elif (newData is None):
                newTtoP[time] = currentData
                continue
            newTtoP[time] = dict()
            pointTot = self.times_to_pos.get(time)['NUMPOINTS'] + other.times_to_pos.get(time)['NUMPOINTS']
            selfWeight = self.times_to_pos.get(time)['NUMPOINTS'] / pointTot
            otherWeight = other.times_to_pos.get(time)['NUMPOINTS'] / pointTot
            newTtoP[time]['CONFIDENCE'] = (selfWeight * (self.times_to_pos.get(time)['CONFIDENCE']) + otherWeight * (other.times_to_pos.get(time)['CONFIDENCE'])) / 2
            newTtoP[time]['LOCATION'] = []
            newTtoP[time]['LOCATION'].append((selfWeight * self.times_to_pos.get(time)['CONFIDENCE'] * (self.times_to_pos.get(time)['LOCATION'][0]) + otherWeight * other.times_to_pos.get(time)['CONFIDENCE'] * (other.times_to_pos.get(time)['LOCATION'][0])) / 2)
            newTtoP[time]['LOCATION'].append((selfWeight * self.times_to_pos.get(time)['CONFIDENCE'] * (self.times_to_pos.get(time)['LOCATION'][1]) + otherWeight * other.times_to_pos.get(time)['CONFIDENCE'] * (other.times_to_pos.get(time)['LOCATION'][1])) / 2)
            newTtoP[time]['LOCATION'][0] = newTtoP[time]['LOCATION'][0] / ((self.times_to_pos.get(time)['CONFIDENCE'] + other.times_to_pos.get(time)['CONFIDENCE']) / 2)
            newTtoP[time]['LOCATION'][1] = newTtoP[time]['LOCATION'][1] / ((self.times_to_pos.get(time)['CONFIDENCE'] + other.times_to_pos.get(time)['CONFIDENCE']) / 2)
            newTtoP[time]['LOCATION'][0] = newTtoP[time]['LOCATION'][0] * pointTot
            newTtoP[time]['LOCATION'][1] = newTtoP[time]['LOCATION'][1] * pointTot
            newTtoP[time]['NUMPOINTS'] = self.times_to_pos.get(time)['NUMPOINTS'] + other.times_to_pos.get(time)['NUMPOINTS']
        self.times_to_pos = newTtoP


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