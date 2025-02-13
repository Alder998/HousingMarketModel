# Utils file to get, create, manage SQL Data

from sqlalchemy import create_engine
import psycopg2
import pandas as pd

class Database:
    def __init__(self, user, password, port, db):
        self.user = user
        self.password = password
        self.port = port
        self.db = db
        pass

    # generalized method to get data from existing DB
    def getDataFromLocalDatabase (self, tableName):
        engine = create_engine('postgresql://' + self.user + ':' + self.password + '@localhost:' + self.port + '/' + self.db)
        query = 'SELECT * FROM public."' + tableName + '"'
        data = pd.read_sql(query, engine)
        return data

    def createTable (self, data, newTableName, check_rows=True, if_exist='append'):

        if check_rows:
            # Check if the table already exists
            allTables = self.getAllTablesInDatabase()
            if allTables['table_name'].str.contains(newTableName).any():
                raise Exception('ERROR: Table Already Present in the Database! It is recommended to use an append method!')

        file = data
        connection = psycopg2.connect(
            database=self.db,
            user=self.user,
            password= self.password,
            host="localhost",
            port=self.port
        )
        engine = create_engine('postgresql://' + self.user + ':' + self.password + '@localhost:' + self.port + '/' + self.db)
        file.to_sql(newTableName, engine, if_exists=if_exist, index=False)
        connection.close()

    def appendDataToExistingTable (self, dataToAppend, tableName):

        # Get the existing data from the table
        existingData = self.getDataFromLocalDatabase(tableName)
        # Concatenate the data (control that the column have to be the same, otherwhise raise Exception)
        columnCheck = []
        for singleColumnInExistingTable in existingData.columns:
            if singleColumnInExistingTable in dataToAppend.columns:
                columnCheck.append(singleColumnInExistingTable)
        if (len(columnCheck) != len(dataToAppend.columns)) | (len(existingData.columns) != len(dataToAppend.columns)):
            raise Exception('ERROR: The columns from the new table do not match the Table columns in the existing Table!')

        # if everything is ok, we can proceed
        finalData = pd.concat([existingData, dataToAppend], axis = 0).drop_duplicates().reset_index(drop=True)
        self.createTable(finalData, tableName, check_rows=False, if_exist='replace') # Creation without checking that the Table is existing

        return finalData

    def getAllTablesInDatabase (self):
        engine = create_engine('postgresql://' + self.user + ':' + self.password + '@localhost:' + self.port + '/' + self.db)
        query = ("SELECT table_schema, table_name"+
                 " FROM information_schema.tables \n"+
                 " WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema') \n"+
                 " ORDER BY table_schema, table_name;")

        data = pd.read_sql(query, engine)

        return data

    def excludeAlreadyProcessedData(self, data, tableName, key, logs = False):

        # get the data from an existing table (user-defined), and check if the table exists
        allTables = self.getAllTablesInDatabase()
        # Case when the table is not existing, so return the original data
        if ~allTables['table_name'].str.contains(tableName).any():
            return data
        else:
            # get the table
            existingTable = self.getDataFromLocalDatabase(tableName)
            resulting = data[~data[key].isin(existingTable[key])].reset_index(drop=True)
            if resulting.empty:
                raise Exception('All the data in the Current Table has been Processed!')
            if logs:
                print('DATA SIZE FROM ALREADY-EXISTING OBSERVATION FILTERING...')
                print('Size of Table Before Filtering: ' + str(len(data[key])) + ' Observations')
                print('Size of Table After Filtering: ' + str(len(resulting[key])) + ' Observations')
                print('\n')

        # It will return the filtered database
        return resulting











