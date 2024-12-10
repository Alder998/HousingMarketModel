# Class to process data to compute how dangerous a street is

from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from datetime import datetime
from Utils import Database as d
import os
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
import areaDangerModel as dm
import os
import torch

class areaDangerProcessing:
    def __init__(self, city):
        self.city = city
        pass

    def createBinaryCrimeDataset (self):

        load_dotenv('App.env')
        database_user = os.getenv('DATABASE_USER')
        database_password = os.getenv('DATABASE_PASSWORD')
        database_port = os.getenv('DATABASE_PORT')
        database_db = os.getenv('DATABASE_DB')

        # Instantiate the DB
        database = d.Database(database_user, database_password, database_port, database_db)
        data = database.getDataFromLocalDatabase("newsDatabase_" + self.city)

        # Drop Duplicates, remove articles without a topic
        data = data.drop_duplicates().reset_index(drop=True)
        data = data[(~data['Topics'].isna()) & (~data['Topics'].str.match(r'^\s*$', na=False))].reset_index(drop=True)
        # Database Stats
        print('Streets in Database:', len(data['Address'].unique()))
        print('Articles in Database:', len(data['Article']))
        # Filter for crime tags
        words = ['arresti', 'furti', 'droga', 'morti', 'incendi', 'omicidi', 'spaccio', 'denunce', 'accoltella',
                 'violenze', 'risse', 'inseguimenti', 'indagini', 'violenze sessuali', 'truffe', 'processi', 'spara', 'rapina']
        for word in words:
            data.loc[data['Topics'].str.contains(word), 'Crime'] = 1
        data['Crime'] = data['Crime'].fillna(0)

        # Encode the street name with the street Encoder from SQL
        load_dotenv('App.env')
        database_user = os.getenv('DATABASE_USER')
        database_password = os.getenv('DATABASE_PASSWORD')
        database_port = os.getenv('DATABASE_PORT')
        database_db = os.getenv('DATABASE_DB')
        # Instantiate the DB
        database = d.Database(database_user, database_password, database_port, database_db)
        encodingData = database.getDataFromLocalDatabase("geoData_" + self.city)
        encodedAdressData = pd.merge(left=data, right=encodingData, left_on='Address', right_on='Address', how='inner').drop_duplicates(subset=['Article', 'Address']).reset_index(drop=True)

        # Create the final database
        encodedAdressData = encodedAdressData[['Latitude', 'Longitude', 'Article', 'Crime']].drop_duplicates().reset_index(drop=True)

        print('Number of News after merge with coordinates:', len(encodedAdressData['Latitude']))
        print('Number of crime tags:', len(encodedAdressData['Latitude'][encodedAdressData['Crime'] == 1]))

        return encodedAdressData

    def trainTestSplit (self, data):

        # The data we receive here is a dictionary of tensors and output

        X_train, X_test, y_train, y_test = train_test_split(
            data['Embedding'], data['Output'], test_size=0.20, random_state=42, stratify=data['Output'])

        # Verify train and test set distribution
        dataOutput_train = pd.Series(y_train)
        dataOutput_test = pd.Series(y_test)
        # Log with the percentage Distribution
        print('Distribution of Outputs in train set: ', round((len(dataOutput_train[dataOutput_train == 1]) / len(dataOutput_train)) * 100, 3), '%')
        print('Distribution of Outputs in test set: ', round((len(dataOutput_test[dataOutput_test == 1]) / len(dataOutput_test)) * 100, 3), '%')

        return X_train, X_test, y_train, y_test

    def processDatasetForModel (self, returnType='CLS'):

        step1 = self.createBinaryCrimeDataset()
        path = "embeddings_sentences_" + returnType.lower() + ".pt"
        if os.path.exists(path):
            print('Loading data...')
            loaded_data = torch.load(path)
            step2 = self.trainTestSplit(loaded_data)
        else:
            step1_1 = dm.areaDangerModel(self.city).encodeTextVariablesInDataset(step1, returnType)
            step2 = self.trainTestSplit(step1_1)

        return step2





