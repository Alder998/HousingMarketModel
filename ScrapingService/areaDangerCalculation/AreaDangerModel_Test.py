# Test the area danger Model

import areaDangerDataProcessing as dp
import areaDangerModel as dm
import os
from dotenv import load_dotenv
from Utils import Database as d

returnType = 'mean'
city = 'Milano'
subsample = 0.80
test_size = 0.30

# Model Trainer (if not trained)
crimeDataForModel = dp.areaDangerProcessing(city).processDatasetForModel(model="bert-base-multilingual-cased", returnType=returnType,
                                                                             subsample=subsample, test_size=test_size)
# Train only if is not stored
path = "CrimeModel_" + returnType.lower() + ".h5"
if not os.path.exists(path):
    model = dm.areaDangerModel(city).trainAndStoreNNModelForNews(crimeDataForModel, trainingEpochs=100,
                                                    structure=[300, 300, 300, 300], returnType=returnType)
else:
    print('Using Model' + " CrimeModel_" + returnType.lower() + ".h5...")

# Create Predictions for each different cities

# Import and Instantiate the Database Object
load_dotenv('App.env')
database_user = os.getenv('DATABASE_USER')
database_password = os.getenv('DATABASE_PASSWORD')
database_port = os.getenv('DATABASE_PORT')
database_db = os.getenv('DATABASE_DB')
# Instantiate the DB
database = d.Database(database_user, database_password, database_port, database_db)
availableCities = database.getAllTablesInDatabase()
availableCities = availableCities[availableCities['table_name'].str.contains("geoData_")].reset_index(drop=True)
availableCities = availableCities['table_name'].str.split('_').str[1]
encodingData = []
for cityS in availableCities:
    predicted = dp.areaDangerProcessing(city).predictDangerFromNews(model="bert-base-multilingual-cased",
                                                        prediction_set="newsDatabase_" + cityS, returnType=returnType)
# 'crimeValidationSet_'+'Milano' for validation
# 'newsDatabase_' + city for all news
# Create the Dataset of street Danger