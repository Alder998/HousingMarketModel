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

        # data is the encoded data from the function createBinaryCrimeDataset

        predictor = np.array(data['Crime']).reshape(len(data['Crime']), 1)
        features = np.array(data[['Latitude','Longitude']]).reshape(len(data['Crime']), 2)
        x_train, x_test, y_train, y_test = train_test_split(
            features, predictor, test_size=0.20, random_state=1893, stratify=predictor)

        # Analytics for train and test set
        dataForStats_train = pd.concat([pd.DataFrame(y_train).set_axis(['Pred'], axis = 1), pd.DataFrame(x_train)], axis = 1)
        dataForStats_test = pd.concat([pd.DataFrame(y_test).set_axis(['Pred'], axis = 1), pd.DataFrame(x_test)], axis = 1)
        percPred_train = len(dataForStats_train[0][dataForStats_train['Pred'] == 1]) / len(dataForStats_train[0])
        percPred_test = len(dataForStats_test[0][dataForStats_test['Pred'] == 1]) / len(dataForStats_test[0])
        print('Percentage of Predictor in Train set:', round(percPred_train*100, 2), '%')
        print('Percentage of Predictor in Test set:', round(percPred_test*100, 2), '%')

        return x_train, x_test, y_train, y_test

    def processDatasetForModel (self):

        step1 = self.createBinaryCrimeDataset()
        step1_1 = dm.areaDangerModel(self.city).encodeTextVariablesInDataset()
        #step2 = self.trainTestSplit(step1)

        return step1_1





