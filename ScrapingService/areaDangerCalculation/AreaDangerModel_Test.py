# Test the area danger Model

import areaDangerDataProcessing as dp
import areaDangerModel as dm
import os

returnType = 'mean'
city = 'Milano'

# Model Trainer (if not trained)
crimeDataForModel = dp.areaDangerProcessing(city).processDatasetForModel(model="bert-base-multilingual-cased", returnType=returnType,
                                                                             subsample=0.75, test_size=0.33)
# Train only if is not stored
path = "CrimeModel_" + returnType.lower() + ".h5"
if not os.path.exists(path):
    model = dm.areaDangerModel(city).trainAndStoreNNModelForNews(crimeDataForModel, trainingEpochs=100,
                                                    structure=[300, 300, 300, 300], returnType=returnType)
else:
    print('Using Model' + " CrimeModel_" + returnType.lower() + ".h5...")

predicted = dp.areaDangerProcessing(city).predictDangerFromNews(model="bert-base-multilingual-cased",
                                                    prediction_set="newsDatabase_" + city, returnType=returnType)
# 'crimeValidationSet_'+'Milano' for validation
# 'newsDatabase_' + city for all news
# Create the Dataset of street Danger