# Test the area danger Model

import areaDangerDataProcessing as dp
import areaDangerModel as dm

crimeDataForModel = dp.areaDangerProcessing('Milano').processDatasetForModel(returnType='CLS')
model = dm.areaDangerModel('Milano').NNModel(crimeDataForModel)

#print(crimeDataForModel)