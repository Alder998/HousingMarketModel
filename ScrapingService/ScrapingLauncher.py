# Launch Scraping Algorithms

import ScrapingService as s

#"localiMinimo=4&localiMassimo=4&"

updated = s.ScrapingService('Milano').launchScraping(10, 10, filterString = "")

print('Analysis Terminated Successfully!')
print('\n')
print(updated)


