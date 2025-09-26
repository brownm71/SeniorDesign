class Player:
    """Represents a player throughout the game."""
    times_to_pos : dict[float,dict[str,tuple|float]] # (5,7)=x[1.2]['LOCATION']
    compressed : bool

    def __str__(self):
        return f'Player: {self.name}'
    def __repr__(self):
        return self.__str__()
    
    def __init__(self,player_dict : dict = None,name = 'default'):
        self.times_to_pos = {}
        self.name = name
        self.compressed = False

        if player_dict is None:
            self.player_dict = {}

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

    def compress(self):
        """Compress into a single point."""
        if self.compressed:
            return
        #TODO

    def combine_arithmetic(self, other):
        """Combine two player objects into one player using weighted arithmetic mean on confidence and nuber of points."""
        if not isinstance(other,Player):
            raise Exception('Must combine with a player.')
        if (self.name != other.name):
            raise Exception("Must combine players that are the same.")
        newTtoP :dict[float,list[dict[str, tuple|float]]]= {}
        
        shared_times = set()
        for time in self.times_to_pos.keys():
            shared_times.add(time)
        for time in other.times_to_pos.keys():
            shared_times.add(time)
        
        # check if either needs to be compressed:
        for time in shared_times:
            if len(self.times_to_pos.get(time,[])) > 1:
                # self needs to be commpressed.
                self.compress()
            if len(other.times_to_pos.get(time,[])) > 1:
                # other needs to be commpressed.
                other.compress()



        # sharedTimes contains all unique time values
        for time in shared_times:
            current_data = self.times_to_pos.get(time)[0]
            new_data = other.times_to_pos.get(time)[0]
            if (current_data is None):
                newTtoP[time] = new_data
                continue
            elif (new_data is None):
                newTtoP[time] = current_data
                continue


            newTtoP[time] = [{}]
            total_points = self.times_to_pos.get(time)[0]['NUMPOINTS'] + other.times_to_pos.get(time)[0]['NUMPOINTS']
            self_weight = self.times_to_pos.get(time)[0]['NUMPOINTS']
            other_weight = other.times_to_pos.get(time)[0]['NUMPOINTS']

            self_confidence = self.times_to_pos.get(time)[0]['CONFIDENCE']
            other_confidence = other.times_to_pos.get(time)[0]['CONFIDENCE']

            newTtoP[time][0]['CONFIDENCE'] = (self_weight * (self.times_to_pos.get(time)[0]['CONFIDENCE']) + other_weight * (other.times_to_pos.get(time)[0]['CONFIDENCE'])) /(2*total_points)
            
            self_weighted_location_x = self_weight * self_confidence * self.times_to_pos.get(time)[0]['LOCATION'][0]
            self_weighted_location_y = self_weight * self_confidence * self.times_to_pos.get(time)[0]['LOCATION'][1]
            other_weighted_location_x = other_weight * other_confidence * other.times_to_pos.get(time)[0]['LOCATION'][0]
            other_weighted_location_y = other_weight * other_confidence * other.times_to_pos.get(time)[0]['LOCATION'][1]

            new_x_location = ((self_weighted_location_x + other_weighted_location_x) / (self_confidence + other_confidence))
            new_y_location = ((self_weighted_location_y + other_weighted_location_y) / (self_confidence + other_confidence))
            
            newTtoP[time][0]['LOCATION'] = []
            newTtoP[time][0]['LOCATION'].append(new_x_location)
            newTtoP[time][0]['LOCATION'].append(new_y_location)
            
            newTtoP[time][0]['NUMPOINTS'] = self.times_to_pos.get(time)[0]['NUMPOINTS'] + other.times_to_pos.get(time)[0]['NUMPOINTS']
        self.times_to_pos = newTtoP

    def combine_geometric(self,other):
        """Combine two players using a weighted Geometric average."""
        pass
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
    

def weighted_geometric_avrg(values : list, weights : list) -> float:
    val = 1 
    for i in range(len(values)):
        val = val * values[i]**(weights[i])
    res = val**(1/sum(weights))
    return res
