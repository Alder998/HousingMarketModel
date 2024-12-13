# Test the area danger Model

import areaDangerDataProcessing as dp
import areaDangerModel as dm

crimeDataForModel = dp.areaDangerProcessing('Milano').processDatasetForModel(returnType='CLS', test_size=0.33)
model = dm.areaDangerModel('Milano').trainAndStoreNNModelForNews(crimeDataForModel, trainingEpochs=100, structure=[300, 300,
                                                                                300, 300])

print(model)