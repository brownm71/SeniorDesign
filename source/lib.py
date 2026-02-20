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

    def splineInterpolateFill(self, timestep = 1, doBasicInterpolatePass = False):
        """Take all the points, and fill in missing ones using Spline Interpolation."""
        # assumes Initial positions are accurate and there.

        sorted_times = sorted(self.times_to_pos.keys())
        start_time = float(sorted_times[0])
        end_time = float(sorted_times[-1])
        temp_times_to_pos = {}
        current_time = start_time
        while current_time <= end_time:
            if current_time not in self.times_to_pos:
                # Add a placeholder for the missing time
                temp_times_to_pos[current_time] = [{'LOCATION': None, 'CONFIDENCE': -1.0}]
            else:
                temp_times_to_pos[current_time] = self.times_to_pos[current_time]
            current_time += timestep

        # make sure the times are sorted.
        sorted_times = sorted(temp_times_to_pos.keys())
        points = []
        for time in sorted_times:
            if len(temp_times_to_pos[time]) !=0:
                confidence = temp_times_to_pos[time][0]['CONFIDENCE']
                if confidence < 0:
                    # this is a point to fill in.
                    points.append(None)
                else:
                    points.append(temp_times_to_pos[time][0]['LOCATION'])
            else:
                points.append(None) # this is a point to fill in
        # we have collected the points, now we fill in the gaps
        for i in range(len(points)):
            doInterpolation = True
            if points[i] is None:
                # This is a point to fill in.
                # find the closest point to the left.
                left_index_1 = -1
                for j in range(i - 1, -1, -1):
                    if points[j] is not None:
                        left_index_1 = j
                        break
                left_index_2 = -1
                if left_index_1 - 1 >= 0 and points[left_index_1 -1] is not None:
                    left_index_2 = left_index_1 - 1
                # find the closest point to the right.
                right_index_1 = -1
                for j in range(i + 1, len(points)):
                    if points[j] is not None:
                        right_index_1 = j
                        break
                right_index_2 = -1
                if right_index_1 + 1 <= len(points) - 1 and points[right_index_1 + 1] is not None:
                    right_index_2 = right_index_1 + 1

                # if we have two points on both sides, we can interpolate
                if left_index_1 != -1 and left_index_2 != -1 and right_index_1 != -1 and right_index_2 != -1:
                    left_point_1 = points[left_index_1]
                    right_point_1 = points[right_index_1]
                    left_point_2 = points[left_index_2]
                    right_point_2 = points[right_index_2]

                # if we are missing the furthest left point we need to fill it
                elif left_index_2 == -1 and left_index_1 != -1 and right_index_1 != -1 and right_index_2 != -1:
                    left_point_1 = points[left_index_1] 
                    right_point_1 = points[right_index_1]
                    right_point_2 = points[right_index_2]

                    left_point_2 = []
                    # generate an x and y coordinate based on the difference between the known right and left points.
                    left_point_2.append(points[left_index_1][0] - (points[right_index_1][0] - points[left_index_1][0]))
                    left_point_2.append(points[left_index_1][1] - (points[right_index_1][1] - points[left_index_1][1]))

                # if we are missing the furthest right point we need to fill it
                elif left_index_2 != -1 and left_index_1 != -1 and right_index_1 != -1 and right_index_2 == -1:
                    left_point_1 = points[left_index_1] 
                    left_point_2 = points[left_index_2]
                    right_point_1 = points[right_index_1]
                    right_point_2 = []

                    # generate an x and y coordinate based on the difference between the known right and left points.
                    right_point_2.append(points[right_index_1][0] + (points[right_index_1][0] - points[right_index_1][0]))
                    right_point_2.append(points[right_index_1][1] + (points[right_index_1][1] - points[right_index_1][1]))

                # Non-feasible case. Not enough data to interpolate.
                else:
                    doInterpolation = False
                
                # Do the interpolation
                if (doInterpolation):
                    numMissingPts = int(right_index_1 - left_index_1)
                    for j in range(numMissingPts - 1):
                        normalized_current_step = (j + 1) / numMissingPts
                        interpolated_point = []
                        val = []
                        val.append(catmull_formula(left_point_2[0], left_point_1[0], right_point_1[0], right_point_2[0], normalized_current_step))
                        val.append(catmull_formula(left_point_2[1], left_point_1[1], right_point_1[1], right_point_2[1], normalized_current_step))
                        interpolated_point.append(val)
                        print("appended")
                        points[i + j] = list(interpolated_point)
                    i += j

                    

        # Now we update the original dictionary with the interpolated points
        for i, time in enumerate(sorted_times):
            if points[i] is not None and temp_times_to_pos[time][0]['CONFIDENCE'] < 0:
                if (self.times_to_pos.get(time, None) is None):
                    self.times_to_pos[time] = [{}]
                self.times_to_pos[time][0]['LOCATION'] = points[i]
                self.times_to_pos[time][0]['CONFIDENCE'] = 0.05 # Mark as interpolated 
                self.times_to_pos[time][0]['NUMPOINTS'] = 1 
        if (doBasicInterpolatePass):
            self.basicInterpolateFill(timestep)

    def compress(self,round_place = None, bayesian = False):
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
                total_numpoints = data_points[0]['NUMPOINTS'] + data_points[i+1]['NUMPOINTS']
                if (bayesian):
                    new_confidence = update_confidence_bayesian(self_con, other_con, similarity)
                else:
                    new_confidence = update_confidence(self_con, other_con, similarity, total_numpoints)

                self_weighted_location_x = self_weight * self_con * data_points[0]['LOCATION'][0]
                self_weighted_location_y = self_weight * self_con * data_points[0]['LOCATION'][1]
                other_weighted_location_x = other_weight * other_con * data_points[i+1]['LOCATION'][0]
                other_weighted_location_y = other_weight * other_con * data_points[i+1]['LOCATION'][0]

                new_x_location = ((self_weighted_location_x + other_weighted_location_x) / (self_con*self_weight + other_con*other_weight))
                new_y_location = ((self_weighted_location_y + other_weighted_location_y) / (self_con*self_weight + other_con*other_weight))

                new_location = [new_x_location,new_y_location]

                

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

    def compress_geometric(self,round_place : int = None):
        """Compresses an historic player into having 1 datapoint per timestep.
        If round_place is passed, it will round all numbers to that many decimal places."""
        
        newTtoP :dict[float,list[dict[str, tuple|float]]] = {}
        
        for time in self.times_to_pos.keys():
            weights = []
            points_x = []
            points_y = []
            
            for data in self.times_to_pos.get(time,[]):
                points_x.append(data['LOCATION'][0])
                points_y.append(data['LOCATION'][1])
                weights.append(data['CONFIDENCE'])

            average_weights = sum(weights) / len(weights)

            print(points_y)
            print(points_x)

            new_y = weighted_geometric_avrg(points_y,weights)
            new_x = weighted_geometric_avrg(points_x,weights)
            if round_place is not None:
                new_x = round(new_x,round_place)
                new_y = round(new_y,round_place)
                average_weights = round(average_weights,round_place)
            
            newTtoP[time] = [{'LOCATION':[new_x,new_y],'CONFIDENCE' : average_weights,'NUM_POINTS':len(weights)}]
        self.times_to_pos = newTtoP

    def combine_arithmetic(self, other, bayesian = False):
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
                self.compress(bayesian=bayesian)
            if len(other.times_to_pos.get(time,[])) > 1:
                # other needs to be commpressed.
                other.compress(bayesian=bayesian)



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
            if (bayesian):
                new_confidence = update_confidence_bayesian(self_confidence, other_confidence, similarity)
            else:
                new_confidence = update_confidence(self_confidence, other_confidence, similarity, total_points)
            
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
        """Combine all of the data from one player object with another using a weighted Geometric average."""
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

        # now go through every point in the given time and add it to a list, while also adding all of their weights to a different list.
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

