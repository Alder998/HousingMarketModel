import DistanceCalculationService as dc

city = 'Milano'

# Possible Values for Type: 'car-time' | 'ACF' | 'car'
dist = dc.distanceCalculationService(city).computeDistanceFromCityCentre(type = 'bike-time', subsample = 1500)

print(dist)
