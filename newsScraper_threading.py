import os

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium_stealth import stealth
from fake_useragent import UserAgent

from multiprocessing.pool import ThreadPool
import threading

from config import search_queries, date, extendResultsTimes, filename, filename_to_review, \
    threads, known_problematic, domain_blocklist, \
    relevancy_rating_points, points_threshold_qualified, points_threshold_to_review

from newsScraper import Article, get_local_driver, \
    getPage, prepare_requests, extractArticles, saveArticles, \
    inDomainBlocklist, isNotDuplicate, closePopup, close_drivers, close_local_driver

from relevanceTester import calculateRelevance, isQualified, isToReview

qualified_articles = []
to_review_articles = []

# Capsuled in a function to allow threading
def checkArticle(article):
    driver = get_local_driver()

    # Skip if in blocklist
    if inDomainBlocklist(article, domain_blocklist):
        return

    # Check if is known problematic site and click popup away
    # if article.url_domain in known_problematic.keys():
    #     if not closePopup(driver, article):
    #         return

    print(f"starting thread: {threading.get_ident()}, checking article: {article.url_full}")

    # Fetch article page
    gotArticlePage = getPage(driver, article.url_full)

    if not gotArticlePage:
        return

    # Rate relevance of article
    calculateRelevance(driver, article, relevancy_rating_points)

    # Check for doubles and Append
    if isQualified(article, points_threshold_qualified) and isNotDuplicate(article, qualified_articles):
        qualified_articles.append(article)

    elif isToReview(article, points_threshold_to_review) and isNotDuplicate(article, to_review_articles):
        to_review_articles.append(article)
    
# ==============================================
print("starting up...")

options = Options()
#options.add_argument('-headless')
main_driver = webdriver.Firefox(options=options)

urls = prepare_requests(filename, filename_to_review, search_queries, date)

with ThreadPool(processes=threads) as pool:
    for i, url in enumerate(urls):

        # Fetch DuckDuckGo search results
        gotResultsPage = getPage(main_driver, url)

        # NOT allowed to fail, 'continue' skips iteration
        if not gotResultsPage:
            continue
        
        # Extract articles from DuckDuckGo search results page
        curr_articles = extractArticles(main_driver, extendResultsTimes, search_queries[i])

        if not curr_articles:
            continue

        # Here the threading happens
        pool.map(checkArticle, curr_articles)
    
        print(f"all current articles: {curr_articles}")

    # Save qualified articles to file
    saveArticles(qualified_articles, filename)

    # Save to review articles to file
    saveArticles(to_review_articles, filename_to_review)

    # Close local driver
    # pool.map(close_local_driver, [1] * threads)

# Kill all Google Chrome 
# close_drivers()

print("shutting down main driver...")
main_driver.quit()