def catmull_formula(p0:float, p1:float, p2:float, p3:float, t:float) -> float:
    """ The calculation for catmull spline interpolation. """
    return 0.5 * (
        (2 * p1) +
        (-p0 + p2) * t +
        (2 * p0 - 5 * p1 + 4 * p2 - p3) * t**2 +
        (-p0 + 3 * p1 - 3 * p2 + p3) * t**3
    )

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
    
    def combine(self,other,method = 'Arithmetic',fill = False, bayesian = False):
        if self.meta['game_ID'] != other.meta['game_ID']:
            raise Exception("Files do not share a Game ID.")
        
        # Copy the teams for calculation of standard deviation from final point.
        orig = self.copy()
        orig_other = other.copy()
        orig.combine_historic(orig_other)
        
        if method =='Arithmetic':
            for i in range(len(self.teams)):
                for j in range(len(self.teams[i].list_of_players)):
                    self.teams[i].list_of_players[j].combine_arithmetic(other.teams[i].list_of_players[j], bayesian)
        if method =='Geometric':
            for i in range(len(self.teams)):
                for j in range(len(self.teams[i].list_of_players)):
                    self.teams[i].list_of_players[j].combine_geometric(other.teams[i].list_of_players[j])
        self.fill_std_dev(orig)
        
        
        if fill:
            # we need to interpolate.
            for team in self.teams:
                for player in team.list_of_players:
                    player.basicInterpolateFill(float(self.meta['time_step']))

    def fill_std_dev(self, past_self):
        """Computes the standard deviation for each point for each player. Requires compressed input"""
        for i in range(len(self.teams)):
                for j in range(len(self.teams[i].list_of_players)):
                    for time in self.teams[i].list_of_players[j].times_to_pos.keys():
                        x_mean = self.teams[i].list_of_players[j].times_to_pos[time][0]['LOCATION'][0]
                        y_mean = self.teams[i].list_of_players[j].times_to_pos[time][0]['LOCATION'][1]
                        pointsX = []
                        pointsY = []
                        for pt in past_self.teams[i].list_of_players[j].times_to_pos[time]:
                            pointsX.append(pt['LOCATION'][0]) 
                            pointsY.append(pt['LOCATION'][1])
                        x_std_dev = calc_standard_dev(pointsX, x_mean, len(pointsX))
                        y_std_dev = calc_standard_dev(pointsY, y_mean, len(pointsY))
                        # Take the largest standard deviation so it is a circle and not an oval
                        std_dev = max(x_std_dev, y_std_dev)
                        self.teams[i].list_of_players[j].times_to_pos[time][0]['SD'] = std_dev
        self.calc_dataset_std_dev()
        
    def calc_dataset_std_dev(self):
        """Calculate the standard deviation for the entire data set for easier readability. Requires a compressed data set where the standard deviations have already been calculated."""
        sds = []
        for i in range(len(self.teams)):
                for j in range(len(self.teams[i].list_of_players)):
                    for time in self.teams[i].list_of_players[j].times_to_pos.keys():                        
                        sds.append(self.teams[i].list_of_players[j].times_to_pos[time][0]['SD'])
        self.meta['net_standard_deviation'] = net_standard_deviation(sds, len(sds))

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

