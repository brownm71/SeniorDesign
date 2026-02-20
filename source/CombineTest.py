from lib import *
from fileIO import *

filenames = ("SeniorDesign\\docs\\singleTeamTest.json","SeniorDesign\\docs\\singleTeamTest2.json")

# combine_files(filenames,"TestOut.json")

f1 = readJson(filenames[0])
f2 = readJson(filenames[1])
f1.combine(f2, 'GeometricIt', bayesian=True)
writeJson('test.json',f1)