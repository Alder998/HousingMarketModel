# Launch Scraping Algorithms

import ScrapingService as s

#updatedAll = s.ScrapingService('Milano').launchGeneralizedScraping(10, 10)
#updated = s.ScrapingService('Milano').launchScraping(10, 10, filterString = "")

# News Scraper
news = s.ScrapingService('Milano').launchNewsScraper(subsample=500)

print('Analysis Terminated Successfully!')
print('\n')
#print(updated)
print(news)


