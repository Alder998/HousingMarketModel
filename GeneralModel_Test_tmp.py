# Train Model to predict city Areas

from sqlalchemy import create_engine
import pandas as pd
from Utils import GeneralPurposeModels as gen
from Utils import Database as d
import os
import numpy as np
from dotenv import load_dotenv
import matplotlib.pyplot as plt

# Instantiate Database
load_dotenv('App.env')
database_user = os.getenv('DATABASE_USER')
database_password = os.getenv('DATABASE_PASSWORD')
database_port = os.getenv('DATABASE_PORT')
database_db = os.getenv('DATABASE_DB')
# Instantiate the DB
database = d.Database(database_user, database_password, database_port, database_db)

city = 'Milano'

# Houses DB
dataH = database.getDataFromLocalDatabase("offerDetailDatabase_"+ city)
# Geo DB
dataG = database.getDataFromLocalDatabase("geoData_"+ city)

data = pd.merge(left=dataH[['Adress', 'Area']], right=dataG[['Address','Latitude','Longitude']],
                             left_on='Adress', right_on='Address', how='inner').drop_duplicates().dropna().reset_index(drop=True)
# Train Model
areaPred = gen.generalPurposeModels(city).trainModelForAreaPrediction(data, test_size=0.20,
                                                                    coord_filters = [45.40, 45.55, 9.10, 9.26],
                                                                    model = 'KNN')

# PREDICT
# Now, get the data with Coordinates and no Area
dataNoArea = pd.merge(left=dataG[['Address','Latitude','Longitude']], right=dataH[['Adress','Area']],
                       left_on='Address', right_on='Adress', how='left').drop_duplicates().reset_index(drop=True)
dataNoArea = dataNoArea[['Area', 'Latitude', 'Longitude']].drop_duplicates().reset_index(drop=True)
# Filter for the city
dataNoArea = dataNoArea[((dataNoArea['Latitude'] > 45.40) &
                                       (dataNoArea['Latitude'] < 45.55)) & ((dataNoArea['Longitude'] < 9.26) &
                                       (dataNoArea['Longitude'] > 9.10))].reset_index(drop=True)
dataNoArea = dataNoArea[dataNoArea['Area'].isna()].reset_index(drop=True)

# Prediction
predictedAreas = gen.generalPurposeModels(city).predictAreaFromCoordinates(np.array(dataNoArea[['Latitude',
                                                                                        'Longitude']]), model='KNN')
# See Predictions
reference = pd.concat([dataNoArea[['Latitude','Longitude']],
                 pd.DataFrame(predictedAreas).set_axis(['Area'], axis=1)], axis = 1)
# Encode Areas
encodeData = []
for i, singleArea in enumerate(reference['Area'].unique()):
    df = pd.DataFrame(
        pd.concat([pd.Series(singleArea), pd.Series(i)], axis=1).set_axis(['Area', 'code'], axis=1))
    encodeData.append(df)
encodeData = pd.concat([sdf for sdf in encodeData]).reset_index(drop=True)
# Translate codes
for ar in range(len(encodeData['Area'])):
    reference.loc[reference['Area'] == encodeData['Area'][ar], 'Area_enc'] = encodeData['code'][ar]

# Plot
plt.figure(figsize=(15, 8))
plt.scatter(reference['Latitude'], reference['Longitude'], c=reference["Area_enc"], cmap="viridis")
#plt.scatter(notAvailable['Latitude'], notAvailable['Longitude'], marker='x', color = 'red', label='Not Available', s=7)
plt.show()
