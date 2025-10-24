import copy
import math
class Player:
    """Represents a player throughout the game."""
    times_to_pos : dict[float,list[dict[str,tuple|float]]] # (5,7)=x[1.2]['LOCATION']
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
                self.times_to_pos[current_time] = [{'LOCATION': None, 'CONFIDENCE': -1.0}]
            current_time += timestep

        # make sure the times are sorted.
        sorted_times = sorted(self.times_to_pos.keys())
        points = []
        for time in sorted_times:
            if len(self.times_to_pos[time]) !=0:
                confidence = self.times_to_pos[time][0]['CONFIDENCE']
                if confidence < 0:
                    # this is a point to fill in.
                    points.append(None)
                else:
                    points.append(self.times_to_pos[time][0]['LOCATION'])
            else:
                points.append(None) # this is a point to fill in
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
            if points[i] is not None and self.times_to_pos[time][0]['CONFIDENCE'] < 0:
                self.times_to_pos[time][0]['LOCATION'] = points[i]
                self.times_to_pos[time][0]['CONFIDENCE'] = 0.1 # Mark as interpolated 
                self.times_to_pos[time][0]['NUMPOINTS'] = 0 # TODO What to do here?? 

    def compress(self,round_place = None):
        """Compresses multiple data points at the same timestamp into a single, weighted-average point."""
        if self.compressed:
            return

        new_times_to_pos = {}
        for time, data_points in self.times_to_pos.items(): # there is garaunteed to be a least one point.
            if not isinstance(data_points, list) or len(data_points) <= 1:
                new_times_to_pos[time] = data_points
                continue

            for i in range(len(data_points)-1):
                # we costantly update the first point, untill it becomes the only point remaining.
                self_weight = data_points[0]['NUMPOINTS']
                other_weight = data_points[i+1]['NUMPOINTS']

                self_con = data_points[0]['CONFIDENCE']
                other_con = data_points[i+1]['CONFIDENCE']
                similarity = similarity_calc(data_points[0], data_points[i+1])
                if (similarity < 0.45):
                    new_confidence = ((self_con + other_con) / 2) * (similarity / 0.45)
                else:
                    largest = max(self_con ,other_con)
                    smallest = min(self_con,other_con)
                    new_confidence = largest + (1-largest) * smallest

                self_weighted_location_x = self_weight * self_con * data_points[0]['LOCATION'][0]
                self_weighted_location_y = self_weight * self_con * data_points[0]['LOCATION'][1]
                other_weighted_location_x = other_weight * other_con * data_points[i+1]['LOCATION'][0]
                other_weighted_location_y = other_weight * other_con * data_points[i+1]['LOCATION'][0]

                new_x_location = ((self_weighted_location_x + other_weighted_location_x) / (self_con*self_weight + other_con*other_weight))
                new_y_location = ((self_weighted_location_y + other_weighted_location_y) / (self_con*self_weight + other_con*other_weight))

                new_location = [new_x_location,new_y_location]

                total_numpoints = data_points[0]['NUMPOINTS'] + data_points[i+1]['NUMPOINTS']

                # update for next itteration.
                data_points[0]['LOCATION'] = new_location
                data_points[0]['CONFIDENCE'] = new_confidence
                data_points[0]['NUMPOINTS'] = total_numpoints


            if round_place is not None:
                ls = []
                for l in new_location:
                    ls.append(round(l,round_place))
                new_location = ls

            new_times_to_pos[time] = [data_points[0]] # sets it to only be the first datapoint
        
        self.times_to_pos = new_times_to_pos
        self.compressed = True

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
            current_data = self.times_to_pos.get(time)
            new_data = other.times_to_pos.get(time)
            if (current_data is None or len(current_data)==0):
                newTtoP[time] = new_data
                continue
            elif (new_data is None or len(new_data)==0):
                newTtoP[time] = current_data
                continue


            newTtoP[time] = [{}]

            total_points = self.times_to_pos.get(time)[0]['NUMPOINTS'] + other.times_to_pos.get(time)[0]['NUMPOINTS']
            self_weight = self.times_to_pos.get(time)[0]['NUMPOINTS']
            other_weight = other.times_to_pos.get(time)[0]['NUMPOINTS']

            self_confidence = self.times_to_pos.get(time)[0]['CONFIDENCE']
            other_confidence = other.times_to_pos.get(time)[0]['CONFIDENCE']
            similarity = similarity_calc(self.times_to_pos.get(time)[0], other.times_to_pos.get(time)[0])
            if (similarity < 0.45):
                new_confidence = ((self_confidence + other_confidence) / 2) * (similarity / 0.45) # Scale with how statistically different they are. 0.5 is just enough to count as different so just average them.
            else:
                largest = (max(self_confidence ,other_confidence))
                smallest = min(self_confidence,other_confidence)
                new_confidence = largest + (1-largest) * smallest
            
            newTtoP[time][0]['CONFIDENCE'] = new_confidence
            
            self_weighted_location_x = self_weight * self_confidence * self.times_to_pos.get(time)[0]['LOCATION'][0]
            self_weighted_location_y = self_weight * self_confidence * self.times_to_pos.get(time)[0]['LOCATION'][1]
            other_weighted_location_x = other_weight * other_confidence * other.times_to_pos.get(time)[0]['LOCATION'][0]
            other_weighted_location_y = other_weight * other_confidence * other.times_to_pos.get(time)[0]['LOCATION'][1]

            new_x_location = ((self_weighted_location_x + other_weighted_location_x) / (self_confidence*self_weight + other_confidence*other_weight))
            new_y_location = ((self_weighted_location_y + other_weighted_location_y) / (self_confidence*self_weight + other_confidence*other_weight))
            
            newTtoP[time][0]['LOCATION'] = []
            newTtoP[time][0]['LOCATION'].append(new_x_location)
            newTtoP[time][0]['LOCATION'].append(new_y_location)
            
            newTtoP[time][0]['NUMPOINTS'] = total_points
        self.times_to_pos = newTtoP

    def combine_geometric(self,other):
        """Combine two players using a weighted Geometric average."""
        if not isinstance(other,Player):
            raise Exception('Must combine with a player.')
        if (self.name != other.name):
            raise Exception("Must combine players that are the same.")
        
        newTtoP :dict[float,list[dict[str, tuple|float]]] = {}
        
        shared_times = set()
        for time in self.times_to_pos.keys():
            shared_times.add(time)
        for time in other.times_to_pos.keys():
            shared_times.add(time)

        # now go through every point in the given time and add it to a list, while also adding all of there weights to a different list.
        for time in shared_times:
            weights  = []
            points_x = []
            points_y = []
            for data in self.times_to_pos.get(time,[]):
                points_x.append(data['LOCATION'][0])
                points_y.append(data['LOCATION'][1])
                weights.append(data['CONFIDENCE'])
            
            for data in other.times_to_pos.get(time,[]):
                points_x.append(data['LOCATION'][0])
                points_y.append(data['LOCATION'][1])
                weights.append(data['CONFIDENCE'])

            average = sum(weights) / len(weights)

            new_y = weighted_geometric_avrg(points_y,weights)
            new_x = weighted_geometric_avrg(points_x,weights)
            newTtoP[time] = [{'LOCATION':[new_x,new_y],'CONFIDENCE' : average,'NUM_POINTS':len(weights)}]
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
    
