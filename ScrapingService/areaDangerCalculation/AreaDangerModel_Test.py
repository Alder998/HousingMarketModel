# Test the area danger Model

import areaDangerDataProcessing as dp

crimeDataForModel = dp.areaDangerProcessing('Milano').createBinaryCrimeDataset()

print(crimeDataForModel)