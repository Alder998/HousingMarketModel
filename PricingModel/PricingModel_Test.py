import MasterDataGathering as m

city = 'Milano'
masterData = m.MasterDataGathering(city = city).getMasterDatabase(dangerIndexPredictionDataset = "newsDatabase",
                                                         dangerIndexModel = "bert-base-multilingual-cased",
                                                         distanceType = "car-time")
# DB Statistics
print('\n')
print('--- CITY: ' + city + '---')
print('Number of Houses Offers in Database: ' + f"{len(masterData['Address']):,}".replace(",", "."))
print('Number of Single Addresses in Database: ' + f"{len(masterData['Address'].unique()):,}".replace(",", "."))
