# Class to try to compute car and public transport distance from Coordinates
# Seven distances must be computed:
# - Distance as the crow flies from Address to the center
# - Distance as the crow flies from Address to nearest limit of the city center
# - Distance as the crow flies from Address to the nearest underground station
# - Distance with public transports from Address to the city centre
# - Distance with public transports from Address to nearest limit of the city center
# - Distance with the car from Address to the city centre
# - Distance with the car from Address to nearest limit of the city center
import math

import pandas as pd
import numpy as np
from datetime import datetime
from Utils import Database as d
import os
from dotenv import load_dotenv
from scipy.spatial import ConvexHull, Delaunay
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
from geopy.distance import geodesic
import requests

class distanceCalculationService:
    def __init__(self, city):
        self.city = city
        pass

    # utils-like methods to compute distance having latitude and longitude

    def getIfPointIsInCityCenter (self, boundaryPoints, testPoint):

        # Create Delaunay Structure
        hull_region = Delaunay(boundaryPoints)
        # Verify if a given point is inside the Hull Region (== city Center)
        isInCityCenter = hull_region.find_simplex(testPoint) >= 0

        return isInCityCenter

    # Distance ACF
    def computeDistanceACF (self, coords1, coords2):

        # order: Latitude, Longitude
        # Coords2: points from where the distance has to be computed
        # Coords1: main point

        distance = geodesic(coords1, coords2).kilometers

        return distance

    def computeDistanceWithCar (self, coords1, coords2):

        # Coords must be in format "latitude, longitude"
        start = str(coords1[0]) + ',' + str(coords1[1])
        end = str(coords2[0]) + ',' + str(coords2[1])

        # Get the URL from OpenStreetMap
        url = f"http://router.project-osrm.org/route/v1/driving/{start};{end}?overview=false"

        # get request from API
        response = requests.get(url)
        data = response.json()

        # Get the distance in km
        distance = data['routes'][0]['distance'] / 1000

        return distance

    # Car-distance by Car (in minutes)
    def computeDistanceTime (self, coords1, coords2, by='car'):

        lat1, lon1 = coords1[0], coords1[1]
        lat2, lon2 = coords2[0], coords2[1]

        mode = by  # Available: "foot", "bike"
        url = f"http://router.project-osrm.org/route/v1/{mode}/{lon1},{lat1};{lon2},{lat2}?overview=false"

        response = requests.get(url)
        data = response.json()

        travel_time_minutes = math.nan
        if "routes" in data:
            #distance_km = data["routes"][0]["distance"] / 1000  # Converti in km
            travel_time_minutes = data["routes"][0]["duration"] / 60  # Converti in min
        else:
            print("No data for selected coordinates!")

        return travel_time_minutes


    # Utils-Like Method to filter for cities Boundaries
    def filterForCityBoundaries (self, dataG):

        # DataG stands for geoData
        # Filter for city boundaries, and drop duplicates if present
        if self.city == 'Milano':
            dataG = dataG[((dataG['Latitude'] > 45.40) & (dataG['Latitude'] < 45.55)) &
                          ((dataG['Longitude'] < 9.26) & (dataG['Longitude'] > 9.10))].reset_index(drop=True)
        elif self.city == 'Roma':
            dataG = dataG[((dataG['Latitude'] > 41.70) & (dataG['Latitude'] < 42.05)) &
                          ((dataG['Longitude'] > 12.20) & (dataG['Longitude'] < 12.75))].reset_index(drop=True)
        elif self.city == 'Genova':
            dataG = dataG[((dataG['Latitude'] > 44) & (dataG['Latitude'] < 45)) &
                          ((dataG['Longitude'] > 8.75) & (dataG['Longitude'] < 9.1))].reset_index(drop=True)
        elif self.city == 'Torino':
            dataG = dataG[((dataG['Latitude'] > 45.0) & (dataG['Latitude'] < 45.14)) &
                          ((dataG['Longitude'] > 7.6) & (dataG['Longitude'] < 7.750))].reset_index(drop=True)
        elif self.city == 'Firenze':
            dataG = dataG[((dataG['Latitude'] > 43.7) & (dataG['Latitude'] < 43.9)) &
                          ((dataG['Longitude'] > 11.0) & (dataG['Longitude'] < 11.4))].reset_index(drop=True)
        elif self.city == 'Bologna':
            dataG = dataG[((dataG['Latitude'] > 44.4) & (dataG['Latitude'] < 44.6)) &
                          ((dataG['Longitude'] > 11.2) & (dataG['Longitude'] < 11.45))].reset_index(drop=True)
        elif self.city == 'Napoli':
            dataG = dataG[((dataG['Latitude'] > 40.7) & (dataG['Latitude'] < 41.0)) &
                          ((dataG['Longitude'] > 14.1) & (dataG['Longitude'] < 14.5))].reset_index(drop=True)
        elif self.city == 'Palermo':
            dataG = dataG[((dataG['Latitude'] > 38) & (dataG['Latitude'] < 40.0)) &
                          ((dataG['Longitude'] > 13.2) & (dataG['Longitude'] < 13.55))].reset_index(drop=True)
        elif self.city == 'Catania':
            dataG = dataG[((dataG['Latitude'] > 37.45) & (dataG['Latitude'] < 37.6)) &
                          ((dataG['Longitude'] > 15.0) & (dataG['Longitude'] < 15.13))].reset_index(drop=True)
        else:
            raise Exception('City not Valid!')
        return dataG

    # Utils-like method to have a city center proxy
    def getCityCentreFromHousePrices(self, plot=False):

        # Instantiate the DB
        load_dotenv('App.env')
        database_user = os.getenv('DATABASE_USER')
        database_password = os.getenv('DATABASE_PASSWORD')
        database_port = os.getenv('DATABASE_PORT')
        database_db = os.getenv('DATABASE_DB')
        database = d.Database(database_user, database_password, database_port, database_db)
        dataG = database.getDataFromLocalDatabase("geoData_" + self.city)
        dataH = database.getDataFromLocalDatabase("offerDetailDatabase_" + self.city)

        dataG = self.filterForCityBoundaries(dataG)
        dataG = dataG.dropna()

        # Now, merge the houses Database to take the adress of the houses
        housesAddress = pd.merge(left=dataH[['Adress', 'Area', 'Price per square meter']], right=dataG,
                                 left_on='Adress', right_on='Address',
                                 how='left').drop_duplicates().dropna().reset_index(drop=True)

        # Get the area price
        areaPrice = housesAddress[['Area', 'Price per square meter']].groupby('Area', as_index=False).mean()
        areaPrice = areaPrice.sort_values(by='Price per square meter', ascending=False).reset_index(drop=True)
        # print(areaPrice)
        centerAreas = list(areaPrice['Area'][0:int(len(areaPrice['Area']) * 0.20)])

        # Filter for the Most Expensive Areas
        for centerArea in centerAreas:
            housesAddress.loc[housesAddress['Area'] == centerArea, 'center'] = 1
            housesAddress['center'] = housesAddress['center'].fillna(0)

        # Drop Ouliers on the center Areas with the centroid method
        df_centre = housesAddress[housesAddress['center'] == 1].reset_index(drop=True)
        # print('pre-outliers:', len(df_centre['Address']))
        centroid = df_centre[['Latitude', 'Longitude']].mean().values
        distances = cdist(df_centre[['Latitude', 'Longitude']], [centroid])

        # Remove Outliers
        threshold = 2 * distances.std()
        filteredAddress = df_centre[distances.flatten() < threshold]
        outliers = df_centre[distances.flatten() > threshold]
        outliers.loc[outliers['center'] == 1, 'center'] = 0

        # print('post-outliers removal:', len(filteredAddress['Address']))
        housesAddress = pd.concat([housesAddress[housesAddress['center'] == 0].reset_index(drop=True),
                                   outliers, filteredAddress], axis=0).drop_duplicates().reset_index(drop=True)
        # Plot

        housesAddress = housesAddress[['Address', 'Area', 'Price per square meter', 'Latitude', 'Longitude', 'center']]

        # Now, create an area of each point inside the cloud representing the City Center. A city may have many city centres (as Roma)
        # For now, we have to assume that the city centre coincides with the priciest area.

        # Compute the central Area with the Convex Hull
        nuvola = housesAddress[housesAddress['center'] == 1][['Latitude', 'Longitude']].values
        # Compute Convex Hull
        hull = ConvexHull(nuvola)
        # Index on the convex hull border
        boundary_indices = hull.vertices
        # Points on the border
        boundary_points = nuvola[boundary_indices]

        # Plot
        if plot:
            plt.figure(figsize=(12, 8))
            plt.scatter(housesAddress['Longitude'], housesAddress['Latitude'], c=housesAddress['center'], cmap='coolwarm')
            plt.xlabel('Longitude')
            plt.ylabel('Latitude')
            for simplex in hull.simplices:
                plt.plot(nuvola[simplex, 1], nuvola[simplex, 0], 'k-')  # Linee del Convex Hull
            plt.title('Houses Distribution VS Priciest Centre (city: ' + self.city + ')')
            plt.show()

        return boundary_points


    # 1. Distance as the crow flies from Address to the center
    # Implement in the next episode
    def computeDistanceFromCityCentre (self, type = 'ACF', subsample = 'all'):

        # Load the Houses Coordinates
        # Instantiate the Database
        load_dotenv('App.env')
        database_user = os.getenv('DATABASE_USER')
        database_password = os.getenv('DATABASE_PASSWORD')
        database_port = os.getenv('DATABASE_PORT')
        database_db = os.getenv('DATABASE_DB')
        db_name = 'DistanceCalculation_' + self.city + '_' + type

        # Instantiate the DB
        database = d.Database(database_user, database_password, database_port, database_db)
        # Get the geo database
        geoData = database.getDataFromLocalDatabase("geoData_" + self.city + "").dropna().drop_duplicates(subset = 'Address').reset_index(drop=True)
        geoData = self.filterForCityBoundaries(geoData)

        # Exclude already Processed Addresses (to avoid long calculations, and preserve the number of API requests)
        geoData = database.excludeAlreadyProcessedData(geoData, db_name, 'Address', logs = True)
        # Take a subsample if required
        if subsample != 'all':
            geoData = geoData[0:subsample]

        # City centre computed as the priciest area on house prices

        # get the city center points
        cityCentrePoints = self.getCityCentreFromHousePrices(plot = False)
        # compute distance from each points

        minimumDistance = []
        for i in range(len(geoData['Latitude'])):
            # Obtain the coordinates of each one of the houses
            coordSet = list([geoData['Latitude'][i], geoData['Longitude'][i]])
            distances = []
            for j in range(len(cityCentrePoints)):
                # Obtain the coordinates of each one of the boundary points of the city centre
                coordSet1 = cityCentrePoints[j]
                # get the nearest point to the city centre to speed up the algorithm
                cityCentreDistance = self.computeDistanceACF(coordSet, coordSet1)
                # If a Point is in city Center, then put 0 on distance
                if self.getIfPointIsInCityCenter(cityCentrePoints, coordSet):
                    cityCentreDistance = 0.0
                distances.append(cityCentreDistance)

            dataWithDistances = pd.concat([pd.DataFrame(cityCentrePoints),
                                           pd.DataFrame(distances).set_axis(['distance'], axis = 1)], axis = 1)
            # Use the minimum point distance for benchmark
            # Retrieve the coordinates relative to the minimum distance
            minimumPointDistance = dataWithDistances[[0, 1]][dataWithDistances['distance'] == np.min(distances)].values
            minimumPointDistance = minimumPointDistance.flatten().tolist()

            # If every point is 0, no need to compute the distance
            if dataWithDistances['distance'].eq(0).all():
                cityCentreDistance = 0.0
            else:
                if type == 'ACF':
                    cityCentreDistance = minimumPointDistance
                elif type == 'car':
                    cityCentreDistance = self.computeDistanceWithCar(coordSet, minimumPointDistance)
                elif type == 'car-time':
                    cityCentreDistance = self.computeDistanceTime(coordSet, minimumPointDistance)
                elif type == 'foot-time':
                    cityCentreDistance = self.computeDistanceTime(coordSet, minimumPointDistance, by='foot')
                elif type == 'bike-time':
                    cityCentreDistance = self.computeDistanceTime(coordSet, minimumPointDistance, by='bike')
                else:
                    raise Exception('Method Not Specified!!')
            minimumDistance.append(cityCentreDistance)

            # Logs and check
            if 'time' in type:
                print(str(round((i / len(geoData['Latitude'])) * 100, 2)) + '% - ' +
                      'Computing time from the city centre for Address: ' + geoData['Address'][i] + ' - City: ' +
                      self.city + ' - Time: ' + str(round(np.min(distances), 2)) + ' minutes')
            else:
                print(str(round((i / len(geoData['Latitude'])) * 100, 2)) + '% - ' +
                      'Computing Distance from the city centre for Address: ' + geoData['Address'][i] + ' - City: ' +
                      self.city + ' - Distance: ' + str(round(np.min(distances), 2)) + ' km')

        # Concat the house coordinated with the distance from city centre
        geoDataWithDist = pd.concat([geoData[['ID', 'Address', 'Latitude', 'Longitude']],
                                     pd.DataFrame(minimumDistance).set_axis(['Distance ' + type + ' from Center'], axis=1)], axis=1)

        # Save in the Database, if not existing, concatenate otherwise
        allTables = database.getAllTablesInDatabase()
        if allTables['table_name'].str.contains(db_name).any():
            database.appendDataToExistingTable(geoDataWithDist, db_name)
        else:
            database.createTable(geoDataWithDist, db_name)

        return geoDataWithDist





