# Launch Scraping Algorithms

import ScrapingService as s

updatedAll = s.ScrapingService('Milano').launchGeneralizedScraping(10, 10)
updated = s.ScrapingService('Milano').launchScraping(10, 10, filterString = "")

print('Analysis Terminated Successfully!')
print('\n')
print(updated)


