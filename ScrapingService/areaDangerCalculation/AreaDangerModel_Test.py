# Test the area danger Model

import areaDangerDataProcessing as dp
import areaDangerModel as dm

# Model Trainer (if not trained)
#crimeDataForModel = dp.areaDangerProcessing('Milano').processDatasetForModel(returnType='cls', test_size=0.33)
#model = dm.areaDangerModel('Milano').trainAndStoreNNModelForNews(crimeDataForModel, trainingEpochs=100, structure=[300, 300, 300, 300], returnType='cls')

# Create the Dataset of street Danger