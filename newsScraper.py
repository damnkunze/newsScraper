import urllib
import re, os
import threading

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from selenium_stealth import stealth
from fake_useragent import UserAgent

class Article():
    def __init__(self, url_full, title = None, source = None, url_domain = None, query = None):
        self.title = title
        self.source = source
        self.url_full = url_full
        self.url_domain = url_domain
        self.query = query
        self.relevance_score = 0
    
    # To string conversion
    def __repr__(self):
        return f"{self.title} - {self.url_domain}\n"
    
    # For exporting in three lines to a file
    def exportToFile(self):
        return f"{self.title}\n{self.source}\n{self.url_full}\n"

# Known problematic sites: popup closer buttons
known_problematic = {
    "msn.com": "#onetrust-reject-all-handler", 
    "zeit.de": ".message-component", 
    "nachrichten.yahoo.com": "button.btn:nth-child(6)", 
}

# domains to ignore
domain_blocklist = [
    "duckduckgo.com",
    "reddit.com",
    "instagram.com",
    "letztegeneration.de"
]

# format queries to requestable urls
def prepare_requests(file, file_to_review, queries, date):
    # Empty file if exists already
    open(file, 'w').close()
    open(file_to_review, 'w').close()

    urls = []
    for i in range(len(queries)):
        # Encode in URL format
        # FIXME: Encode special characters
        # queries[i] = queries[i].replace(" ", "_")

        urls.append(f"https://duckduckgo.com/?q={queries[i]}&df={date}..{date}")
        # For testing: #urls.append(f"https://www.google.com/search?q={queries[i]}")

    return urls

threadLocal = threading.local()

def get_local_driver():
    # persist driver instance in thread
    driver = getattr(threadLocal, 'driver', None)

    if driver is None:
        options = webdriver.ChromeOptions()

        # To stay undetected as a bot
        userAgent = UserAgent().random
        options.add_argument(f'user-agent={userAgent}')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        #chromeOptions.add_argument("--headless")
        driver = webdriver.Chrome(options=options)

        # To stay undetected as a bot
        # stealth(driver,
        #         languages=["en-US", "en"],
        #         vendor="Google Inc.",
        #         platform="Win32",
        #         webgl_vendor="Intel Inc.",
        #         renderer="Intel Iris OpenGL Engine",
        #         fix_hairline=True,
        #         )

        setattr(threadLocal, 'driver', driver)

    return driver

def getPage(driver, url):
    print("fetching...", url)
    try: 
        driver.get(url)
        print("fetched!", url)
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

        article = Article(url_full, title, source, url_domain, query)
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
    print("SAVING!", articles, file)
    file = open(file, "a")

    for article in articles:
        file.write(article.exportToFile())

    file.close()
    print("Saved " + str(len(articles)) + " articles!")

def close_local_driver(_):
    print(f"closing driver in thread {threading.get_ident()}!")

    get_local_driver().quit()

def close_drivers():
    print("killing all drivers!")
    # killall Google\ Chrome
    os.system("killall Google\ Chrome")








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