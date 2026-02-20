from lib import *
from Interface import *


x = STI()
x.load('t.json')
p = x.get_player('player_1')
p.calc_velocity_estimate()
print(p.get_list_of_positions())
