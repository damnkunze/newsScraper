import urllib
import re # RegEX
# import os # For VPN

from selenium.webdriver.common.by import By

class Article():
    def __init__(self, title, source, url_full, url_netloc):
        self.title = title
        self.source = source
        self.url_full = url_full
        self.url_netloc = url_netloc

    # To string conversion
    def __str__(self):
        return f"{self.title}\n{self.source}\n{self.url_full}\n"
    
# format queries to requestable urls
def prepare_requests(file, queries, date):
    # Empty file if exists already
    open(file, 'w').close()

    urls = []
    for i in range(len(queries)):
        # Encode in URL format
        # FIXME: Encode special characters
        queries[i].replace(" ", "_")

        urls.append(f"https://duckduckgo.com/?q={queries[i]}&df={date}..{date}")
        # For testing: #urls.append(f"https://www.google.com/search?q={queries[i]}")

    return urls

def getScreenshot(driver, urlToCheck, screenshotSaveName):
    try:
        driver.save_screenshot(screenshotSaveName)
        print("\nSCREENSHOT SAVED AT " + screenshotSaveName + " OF " + urlToCheck)

    except Exception as e:
        print(e)
        return "error"

# Filter out article if not meeting requirements (eg: is on topic)
def meetsRequirements(driver, url_link, article_requirements):
    driver.get(url_link)
    #getScreenshot(driver, url_link, "TESTBRE.png")

    try:
        body = driver.find_element(By.CSS_SELECTOR, 'body').get_attribute('innerHTML')

    except Exception as e:
        print(e)
        return False

    # bool(re.search(value, body)) is case-insensitive

    for value in article_requirements['all of']:
        if not bool(re.search(value, body, re.IGNORECASE)):
            print("misses mandatory " + value + ":", url_link)
            return False
    
    contains_one_of = False
    for value in article_requirements['one of']:
        if bool(re.search(value, body, re.IGNORECASE)):
            contains_one_of = True
            break

    print("tudo bem:" if contains_one_of else "no extra keywords:", url_link)
    #return contains_one_of
    return True

def extractNews(driver, urlToCheck, extendResults):    
    try:
        # Scrape Page
        print("fetching...")
        driver.get(urlToCheck)
        print(urlToCheck + " fetched!")

        # Set region to germany
        driver.find_element(By.CSS_SELECTOR, ".dropdown__switch").click()

        # Ask for more results n times
        for _ in range(extendResults):
            try:
                driver.find_element(By.CSS_SELECTOR, ".result--more").click()
            except:
                break
        
        # Find all search results (articles) elements
        articles_elems = driver.find_elements(By.TAG_NAME, "article")

    except Exception as e:
        print("element error ", e)
        return False
    
    articles = []
    for article_elem in articles_elems:
        try:
            title = article_elem.find_element(By.CSS_SELECTOR, "div:nth-child(2) > h2:nth-child(1) > a:nth-child(1) > span:nth-child(1)").text
            url_full = article_elem.find_element(By.CSS_SELECTOR, "div:nth-child(2) > h2:nth-child(1) > a:nth-child(1)").get_attribute("href")
        except Exception as e:
            print("element error ", e)
            return False

        url_netloc = urllib.parse.urlparse(url_full).netloc
        source = ".".join(url_netloc.split(".")[0:-1]) # Get site name without TLD, eg. news.bre.de => news.bre

        article = Article(title, source, url_full, url_netloc)
        articles.append(article)

    print("Extracted " + str(len(articles)) + " articles!")

    return articles

def saveNews(articles, file):
    file = open(file, "a")

    for article in articles:
        file.write(str(article))

    file.close()
    print("Saved " + str(len(articles)) + " valid articles!")