def weighted_geometric_avrg(values : list, weights : list, top_range = 10000) -> float:
    """Calculate the weighted geometric average for two player objects. Called in the combine_geometric function
    for calculation. Maps to [1 top_range] (10000 by default) to ensure log produces real results."""
    v_min = min(values)
    v_max = max(values)
    # Need to make sure that there is a difference in the max and min.
    if v_max == v_min:
        return v_max # there is only one value
    top_frac = 0
    min_range = 1
    scaled_values = []
    for val in values:
        scaled_val = min_range + ((val - v_min) * (top_range - min_range) / (v_max - v_min))
        scaled_values.append(scaled_val)
    for i in range(len(scaled_values)):
        top_frac += math.log(scaled_values[i]) * weights[i]
    bot_frac = sum(weights)
    res_scaled = math.exp(top_frac / bot_frac)
    res_descaled = ((res_scaled - min_range) * (v_max - v_min) / (top_range - min_range)) + v_min
    return res_descaled

def similarity_calc(m1:dict[str,tuple|float], m2:dict[str,tuple|float]):
    """
    Calculates a similarity score between two points based on a modified cosine similarity.

    This function treats the two input points as vectors from the origin. It computes
    their dot product and divides it by the squared L2 norm (magnitude) of the
    longer of the two vectors. This penalizes differences in both angle and magnitude.
    The result is then scaled from a [-1, 1] range to a [0, 1] range, where 1
    represents high similarity.

    Args:
        m1: A dictionary containing the first point's data, including a 'LOCATION' tuple.
        m2: A dictionary containing the second point's data, including a 'LOCATION' tuple.

    Returns:
        A float between 0 and 1 representing the similarity score.
    """
    pt1 = m1['LOCATION']
    pt2 = m2['LOCATION']
    xdot = pt1[0] * pt2[0]
    ydot = pt1[1] * pt2[1]
    dot_total = xdot + ydot
    similarity = dot_total / max(math.sqrt(pt1[0]**2 + pt1[1]**2) , math.sqrt(pt2[0]**2 + pt2[1]**2) )**2
    similarity = (similarity + 1) / 2 # Transforms from -1 to 1 into 0 to 1
    return similarity

