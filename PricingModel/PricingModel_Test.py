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
                                                     predictors = ['Area','Size','Floor','Rooms','Toilets','DangerIndex',
                                                                   'Distance car-time from Center'],
                                                     outputCol = 'Price',
                                                     test_size = 0.25,
                                                     trainingEpochs = 200,
                                                     NNstructure = {'FF':[500, 500, 500]},
                                                     save = False)
