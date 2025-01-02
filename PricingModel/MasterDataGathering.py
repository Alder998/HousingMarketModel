# Class to get Master data, i.e., House Database, Geo Database, Danger Index from News, Distance From Center Database,
# And Parameter Selection

import pandas as pd
from Utils import Database as d
import os
import numpy as np
from dotenv import load_dotenv

class MasterDataGathering:

    def __init__(self, city):
        self.city = city

    # Function to get all the data
    def getMasterDatabase(self):

        # Instantiate Database
        load_dotenv('App.env')
        database_user = os.getenv('DATABASE_USER')
        database_password = os.getenv('DATABASE_PASSWORD')
        database_port = os.getenv('DATABASE_PORT')
        database_db = os.getenv('DATABASE_DB')
        # Instantiate the DB
        database = d.Database(database_user, database_password, database_port, database_db)

        # Get all the single tables
        # Houses
        houses = database.getDataFromLocalDatabase("offerDetailDatabase_" + self.city)
        # Geographical Coordinates
        geo = database.getDataFromLocalDatabase("geoData_" + self.city)
        # Danger Index (from News Model)
        dangerIndex = database.getDataFromLocalDatabase("dangerPredictionSet_" + self.city)
        # Distance Calculation
        distance = database.getDataFromLocalDatabase("distanceCalculation_" + self.city)

        # Remove once the distance DB has been created
        return 0
