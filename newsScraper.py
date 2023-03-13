import urllib
import os

from selenium.webdriver.common.by import By

class Article():
    def __init__(self, title, source, url):
        self.title = title
        self.source = source
        self.url = url

    # To string conversion
    def __str__(self):
        return f"{self.title}\n{self.source}\n{self.url}\n"
    
# format queries to requestable urls
def start_requests(file, queries, date):
    # Remove file if exists already
    open(file, 'w').close()
    urls = []
    
    for i in range(len(queries)):
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

# Filter out article if not on topic
def meetsRequirements(driver, url_link, article_requirements):
    driver.get(url_link)
    getScreenshot(driver, url_link, "TESTBRE.png")

    val = "Klima"
    klima = driver.find_element(By.XPATH, f"//body[contains(text(), '{val}')]")
    print("OI!")
    print(klima)

    contains_all_of = True
    # for value in article_requirements['all of']:
    #     print("Öh?")
    #     if not driver.find_element(By.XPATH, f"//*[text()='{value}']"):
    #         print("Für dich heute leider nicht")
    #         contains_all_of = False
    
    contains_one_of = True
    #contains_one_of = False
    #for value in article_requirements['one of']:
    #    if not driver.find_element(By.XPATH, f"//*[text()='{value}']"):
    #        contains_one_of = True

    if contains_all_of and contains_one_of:
        return True
    return False

def extractNews(driver, urlToCheck, extendResults, blocklist, article_requirements):    
    print(urlToCheck + " fetched!")

    try:
        # Scrape Page
        driver.get(urlToCheck)

        # Set region to germany
        driver.find_element(By.CSS_SELECTOR, ".dropdown__switch").click()

        # Ask for more results
        for i in range(extendResults):
            driver.find_element(By.CSS_SELECTOR, ".result--more").click()
        
        # Find all search results (articles) elements
        articles_elems = driver.find_elements(By.TAG_NAME, "article")

    except Exception as e:
        print("element error ", e)
        return False
    
    articles = []
    for article_elem in articles_elems:
        try:
            title = article_elem.find_element(By.CSS_SELECTOR, "div:nth-child(2) > h2:nth-child(1) > a:nth-child(1) > span:nth-child(1)").text
            url_link = article_elem.find_element(By.CSS_SELECTOR, "div:nth-child(2) > h2:nth-child(1) > a:nth-child(1)").get_attribute("href")
        except Exception as e:
            print("element error ", e)
            return False

        parsed_url = urllib.parse.urlparse(url_link).netloc
        source = ".".join(parsed_url.split(".")[0:-1]) # Get site name without TLD, eg. news.bre.de => news.bre

        if parsed_url not in blocklist:
            if meetsRequirements(driver, url_link, article_requirements):
                article = Article(title, source, url_link)
                articles.append(article)

    return articles

def saveNews(articles, file):
    file = open(file, "a")

    for article in articles:
        file.write(str(article))

    file.close()
    print("Saved " + str(len(articles)) + " valid articles!")