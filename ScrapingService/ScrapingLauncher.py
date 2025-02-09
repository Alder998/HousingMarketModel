# Launch Scraping Algorithms

import ScrapingService as s
import os
from dotenv import load_dotenv
from Utils import Database as d

city = 'Milano'
iterations = 10
pages = 10

# Two different ways of scraping the house offers
# If Existing, process, if not, Start with a 1-iteration Scraping
load_dotenv('App.env')
database_user = os.getenv('DATABASE_USER')
database_password = os.getenv('DATABASE_PASSWORD')
database_port = os.getenv('DATABASE_PORT')
database_db = os.getenv('DATABASE_DB')
database = d.Database(database_user, database_password, database_port, database_db)

db_name = "offerDetailDatabase_" + city
allTables = database.getAllTablesInDatabase()
# if the table is present, append, otherwhise, create
if ~allTables['table_name'].str.contains(db_name).any():
    firstIteration = s.ScrapingService(city).launchScraping(2, 1, filterString = "")

# Once all set, proceed
updatedAll = s.ScrapingService(city).launchGeneralizedScraping(pages, iterations)
updated = s.ScrapingService(city).launchScraping(pages, iterations, filterString = "")

# News Scraper
news = s.ScrapingService(city).launchNewsScraper(subsample=2000, exclude_already_processed=True, all_streets=False)
# Geographic Scraper (better to have many iteration on small requests to avoid max retries)
for retry in range(0,700):
    geo = s.ScrapingService(city).createOrUpdateGeoDataset(base_dataset="offerDetailDatabase_" + city, exclude_already_processed=True,
                                                               subsample=1)

print('Analysis Terminated Successfully!')
