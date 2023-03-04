import pandas as pd
import numpy as np
path = 'C:/Users/asus/Documents/AirSim/2023-03-04-00-23-51/airsim_rec.txt'
data=pd.read_csv(path,sep='\t',header=None)
print(data)
for i in range(len(data.iloc[0,:])):
    if data[i][0] == "Latitude":
        print(np.array(data.iloc[1:,i]))