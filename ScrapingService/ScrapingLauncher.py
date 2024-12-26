# Launch Scraping Algorithms

import ScrapingService as s

# Two different ways of scraping the house offers
#updatedAll = s.ScrapingService('Milano').launchGeneralizedScraping(10, 10)
#updated = s.ScrapingService('Milano').launchScraping(10, 10, filterString = "")

# News Scraper
news = s.ScrapingService('Milano').launchNewsScraper(subsample=3000, exclude_already_processed=False, all_streets=True)
# Geographic Scraper
#geo = s.ScrapingService('Milano').createOrUpdateGeoDataset(base_dataset="newsDatabase_" + 'Milano', exclude_already_processed=True,
#                                                           subsample=75)
print('Analysis Terminated Successfully!')
print('\n')
#print(updated)
# print(news)
