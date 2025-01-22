# Class to try to compute car and public transport distance from Coordinates
# Seven distances must be computed:
# - Distance as the crow flies from Address to the center
# - Distance as the crow flies from Address to nearest limit of the city center
# - Distance as the crow flies from Address to the nearest underground station
# - Distance with public transports from Address to the city centre
# - Distance with public transports from Address to nearest limit of the city center
# - Distance with the car from Address to the city centre
# - Distance with the car from Address to nearest limit of the city center

import pandas as pd
import numpy as np
from datetime import datetime
from Utils import Database as d
import os
from dotenv import load_dotenv
from scipy.spatial import ConvexHull
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt

class distanceCalculationService:
    def __init__(self, city):
        self.city = city
        pass

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

        # Filter for Milan city boundaries, and drop duplicates if present
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
    def computeDistanceACFFromCityCentre (self):

        return 0





