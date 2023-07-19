import numpy as np
import pandas as pd

#drop all the unnecessary columns 
data = pd.read_csv('indicators.csv')
data = data.loc[:, :'Credit Rating']

#refilling the empty values with the ffill method then dropping duplicates
data = data.replace('', np.nan)
data = data.fillna(method='ffill', axis=0).fillna(method='bfill', axis=0)

data = data.drop_duplicates()
data.to_csv('cleaned.csv', index=False)