# Scraping Service Library to get housing data
import math
import os
from Utils import Database as d
import numpy as np
from dotenv import load_dotenv

class ScrapingService:
    def __init__(self, city):
        self.city = city
        pass

    # STEP 1: Get the links from the main page of house selling in a given city. Get the Links in an iterattive way, store it in a Database, update it
    def getLinkDB (self, pages=10, filterString=""):
        import requests
        from bs4 import BeautifulSoup
        import pandas as pd
        import random

        # First, load the SQL credencials
        load_dotenv('App.env')
        database_user = os.getenv('DATABASE_USER')
        database_password = os.getenv('DATABASE_PASSWORD')
        database_port = os.getenv('DATABASE_PORT')
        database_db = os.getenv('DATABASE_DB')

        # Take data from Immobiliare.it, store the data

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}

        # Iterate for pages
        pag_max = pages
        pageLinks = []
        for page in range(pag_max):
            print("Processing page...", page)
            target_url = "https://www.immobiliare.it/vendita-case/" + self.city.lower() + "/?" + filterString + "pag=" + str(
                pag_max + random.choice(range(0, 71)))

            resp = requests.get(target_url, headers=headers)
            soup = BeautifulSoup(resp.text, 'html.parser')

            # 1. find the link of each specific Offer
            div_gen = soup.find_all("div")
            for single_div in div_gen:
                links = single_div.find_all('a', href=True)
                for link in links:
                    if "/annunci/" in link['href']:
                        pageLinks.append(link['href'])

        pageLinks = pd.DataFrame(pageLinks).drop_duplicates().reset_index(drop=True).set_axis(['link'], axis=1)
        print("number of offers found: ", len(pageLinks['link']))
        # Isolate the Offer Univocal code
        pageLinks = pd.concat([pageLinks, pageLinks['link'].str.split("/").str[4]], axis=1).set_axis(['link', 'ID'], axis=1)

        # Update (temporary)
        existingFile = pd.read_excel(r"C:\Users\alder\Desktop\Projects\storage_tmp\houses_tmp.xlsx")
        updatedFiles = pd.concat([existingFile, pageLinks], axis=0).drop_duplicates().reset_index(drop=True)
        updatedFiles.to_excel(r"C:\Users\alder\Desktop\Projects\storage_tmp\houses_tmp.xlsx", index=False)
        print('Number of houses in DB:', len(updatedFiles['link']))

        # Update (SQL, with customized table name)
        db_name = 'offerLinkTable_'+self.city
        # Instantiate the DB
        database = d.Database(database_user, database_password, database_port, database_db)
        # Get all table in DB
        allTables = database.getAllTablesInDatabase()
        # if the table is present, append, otherwhise, create
        if allTables['table_name'].str.contains(db_name).any():
            database.appendDataToExistingTable(updatedFiles, db_name)
        else:
            database.createTable(updatedFiles, db_name)

        return updatedFiles

    def massiveLinkScraper(self, pages, iterations, filterString):
        for i in range(iterations):
            print('Iteration:', i)
            data = self.getLinkDB(pages, filterString)
        # The last data after the iteration is enough, since the function getLinkDB returns the already-updated Database
        return data

    def extractFeaturesFromLinks(self, linksDB):
        import requests
        from bs4 import BeautifulSoup
        import pandas as pd

        # Get the data (change to SQL when possible)
        existing = pd.read_excel(r"C:\Users\alder\Desktop\Projects\storage_tmp\houses_all_tmp.xlsx")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}
        updatedFiles = linksDB
        # Process only the IDs that are not in the existing file
        notAvailableLinks = pd.read_excel(r"C:\Users\alder\Desktop\Projects\storage_tmp\not_available_links.xlsx")
        linksToProcess = updatedFiles[~updatedFiles['ID'].isin(existing['ID']) & ~updatedFiles['link'].isin(notAvailableLinks['link'])].reset_index(drop=True)
        unavailableLinks = []
        responseList = []
        charDB = []
        for n, offer in enumerate(linksToProcess['link']):

            if offer == 'https://www.immobiliare.it/annunci/116091343/':
                print('qui')

            # General
            respI = requests.get(offer, headers=headers)
            soupI = BeautifulSoup(respI.text, 'html.parser')

            # Add the Logging
            print('Getting data...', round(n / len(linksToProcess['link']) * 100, 2), ' %')

            # ---Indicazioni Geografiche---
            try:
                div_genI = soupI.find_all("span", class_="re-title__location")
                singleGeo = []
                for single_divI in div_genI:
                    geoGen = single_divI.text
                    singleGeo.append(geoGen)
                # Hard-code to prevent the algorithm to fail, whenever the address is hidden (could be hidden sometimes for privacy Reason)
                if len(singleGeo) == 2:
                    singleGeoDF = pd.DataFrame(singleGeo).transpose().set_axis(["City", "Area"], axis=1)
                    singleGeoDF = pd.concat([singleGeoDF, pd.DataFrame(pd.Series(math.nan))], axis = 1).set_axis(["City", "Area", "Adress"], axis=1)
                else:
                    singleGeoDF = pd.DataFrame(singleGeo).transpose().set_axis(["City", "Area", "Adress"], axis=1)

                # ---Prezzo---
                div_genJ = soupI.find_all("div", class_="re-overview__price")
                for single_divJ in div_genJ:
                    priceGen = single_divJ.text

                # ---Metratura---
                div_genK = soupI.find_all("span")
                multipleS = True
                multipleB = True
                multipleL = True
                multipleF = True
                for value in div_genK:
                    if ('m²' in value.text) & (multipleS):
                        sizeAll = value.text
                        multipleS = False
                    if ('bagn' in value.text) & (multipleB):
                        toiletAll = value.text
                        multipleB = False
                    if ('local' in value.text) & (multipleL):
                        roomsAll = value.text
                        multipleL = False
                    if ('Piano' in value.text) & (multipleF):
                        floorAll = value.text
                        multipleF = False

                # ---Description---
                div_genL = soupI.find_all("div", class_='in-readAll in-readAll--lessContent')
                for desc in div_genL:
                    descAll = desc.text

                # Create The Database internally, not to have unaligned data
                tmpData = pd.concat(
                    [pd.Series(offer), singleGeoDF, pd.Series(descAll), pd.Series(priceGen), pd.Series(sizeAll),
                     pd.Series(floorAll), pd.Series(roomsAll), pd.Series(toiletAll)], axis=1).set_axis(["link", "City",
                                                                                                        "Area", "Adress",
                                                                                                        "Description",
                                                                                                        "Price", "Size",
                                                                                                        "Floor", "Rooms",
                                                                                                        "Toilets"], axis=1)
                charDB.append(tmpData)

            except Exception as e:
                # Customze the errors not to lose any data
                if respI.status_code == 404:
                    print('Error: Link Not available or Offer not Found!')
                    unavailableLinks.append(offer)
                    # Logging List
                    responseList.append('Offer: ' + offer + ' - Status: ' + str(respI.status_code) + " - Message: Link Not available or Offer not Found!")
                else:
                    # Logging List
                    responseList.append('Offer: ' + offer + ' - Status: ' + str(respI.status_code) + " - Message: " + str(e))
                    print('Error:', e)  # Print the Customized Error

        # Handle unavailable links first (unique database)
        if len(unavailableLinks) > 0:
            naLinks = pd.concat([pd.DataFrame(unavailableLinks), pd.DataFrame(np.full(len(unavailableLinks), self.city))],
                                axis = 1).set_axis(['link', 'city'], axis = 1)
            notAvailableLinks = pd.concat([notAvailableLinks, naLinks], axis = 0).reset_index(drop = True)
            notAvailableLinks.to_excel(r"C:\Users\alder\Desktop\Projects\storage_tmp\not_available_links.xlsx", index=False,
                             engine='xlsxwriter')
        # Populate the Scraping Log file
        current_dir = os.path.dirname(__file__)
        log_file_path = os.path.join(current_dir, 'scrapingLogs.txt')
        with open(log_file_path, 'w') as file:
            logFile = "\n".join(responseList)
            file.write(logFile)

        # Now, aggregate the data
        aggregatedData = pd.concat([df for df in charDB], axis=0).reset_index(drop=True)
        aggregatedData = aggregatedData.merge(updatedFiles, on='link').drop_duplicates(
            subset=['Adress', 'Price']).reset_index(drop=True)

        # Get the existing data, concat, drop duplicates
        aggregatedData = pd.concat([existing, aggregatedData], axis=0).drop_duplicates(keep='last').reset_index(drop=True)
        # Save to excel
        aggregatedData.to_excel(r"C:\Users\alder\Desktop\Projects\storage_tmp\houses_all_tmp.xlsx", index=False,
                                engine='xlsxwriter')
        # Analytics on the extracted Data
        print('Total number of Processable Offers: ', len(aggregatedData.dropna().reset_index(drop=True)['link']))

        return aggregatedData

    def cleanOffersDatabase(self, dataRaw):

        # Load the SQL credencials
        load_dotenv('App.env')
        database_user = os.getenv('DATABASE_USER')
        database_password = os.getenv('DATABASE_PASSWORD')
        database_port = os.getenv('DATABASE_PORT')
        database_db = os.getenv('DATABASE_DB')

        # STEP 3: Clean the Database, obtain data that could be processed by a Model
        aggregatedData = dataRaw
        # print(aggregatedData['Price'].unique())

        print('cleaning the Scraping Database...')

        # Price
        aggregatedData['Decrease'] = aggregatedData['Price'].str.split('0€').str[1]
        aggregatedData['Price'] = aggregatedData['Price'].str.split('0€').str[0]
        aggregatedData.loc[~aggregatedData['Decrease'].isnull(), 'Price'] = aggregatedData['Price'] + '0'
        # This part has been commented, since the string "0Prezzo" is only for newly-built houses, that we exlude from
        # the clean data.
        #aggregatedData['Decrease'] = aggregatedData['Price'].str.split('0Prezzo').str[1]
        aggregatedData['Price'] = aggregatedData['Price'].str.split('0Prezzo').str[0]

        aggregatedData = aggregatedData[
            ~aggregatedData['Price'].str.contains(' - ') & ~aggregatedData['Price'].str.contains('da')
            & ~aggregatedData['Price'].str.contains('Prezzo su richiesta') & ~aggregatedData['Price'].str.contains('Venduto')].reset_index(drop=True)
        aggregatedData['Price'] = aggregatedData['Price'].str.replace('€ ', '').str.replace('.', '')
        aggregatedData['Price'] = aggregatedData['Price'].astype(int)

        # Toilets
        aggregatedData = aggregatedData[
            ~aggregatedData['Toilets'].str.contains(' - ') & ~aggregatedData['Toilets'].str.contains('da')]
        aggregatedData['Toilets'] = aggregatedData['Toilets'].str.replace(' bagno', '').str.replace(' bagni',
                                                                                                    '').str.replace('+',
                                                                                                                    '')
        aggregatedData['Toilets'] = aggregatedData['Toilets'].astype(int)

        # Rooms
        aggregatedData = aggregatedData[
            ~aggregatedData['Rooms'].str.contains(' - ') & ~aggregatedData['Rooms'].str.contains('da')]
        aggregatedData['Rooms'] = aggregatedData['Rooms'].str.replace(' locale', '').str.replace(' locali',
                                                                                                 '').str.replace('+',
                                                                                                                 '')
        aggregatedData['Rooms'] = aggregatedData['Rooms'].astype(int)

        # Floor
        aggregatedData = aggregatedData[
            ~aggregatedData['Floor'].str.contains(' - ') & ~aggregatedData['Floor'].str.contains('da')
            & aggregatedData['Floor'].str.contains('Piano')]
        aggregatedData['Floor'] = aggregatedData['Floor'].str.replace('Piano ', '').str.replace('.', '').str.replace(
            'R', '0.5').str.replace('T', '0').str.replace('S', '-1')
        aggregatedData['Floor'] = aggregatedData['Floor'].astype(float)

        # Size
        aggregatedData = aggregatedData[
            ~aggregatedData['Size'].str.contains(' - ') & ~aggregatedData['Size'].str.contains('da')]
        aggregatedData['Size'] = aggregatedData['Size'].str.replace(' m²', '').str.replace('+', '').str.replace('.', '')
        aggregatedData['Size'] = aggregatedData['Size'].astype(int)

        # Compute price per square meter
        aggregatedData['Price per square meter'] = aggregatedData['Price'] / aggregatedData['Size']

        # Same Address and same size means a duplicate, therefore remove it
        aggregatedData = aggregatedData.drop_duplicates(subset=['Adress', 'Size'])

        # Reset Index
        aggregatedData = aggregatedData.reset_index(drop=True)
        aggregatedData.to_excel(r"C:\Users\alder\Desktop\Projects\storage_tmp\houses_all_clean.xlsx", index=False,
                                engine='xlsxwriter')

        print('Processable offers after data cleaning:', len(aggregatedData['Size']))

        # Update (SQL, with customized table name)
        db_name = 'offerDetailDatabase_'+self.city
        # Instantiate the DB
        database = d.Database(database_user, database_password, database_port, database_db)
        # Get all table in DB
        allTables = database.getAllTablesInDatabase()
        # if the table is present, append, otherwhise, create
        if allTables['table_name'].str.contains(db_name).any():
            database.appendDataToExistingTable(aggregatedData, db_name)
        else:
            database.createTable(aggregatedData, db_name)

        return aggregatedData

    def launchScraping (self, pages, iterations, filterString):
        # Put all the functions together
        step1 = self.massiveLinkScraper(pages, iterations, filterString)
        step2 = self.extractFeaturesFromLinks(step1)
        step3 = self.cleanOffersDatabase(step2)
        return step3

    def launchGeneralizedScraping (self, pages, iterations):
        filterList = ["localiMinimo=1&localiMassimo=1&","localiMinimo=2&localiMassimo=2&",
                      "localiMinimo=3&localiMassimo=3&","localiMinimo=4&localiMassimo=4&"]
        for singleFilter in filterList:
            iterationRoom = self.launchScraping(pages, iterations, singleFilter)



