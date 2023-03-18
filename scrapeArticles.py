from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from newsScraper import Article, prepare_requests, extractNews, saveNews, \
                        notInBlocklist, isNotDuplicate, meetsRequirements, \
                        getScreenshot

# CONFIG =============================================================
date = "2023-03-15"
# If the date lies farther in the past prefer to crawl legally at:
# https://commoncrawl.org/the-data/get-started/

search_queries = [
    "Letzte Generation",
    "Klima Kleber"
]

filename = f"News_{date}.txt"
filename_screenshot = f"News_{date}.png"

# press "more results" button n times
extendResultsTimes = 0

# domains to ignore
domain_blocklist = [
    "duckduckgo.com",
    "reddit.com",
    "instagram.com",
    "letztegeneration.de"
]

# requirements for articles
article_has_to_include = {
    'all of': ["Letzte Generation"], # "Klima", 
    'one of': ["Aktivist", "Klima Kleber", "Klima Protest", "Blockade", "Straßenblockade", "Protestaktion"]
}
# ====================================================================
print("starting up...")

options = Options()
options.add_argument('-headless')
driver = webdriver.Firefox(options=options)

urls = prepare_requests(filename, search_queries, date)

all_articles = []
for i, url in enumerate(urls):
    # Connect to VPN?
    # For debugging: # getScreenshot(driver, url, filename_screenshot)

    curr_articles = extractNews(driver, url, extendResultsTimes, search_queries[i])

    if curr_articles:
        # Remove article domains in blocklist
        curr_articles = [a for a in curr_articles if notInBlocklist(a, domain_blocklist)]
        
        # Remove articles not fullfilling requirements
        curr_articles = [a for a in curr_articles if meetsRequirements(driver, a, article_has_to_include)]

        # Check for doubles and Append
        for article in curr_articles:
            if isNotDuplicate(article, all_articles):
                all_articles.append(article)

# Save articles to file
saveNews(all_articles, filename)

driver.quit()

