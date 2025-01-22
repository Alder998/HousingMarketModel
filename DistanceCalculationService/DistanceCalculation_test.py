import DistanceCalculationService as dc

city = 'Roma'

dist = dc.distanceCalculationService(city).getCityCentreFromHousePrices(plot=True)

print(dist)
