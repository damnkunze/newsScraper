from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from newsScraper import Article, known_problematic, \
    getPage, prepare_requests, extractArticles, saveArticles, \
    inDomainBlocklist, isNotDuplicate, closePopup

from relevanceTester import calculateRelevance, isRelevant, OBLIGATORY

# CONFIG =============================================================
date = "2023-03-15"
# If the date lies farther in the past prefer to crawl legally at:
# https://commoncrawl.org/the-data/get-started/

search_queries = [
    "Klima Kleber",
    "Letzte Generation",
    "Klima Protest", 
    "Last Generation", 
    "German Climate Activists"
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

# Amount of relevance points nessesary to be marked as relevant
points_threshold = 6

# Amount of relevance points given
relevancy_rating_points = {
    'query in html': "", #OBLIGATORY,
    'forbidden words': ["Österreich", "Austria", "Just Stop Oil"],
    'qualifying words': ["Letzte Generation", "Letzten Generation", "Letzte-Generation", "Letzten-Generation", "Klima Kleber", "Klimakleber", "Klima Klebern",  "Klimaklebern", "Klima-Kleber", "Klima-Klebern", "Klima Protest", "Klima-Protest", "Klima Aktivist", "Klima-Aktivist", "Klimaaktivist", "Last Generation", "German Climate Activists"],
    
    'query in body': 5,
    'query in url path': 5,
    'query in title': 5,
    'query in heading': 5,
    
    'qualifying words in html': 3,
    
    # "Protest" includes "Protestaktion" and "Blockade" includes "Straßenblockade"
    'bonus words in html': 1,
    'bonus words': ["Aktivist", "Blockade", "Straßenblockade", "Protest", ]
}

# ====================================================================
print("starting up...")

options = Options()
#options.add_argument('-headless')
driver = webdriver.Firefox(options=options)

urls = prepare_requests(filename, search_queries, date)

all_articles = []
for i, url in enumerate(urls):

    # Fetch DuckDuckGo search results
    gotResultsPage = getPage(driver, url)

    # NOT allowed to fail, 'continue' skips iteration
    if not gotResultsPage:
        continue
    
    # Extract articles from DuckDuckGo search results page
    curr_articles = extractArticles(driver, extendResultsTimes, search_queries[i])

    if not curr_articles:
        continue

    for article in curr_articles:
        # Skip if in blocklist
        if inDomainBlocklist(article, domain_blocklist):
            continue

        # Check if is known problematic site and click popup away
        if article.url_domain in known_problematic.keys():
            if not closePopup(driver, article):
                continue

        # Fetch article page
        gotArticlePage = getPage(driver, article.url_full)

        if not gotArticlePage:
            continue

        # Rate relevance of article
        calculateRelevance(driver, article, relevancy_rating_points)

        # Check if off topic
        if not isRelevant(article, points_threshold):
            continue

        # Check for doubles and Append
        if isNotDuplicate(article, all_articles):
            all_articles.append(article)

# Save articles to file
saveArticles(all_articles, filename)

print("shutting down...")
driver.quit()

