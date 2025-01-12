# Test the area danger Model

import areaDangerDataProcessing as dp
import areaDangerModel as dm
import os
from dotenv import load_dotenv
from Utils import Database as d

returnType = 'mean'
subsample = 0.80
test_size = 0.30
prediction_set = 'newsDatabase' # Possible values: 'newsDatabase' | 'crimeValidationSet'

# Model Trainer (if not trained)
crimeDataForModel = dp.areaDangerProcessing().processDatasetForModel(model="bert-base-multilingual-cased", returnType=returnType,
                                                                             subsample=subsample, test_size=test_size)
# Train only if is not stored
path = "CrimeModel_" + returnType.lower() + ".h5"
if not os.path.exists(path):
    model = dm.areaDangerModel().trainAndStoreNNModelForNews(crimeDataForModel, trainingEpochs=100,
                                                    structure=[300, 300, 300, 300], returnType=returnType)
else:
    print('Using Model' + " CrimeModel_" + returnType.lower() + ".h5...")

# Create Predictions for each different cities

# Import and Instantiate the Database Object
# crimeValidationSet

# Get the data
load_dotenv('App.env')
database_user = os.getenv('DATABASE_USER')
database_password = os.getenv('DATABASE_PASSWORD')
database_port = os.getenv('DATABASE_PORT')
database_db = os.getenv('DATABASE_DB')

# Instantiate the DB
database = d.Database(database_user, database_password, database_port, database_db)

predicted = dp.areaDangerProcessing().predictDangerFromNews(model="bert-base-multilingual-cased",
                                                        prediction_set=prediction_set, returnType=returnType)
# 'crimeValidationSet' for validation Dataset (not processed by the model Previously)
# 'newsDatabase_' + city for all news
# Create the Dataset of street Danger