def calc_standard_dev(points, mean, num_pts):
  """
  Calculates the standard deviation.
  """
  if num_pts == 0:
    return 0.0 # Standard deviation is undefined or 0 for no data

  # 1. Calculate the sum of squared differences from the mean
  sum_squared_diff = 0
  for point in points:
    difference = abs(point - mean)
    sum_squared_diff += difference**2

  # 2. Calculate the variance (average of the squared differences)
  variance = sum_squared_diff / num_pts

  # 3. Calculate the standard deviation (square root of the variance)
  std_dev = math.sqrt(abs(variance))

  return std_dev

def net_standard_deviation(sds, num_sd):
    """Calculate the RMS of the standard deviations to get a net standard deviation."""
    sd_sum = 0
    for sd in sds:
        sd_sum += sd
    return sd_sum / len(sds)

def update_confidence(c1:float, c2:float, similarity:float, total_points:int):
    """Update the confidence of a player's position given two locations for a given time with confidences c1 and c2. 
    Use the similarity between the two locations to determine whether to increase or decrease the resulting confidence."""
    if (similarity < 0.45):
        # Scale with how statistically different they are. 0.45 is just enough to count as different so just average them.
        new_confidence = ((c1 + c2) / 2) * (1/total_points) * (similarity / 0.45) 
    else:
        largest = (max(c1 ,c2))
        smallest = min(c1,c2)
        # Scale towards one using the smaller confidence starting from the larger confidence.
        new_confidence = largest + (1/total_points) * (1-largest) * smallest

    return new_confidence

def update_confidence_bayesian(newConf:float, currConf:float, similarity:float) -> float:
    """Use Bayesian Update Methodology to update the confidence using the current confidence and the confidence of the 
    added point."""
    if similarity >= 0.45:
        likelihood_true = currConf
        likelihood_false = 1.0 - currConf 
    else:
        likelihood_true = 1.0 - currConf
        likelihood_false = currConf
    # 3. Apply Bayes' Theorem
    # P(True | Obs) = [P(Obs | True) * P(True)] / P(Obs)
    numerator = likelihood_true * newConf
    
    # The denominator is the total probability of this observation occurring
    # P(Obs | True)*P(True) + P(Obs | False)*P(False)
    denominator = (likelihood_true * newConf) + (likelihood_false * (1.0 - newConf))
    
    new_confidence = numerator / denominator

    return new_confidence

