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
import tensorflow as tf

class areaDangerProcessing:
    def __init__(self, city):
        self.city = city
        pass

    def createBinaryCrimeDataset (self, dataRaw, subsample=1, predict=False):

        # Import and Instantiate the Database Object
        load_dotenv('App.env')
        database_user = os.getenv('DATABASE_USER')
        database_password = os.getenv('DATABASE_PASSWORD')
        database_port = os.getenv('DATABASE_PORT')
        database_db = os.getenv('DATABASE_DB')
        # Instantiate the DB
        database = d.Database(database_user, database_password, database_port, database_db)

        # Apply subsample database + save the validation set (the one on which we are making the predictions)
        # Each one of the street must be count in the validation Dataset

        if predict == False:
            data = []
            for ad in dataRaw['Address'].unique():
                dataS = dataRaw[dataRaw['Address'] == ad].reset_index(drop=True)
                dataTrimmed = dataS[0 : int(round(len(dataS['Address'])*subsample, 0))]
                data.append(dataTrimmed)
            data = pd.concat([df for df in data], axis = 0).reset_index(drop=True)

            # Take care of the validation Dataset, using the news as discriminator
            dataForValidation = dataRaw[~dataRaw['Article'].isin(data['Article'])]
            # Save or update the validation set
            db_name = 'crimeValidationSet_'+self.city
            allTables = database.getAllTablesInDatabase()
            if allTables['table_name'].str.contains(db_name).any():
                database.appendDataToExistingTable(dataForValidation, db_name)
            else:
                database.createTable(dataForValidation, db_name)
        else:
            data = dataRaw

        # Drop Duplicates, remove articles without a topic
        data = data.drop_duplicates().reset_index(drop=True)
        data = data[(~data['Topics'].isna()) & (~data['Topics'].str.match(r'^\s*$', na=False))].reset_index(drop=True)
        # Database Stats - Model
        print('Streets in Database:', len(data['Address'].unique()))
        print('Articles in Database:', len(data['Article']))

        if predict==False:
            # Database Stats - Validation
            print('Streets in Validation Database:', len(dataForValidation['Address'].unique()))
            print('Articles in Validation Database:', len(dataForValidation['Article']))

        # Filter for crime tags
        words = pd.read_excel(r"C:\Users\alder\Downloads\Danger.xlsx")
        words = list(words['Words'][words['Danger'] == 1].reset_index(drop=True))
        for word in words:
            data.loc[data['Topics'].str.contains(word), 'Crime'] = 1
        data['Crime'] = data['Crime'].fillna(0)

        # Encode the street name with the street Encoder from SQL
        encodingData = database.getDataFromLocalDatabase("geoData_" + self.city)
        encodedAdressData = pd.merge(left=data, right=encodingData, left_on='Address', right_on='Address', how='inner').drop_duplicates(subset=['Article', 'Address']).reset_index(drop=True)

        # Create the final database
        encodedAdressData = encodedAdressData[['Latitude', 'Longitude', 'Article', 'Crime']].drop_duplicates().reset_index(drop=True)

        print('Number of News after merge with coordinates:', len(encodedAdressData['Latitude']))
        print('Number of crime tags:', len(encodedAdressData['Latitude'][encodedAdressData['Crime'] == 1]))

        return encodedAdressData

    def trainTestSplit (self, data, test_size=0.20):

        # The data we receive here is a dictionary of tensors and output

        X_train, X_test, y_train, y_test = train_test_split(
            data['Embedding'], data['Output'], test_size=test_size, random_state=42, stratify=data['Output'])

        # Verify train and test set distribution
        dataOutput_train = pd.Series(y_train)
        dataOutput_test = pd.Series(y_test)
        # Log with the percentage Distribution
        print('Distribution of Outputs in train set: ', round((len(dataOutput_train[dataOutput_train == 1]) / len(dataOutput_train)) * 100, 3), '%')
        print('Distribution of Outputs in test set: ', round((len(dataOutput_test[dataOutput_test == 1]) / len(dataOutput_test)) * 100, 3), '%')

        return X_train, X_test, y_train, y_test

    def processDatasetForModel (self, model="bert-base-uncased", returnType='cls', subsample=1, test_size=0.20):

        # Get the data
        load_dotenv('App.env')
        database_user = os.getenv('DATABASE_USER')
        database_password = os.getenv('DATABASE_PASSWORD')
        database_port = os.getenv('DATABASE_PORT')
        database_db = os.getenv('DATABASE_DB')

        # Instantiate the DB
        database = d.Database(database_user, database_password, database_port, database_db)
        dataRaw = database.getDataFromLocalDatabase("newsDatabase_" + self.city)

        step1 = self.createBinaryCrimeDataset(dataRaw, subsample=subsample)
        path = "embeddings_sentences_" + returnType.lower() + ".pt"
        if os.path.exists(path):
            print('Loading data...')
            loaded_data = torch.load(path)
            step2 = self.trainTestSplit(loaded_data, test_size)
        else:
            step1_1 = dm.areaDangerModel(self.city).encodeTextVariablesInDataset(step1, model, returnType)
            step2 = self.trainTestSplit(step1_1, test_size)

        return step2

    def predictDangerFromNews (self, prediction_set, model="bert-base-uncased", returnType='cls'):

        # Import the validation dataset from SQL
        load_dotenv('App.env')
        database_user = os.getenv('DATABASE_USER')
        database_password = os.getenv('DATABASE_PASSWORD')
        database_port = os.getenv('DATABASE_PORT')
        database_db = os.getenv('DATABASE_DB')

        # Instantiate the DB
        # 'crimeValidationSet_'+self.city
        database = d.Database(database_user, database_password, database_port, database_db)
        dataForValidation = database.getDataFromLocalDatabase(prediction_set)

        if prediction_set == 'newsDatabase_' + self.city:
            path = "embeddings_sentences_" + returnType.lower() + ".pt"
            validationSetEmbedding = torch.load(path)
            validationSetEmbedding = np.vstack([tensor.squeeze(0).cpu().numpy() for tensor in validationSetEmbedding['Embedding']])
            validationSetEmbedding = validationSetEmbedding.astype(np.float32)
        else:
            # Encode the Validation Set
            validationSetBinary = self.createBinaryCrimeDataset(dataForValidation, subsample=1, predict=True)

            # Create the Embedding for the Set
            validationSetEmbedding = dm.areaDangerModel(self.city).encodeTextVariablesInDataset(validationSetBinary, model,
                                                                                                returnType, predict=True)
            # Adjust the Data to be processed and convert to numbers (if necessary)
            validationSetEmbedding = np.vstack([tensor.squeeze(0).cpu().numpy() for tensor in validationSetEmbedding['Embedding']])
            validationSetEmbedding = validationSetEmbedding.astype(np.float32)

        # Get the Saved Model
        storedModel = tf.keras.models.load_model('CrimeModel_'+ returnType.lower() +'.h5')

        # Use it to predict probabilities
        modelPrediction = storedModel.predict(validationSetEmbedding)
        # Create the Crime Prediction Dataset
        crimePredData = []
        for i, prediction in enumerate(modelPrediction):
            singleRow = pd.concat([pd.Series(dataForValidation['Address'][i]),
                                   pd.Series(prediction[1])], axis = 1).set_axis(['Address', 'DangerIndex'], axis = 1)
            crimePredData.append(singleRow)
        crimePredData = pd.concat([df for df in crimePredData], axis = 0)

        # Save on SQL
        db_name = 'dangerPredictionSet_' + self.city
        allTables = database.getAllTablesInDatabase()
        if allTables['table_name'].str.contains(db_name).any():
            database.appendDataToExistingTable(crimePredData, db_name)
        else:
            database.createTable(crimePredData, db_name)

        return crimePredData






