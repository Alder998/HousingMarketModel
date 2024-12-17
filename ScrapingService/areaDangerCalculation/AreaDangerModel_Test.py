# Test the area danger Model

import areaDangerDataProcessing as dp
import areaDangerModel as dm

# Model Trainer (if not trained)
crimeDataForModel = dp.areaDangerProcessing('Milano').processDatasetForModel(model="bert-base-multilingual-cased", returnType='mean',
                                                                             subsample=0.75, test_size=0.33)
model = dm.areaDangerModel('Milano').trainAndStoreNNModelForNews(crimeDataForModel, trainingEpochs=100,
                                                                 structure=[300, 300, 300, 300], returnType='mean')

predicted = dp.areaDangerProcessing('Milano').predictDangerFromNews(model="bert-base-multilingual-cased", returnType='mean')

# Create the Dataset of street Danger