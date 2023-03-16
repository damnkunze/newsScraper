from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from newsScraper import Article, prepare_requests, extractNews, saveNews, meetsRequirements, getScreenshot

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
    "www.reddit.com",
    "instagram.com",
    "letztegeneration.de"
]

# Known problematic sites
# www.msn.com, www.zeit.de, de.nachrichten.yahoo.com, 


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
for url in urls:
    # Connect to VPN?
    # For debugging: # getScreenshot(driver, url, filename_screenshot)

    curr_articles = extractNews(driver, url, extendResultsTimes)

    # Remove article domains in blocklist
    curr_articles = [a for a in curr_articles if a.url_netloc not in domain_blocklist]
    #list(filter(lambda article: article.url_netloc not in domain_blocklist, curr_articles))
    
    # Remove articles not fullfilling requirements
    curr_articles = [a for a in curr_articles if meetsRequirements(driver, a.url_full, article_has_to_include)]
    #list(filter(lambda article: meetsRequirements(driver, article.url_full, article_has_to_include), curr_articles))

    # Check for doubles and Append
    for article in curr_articles:
        duplicate = len([a for a in all_articles if article.url_full == a.url_full])
        if duplicate: print("duplicate!!! " + article.url_full) 
        if not duplicate:
            all_articles.append(article)

# Save articles to file
saveNews(all_articles, filename)

driver.quit()

