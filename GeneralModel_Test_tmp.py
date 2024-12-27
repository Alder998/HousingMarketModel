# Train Model to predict city Areas

from sqlalchemy import create_engine
import pandas as pd
from Utils import GeneralPurposeModels as gen

city = 'Milano'

# Houses DB
engine = create_engine('postgresql://postgres:Lavagna123!@localhost:5432/housingMarketModel')
query = 'SELECT * FROM public."offerDetailDatabase_'+ city + '"'
dataH = pd.read_sql(query, engine)
# Geo DB
engine = create_engine('postgresql://postgres:Lavagna123!@localhost:5432/housingMarketModel')
query = 'SELECT * FROM public."geoData_' + city + '"'
dataG = pd.read_sql(query, engine)

data = pd.merge(left=dataH[['Adress', 'Area']], right=dataG[['Address','Latitude','Longitude']],
                             left_on='Adress', right_on='Address', how='inner').drop_duplicates().dropna().reset_index(drop=True)

areaPred = gen.generalPurposeModels(city).trainModelForAreaPrediction(data, test_size=0.20,
                                                                    coord_filters = [45.40, 45.55, 9.10, 9.26])

