# Class to get Master data, i.e., House Database, Geo Database, Danger Index from News, Distance From Center Database,
# And Parameter Selection
import math

import pandas as pd
from Utils import Database as d
import os
import numpy as np
from dotenv import load_dotenv

class MasterDataGathering:

    def __init__(self, city):
        self.city = city

    # Function to get all the data
    def getMasterDatabase (self, dangerIndexPredictionDataset = "newsDatabase",
                          dangerIndexModel = "bert-base-multilingual-cased", distanceType='car-time'):

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

        # Calculated fields
        # Danger Index (from News Model)
        dangerIndex = database.getDataFromLocalDatabase("dangerPredictionSet_" + dangerIndexPredictionDataset + "_" +
                                                        dangerIndexModel)
        # Aggregate for address (multiple scores for each address)
        dangerIndex = dangerIndex.groupby('Address', as_index=False).mean()

        # Distance Calculation
        distance = database.getDataFromLocalDatabase('DistanceCalculation_' + self.city + '_' + distanceType)
        # Get the column that contains the word "Distance"
        selectedColumns = []
        for column in distance.columns:
            if ('distance' in column.lower()) | ('address' in column.lower()):
                selectedColumns.append(column)
        distance = distance[selectedColumns]

        # Merge the DBs
        dataHG = pd.merge(left=houses, right=geo, left_on='Adress', right_on='Address',
                          how='inner').drop_duplicates(subset=['Adress', 'Price']).reset_index(drop=True)
        dataHGD = pd.merge(left=dataHG, right=dangerIndex, left_on='Address', right_on='Address',
                          how='inner')
        dataHGDD = pd.merge(left=dataHGD, right=distance, left_on='Address', right_on='Address',
                          how='inner')
        # Drop the link column
        dataHGDD = dataHGDD.drop(columns=['link'])
        dataHGDD = self.encodeStringVariables(dataHGDD)

        return dataHGDD

    # Function to encode the string Variables into Categorical ones
    def encodeStringVariables (self, data):

        # Get the columns that can be string
        stringColumns = []
        for col in data.columns:
            checkString = pd.to_numeric(data[col], errors='coerce')
            if checkString.isna().any():
                stringColumns.append(col)
            else:
                data[col] = pd.to_numeric(data[col], errors='coerce')

        for col1 in stringColumns:
            column = data[col1]
            # sort the values to preserve the order
            column = column.sort_values(ascending = True)
            for i, uniqueValue in enumerate(column.unique()):
                data.loc[data[col1] == uniqueValue, col1] = i

        return data



