from demoparser2 import DemoParser
import time as t
import pandas as pd
pre = t.time()
parser = DemoParser(r"m1.dem")
ticks_df = parser.parse_ticks(["X", "Y"])
print(ticks_df)
sampledTicks = []
nameL = []
tickL = []
for name, nameGrouped in ticks_df.groupby('name'):
    for tick in range(nameGrouped['tick'].__len__() // 64):
        currentRow = nameGrouped.iloc[tick * 64]
        sampledTicks.append(f"Name,{name}\nX,{currentRow[0]}\nY,{currentRow[1]}\nTick,{currentRow[2]}\n")
with open('jim.csv',"w") as f:
    f.writelines(sampledTicks)
