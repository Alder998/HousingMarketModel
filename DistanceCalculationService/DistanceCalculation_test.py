import DistanceCalculationService as dc

city = 'Milano'

dist = dc.distanceCalculationService(city).computeDistanceFromCityCentre(type = 'car-time')

print(dist)