class Teams_and_Meta:
    teams : list[Team]
    meta : dict
    def __init__(self,teams,meta):
        self.teams = teams
        self.meta = meta

    def copy(self):
        """Create a deep copy of the file."""
        res_teams = []
        for team in self.teams:
            res_teams.append(copy.deepcopy(team))
        newMeta = self.meta.copy() # this should be fine, as it is only stores immutables
        res = Teams_and_Meta(res_teams,newMeta)
        return res
    
    def combine(self,other,method = 'Arithmetic',fill = False):
        if self.meta['game_ID'] != other.meta['game_ID']:
            raise Exception("Files do not share a Game ID.")
        
        if method =='Arithmetic':
            for i in range(len(self.teams)):
                for j in range(len(self.teams[i].list_of_players)):
                    self.teams[i].list_of_players[j].combine_arithmetic(other.teams[i].list_of_players[j],self.meta['allowable_distance'])
        if method =="Geometric":
            for i in range(len(self.teams)):
                for j in range(len(self.teams[i].list_of_players)):
                    self.teams[i].list_of_players[j].combine_geometric(other.teams[i].list_of_players[j])
        
        
        
        if fill:
            # we need to interpolate.
            for team in self.teams:
                for player in team.list_of_players:
                    player.basicInterpolateFill(float(self.meta['time_step']))

    def compress(self,nplaces = None):
        """This will combine all datapoints in every player to one for each time."""
        for team in self.teams:
            for player in team.list_of_players:
                player.compress(nplaces) # this is using an arithmetic weighted average.
    
    def interpolate(self):
        for team in self.teams:
            for player in team.list_of_players:
                player.basicInterpolateFill(float(self.meta['time_step']))

    def combine_historic(self,other):
        """Combines two files maintaining all of there respective data in place."""
        if not isinstance(other, Teams_and_Meta):
            raise Exception('Cannot combine things that are not Team_and_Meta objects.')
        if self.meta['game_ID'] != other.meta['game_ID']:
            raise Exception("Game ID's must be the same!")

        for i in range(len(other.teams)):
            for j in range(len(other.teams[i].list_of_players)):
                for time in (other.teams[i].list_of_players[j].times_to_pos.keys()):
                    for data in other.teams[i].list_of_players[j].times_to_pos[time]:
                        self.teams[i].list_of_players[j].times_to_pos.get(time,[]).append(data)

def weighted_geometric_avrg(values : list, weights : list) -> float:
    val = 1
    for i in range(len(values)):
        val = val * values[i]**(weights[i])
    res = val**(1/sum(weights))
    return res

def similarity_calc(m1:dict[str,tuple|float], m2:dict[str,tuple|float]):
    pt1 = m1['LOCATION']
    pt2 = m2['LOCATION']
    xdot = pt1[0] * pt2[0]
    ydot = pt1[1] * pt2[1]
    dot_total = xdot + ydot
    similarity = dot_total / max(math.sqrt(pt1[0]**2 + pt1[1]**2) , math.sqrt(pt2[0]**2 + pt2[1]**2) )**2
    similarity = (similarity + 1) / 2 # Transforms from -1 to 1 into 0 to 1
    return similarity
