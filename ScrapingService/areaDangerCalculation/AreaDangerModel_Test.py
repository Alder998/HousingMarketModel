# Test the area danger Model

import areaDangerDataProcessing as dp

crimeDataForModel = dp.areaDangerProcessing('Milano').processDatasetForModel(returnType='CLS')

#print(crimeDataForModel)