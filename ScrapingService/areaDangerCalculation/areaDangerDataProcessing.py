# Class to process data to compute how dangerous a street is

from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from datetime import datetime
from Utils import Database as d
import os
from dotenv import load_dotenv

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
        encodingData = database.getDataFromLocalDatabase("offerDetailDatabase_" + self.city)
        encodedAdressData = pd.merge(left=data, right=encodingData, left_on='Address', right_on='Adress', how='inner')

        # Create the final database
        encodedAdressData = encodedAdressData[['ID', 'Article', 'Crime']].drop_duplicates().reset_index(drop=True)

        print('Number of crime tags:', len(encodedAdressData['ID'][encodedAdressData['Crime'] == 1]))

        return encodedAdressData
