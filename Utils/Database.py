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

    def createTable (self, data, newTableName):

        # Check if the table already exists
        allTables = self.getAllTablesInDatabase()
        if allTables.isin(allTables['table_name']):
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
        file.to_sql(newTableName, engine, if_exists='append', index=False)
        connection.close()

    def appendDataToExistingTable (self, dataToAppend, tableName):

        # Get the existing data from the table
        existingData = self.getDataFromLocalDatabase(tableName)
        # Concatenate the data (control that the column have to be the same, otherwhise raise Exception)
        columnCheck = []
        for singleColumnInExistingTable in existingData.columns:
            if singleColumnInExistingTable in dataToAppend.columns:
                columnCheck.append(singleColumnInExistingTable)
        if (len(columnCheck) != dataToAppend.columns) | (len(existingData.columns) != dataToAppend.columns):
            raise Exception('ERROR: The columns from the new table do not match the Table columns in the existing Table!')

        # if everything is ok, we can proceed
        finalData = pd.concat([existingData, dataToAppend], axis = 0).drop_duplicates(keep='first').reset_index(drop=True)
        self.createTable(finalData, tableName)

        return finalData

    def getAllTablesInDatabase (self):
        engine = create_engine('postgresql://' + self.user + ':' + self.password + '@localhost:' + self.port + '/' + self.db)
        query = "SELECT table_schema, table_name"
        "FROM information_schema.tables \n"
        "WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema') \n"
        "ORDER BY table_schema, table_name;"

        data = pd.read_sql(query, engine)

        return data












