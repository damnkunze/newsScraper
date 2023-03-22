import urllib
import re 

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class Article():
    def __init__(self, title, source, url_full, url_domain, query):
        self.title = title
        self.source = source
        self.url_full = url_full
        self.url_domain = url_domain
        self.relevance_score = 0
        self.query = query

    # To string conversion
    def __str__(self):
        return f"{self.title}\n{self.source}\n{self.url_full}\n"

# Known problematic sites: popup closer buttons
known_problematic = {
    "msn.com": "#onetrust-reject-all-handler", 
    "zeit.de": ".message-component", 
    "nachrichten.yahoo.com": "button.btn:nth-child(6)", 
}

# format queries to requestable urls
def prepare_requests(file, queries, date):
    # Empty file if exists already
    open(file, 'w').close()

    urls = []
    for i in range(len(queries)):
        # Encode in URL format
        # FIXME: Encode special characters
        # queries[i] = queries[i].replace(" ", "_")

        urls.append(f"https://duckduckgo.com/?q={queries[i]}&df={date}..{date}")
        # For testing: #urls.append(f"https://www.google.com/search?q={queries[i]}")

    return urls

def getPage(driver, url):
    print("fetching...")
    try: 
        driver.get(url)
        print(url + " fetched!")
        return True
    except: 
        # NOT allowed to fail, if fail skip iteration
        return False

def isNotDuplicate(article, all_articles):
    duplicate = len([a for a in all_articles if article.url_full == a.url_full])
    if duplicate: 
        print("duplicate! " + article.url_full) 
        return False
    else:
        return True

def inDomainBlocklist(article, blocklist):
    if article.url_domain in blocklist:
        print("blocked! " + article.url_domain)
        return True
    return False

def extractArticles(driver, extendResults, query):    
    try:
        # Set region to germany
        driver.find_element(By.CSS_SELECTOR, ".dropdown__switch").click()

        # Ask for more results n times
        for _ in range(extendResults):
            try:
                driver.find_element(By.CSS_SELECTOR, ".result--more").click()
            except NoSuchElementException:
                break

    # IS allowed to fail
    except NoSuchElementException as e: 
        print("Error: Could not set search settings!")
        
    try:
        # Find all search results (articles) elements
        articles_elems = driver.find_elements(By.TAG_NAME, "article")
    
    # NOT allowed to fail
    except NoSuchElementException as e: 
        print("element error ", e)
        return False
    
    articles = []
    for article_elem in articles_elems:
        try:
            title = article_elem.find_element(By.CSS_SELECTOR, "div:nth-child(2) > h2:nth-child(1) > a:nth-child(1) > span:nth-child(1)").text
            url_full = article_elem.find_element(By.CSS_SELECTOR, "div:nth-child(2) > h2:nth-child(1) > a:nth-child(1)").get_attribute("href")
        
        # IS allowed to fail
        except NoSuchElementException as e:
            print("element error ", e)
            continue
        
        # Full site name, eg. news.bre.de
        url_netloc = urllib.parse.urlparse(url_full).netloc 
        # Site name with just TLD and domain name, eg. news.bre.de => bre.de
        url_domain = ".".join(url_netloc.split(".")[-2:]) 
        # Site name without TLD, eg. news.bre.de => news.bre
        source = ".".join(url_netloc.split(".")[0:-1]) 

        article = Article(title, source, url_full, url_domain, query)
        articles.append(article)

    print("Extracted " + str(len(articles)) + " articles!")
    return articles

# Click popup away using selector from known-problematic sites
def closePopup(driver, article):
    print("problematic website!")
    try:
        selector = known_problematic[article.url_domain]

        # Wait max 3s for button to be clickable, using 'expected contition' module
        wait = WebDriverWait(driver, timeout=5, poll_frequency=1) #, ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException])
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        button.click()
        print("Closed Popup!")
        return True

    # If site has been visited before and cookies were set by closing popup
    except TimeoutException:
        print("No Popup to be closed!")
        return True
    
    except:
        # In all other Exception cases
        print("Other error")
        return False

def saveArticles(articles, file):
    file = open(file, "a")

    for article in articles:
        file.write(str(article))

    file.close()
    print("Saved " + str(len(articles)) + " valid articles!")










# Filter out article if not meeting requirements (eg: is on topic)
def meetsRequirements(driver, article, article_requirements):
    url_link = article.url_full

    driver.get(url_link)
    ##getScreenshot(driver, url_link, "TESTBRE.png")

    #calculateArticleRelevance(driver, article)

    try:
        body = driver.find_element(By.CSS_SELECTOR, 'body').get_attribute('innerHTML')

    except NoSuchElementException as e:
        print(e)
        return False

    # Check if contains all keywords in article_requirements['all of']
    for value in article_requirements['all of']:
        # case-insensitive RegEx
        if not bool(re.search(value, body, re.IGNORECASE)):
            print("misses mandatory " + value + ":", url_link)
            return False

    # Check if contains one keyword in article_requirements['one of']
    # FIXME: Currently just optional
    contains_one_of = False
    for value in article_requirements['one of']:
        if bool(re.search(value, body, re.IGNORECASE)):
            contains_one_of = True
            break

    print("tudo bem:" if contains_one_of else "no extra keywords:", url_link)
    #return contains_one_of
    return True

# For debugging: # getScreenshot(driver, url, filename_screenshot)
def getScreenshot(driver, urlToCheck, screenshotSaveName):
    try:
        driver.save_screenshot(screenshotSaveName)
        print("\nSCREENSHOT SAVED AT " + screenshotSaveName + " OF " + urlToCheck)

    except Exception as e:
        print(e)
        return "error"