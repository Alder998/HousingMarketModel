import MasterDataGathering as m
import PricingModel as p


city = 'Milano'
masterData = m.MasterDataGathering(city = city).getMasterDatabase(dangerIndexPredictionDataset = "newsDatabase",
                                                         dangerIndexModel = "bert-base-multilingual-cased",
                                                         distanceType = "car-time")

# DB Statistics
print('\n')
print('--- CITY: ' + city + '---')
print('Number of Houses Offers in Database: ' + f"{len(masterData['Address']):,}".replace(",", "."))
print('Number of Single Addresses in Database: ' + f"{len(masterData['Address'].unique()):,}".replace(",", "."))

model = p.PricingModel().createOrUpdatePricingModel (city = city,
                                                     data = masterData,
                                                     predictors = ['Size','Floor','Rooms','Toilets'],
                                                     outputCol = 'Price',
                                                     test_size = 0.25,
                                                     trainingEpochs = 100,
                                                     NNstructure = {'FF':[500, 500, 500]},
                                                     save = False)
