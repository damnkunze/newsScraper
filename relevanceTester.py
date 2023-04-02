import urllib
import re 

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def isQualified(article, points_threshold):
    # relevance score needs to be above the points threshold and not -1 which represents completely off-topic
    if article.relevance_score < points_threshold or article.relevance_score == -1:
        print("relevance score:", article.relevance_score, "NOT RELEVANT")
        return False

    print("relevance score:", article.relevance_score, "RELEVANT")
    return True

def isToReview(article, points_threshold):
    if article.relevance_score < points_threshold or article.relevance_score == -1:
        print("relevance score:", article.relevance_score, "NOT TO REVIEW")
        return False

    print("relevance score:", article.relevance_score, "TO REVIEW")
    return True

# Rate relevance of article
def calculateRelevance(driver, article, article_requirements):
    query = article.query
    print("Calculating relevance... with query:", query)
    
    # RegEx allows for non-digit chars between keyword words, eg. 'letzte--generation' or 'letzte--generation'
    flexible_query = query.replace(" ", "(\D)*")

    # ------------ Strict requirements ------------
    # Wait for page to load until qualifying word is present in body, title or heading
    try: 
        wait5 = WebDriverWait(driver, timeout=5, poll_frequency=1)

        # Collect all qualifying conditions
        qualifying_conditions = []
        for value in article_requirements['qualifying words']:
            ec = EC.text_to_be_present_in_element((By.CSS_SELECTOR, "body"), value)
            qualifying_conditions.append(ec)

        # Wait until one of the ec is fullfilled
        # *list, is a weird list to tuple conversion, EC.any_of wants a tuple
        wait5.until(EC.any_of(*qualifying_conditions,))
        
        html = driver.find_element(By.CSS_SELECTOR, 'html').get_attribute("innerText")
    except TimeoutException: 
        print("timeout: body does not contain qualifying words!")
        return

    # Cannot include 'forbidden words'
    for forbidden in article_requirements['forbidden words']:
        # case-insensitive RegEx
        if bool(re.search(forbidden, html, re.IGNORECASE)):
            article.relevance_score = -1
            print("contains forbidden word! :", forbidden)
            return

    # ------------ Optional Requirements ------------

    # Points for 'query in body'
    if bool(re.search(flexible_query, html, re.IGNORECASE)):
        article.relevance_score += article_requirements['query in body']
        print("body contains query")
    
    # Points for 'query in url path'
    url_path = urllib.parse.urlparse(article.url_full).path 

    if bool(re.search(flexible_query, url_path, re.IGNORECASE)):
        article.relevance_score += article_requirements['query in url path']
        print(f"url path {url_path} contains query")

    # Points for 'query in title'
    try: 
        title = driver.find_element(By.CSS_SELECTOR, 'title').get_attribute("innerText").replace("\n","")

        if bool(re.search(query, title, re.IGNORECASE)):
            article.relevance_score += article_requirements['query in title']
            print(f"title {title} contains query")
    except: pass

    # Points for 'query in heading'
    try: 
        # 'find_element' not 'find_elements' => Assuming only one heading exists
        heading = driver.find_element(By.CSS_SELECTOR, 'h1').get_attribute("innerText")

        if bool(re.search(query, heading, re.IGNORECASE)):
            article.relevance_score += article_requirements['query in heading']
            print(f"heading {heading} contains query")
    except: pass

    # Points for 'qualifying words in html'
    try:
        qualifying_words = []
        for value in article_requirements['qualifying words']:
            if bool(re.search(value, html, re.IGNORECASE)):
                article.relevance_score += article_requirements['qualifying words in html']
                qualifying_words.append(value)
        
        print(f"contains {len(qualifying_words)} qualifying words in html: ", qualifying_words)
        
    except: pass
    
    # Points for 'bonus words in html'
    try:
        bonus_words = []
        for value in article_requirements['bonus words']:
            if bool(re.search(value, html, re.IGNORECASE)):
                article.relevance_score += article_requirements['bonus words in html']
                bonus_words.append(value)
        
        print(f"contains {len(bonus_words)} bonus words in body: ", bonus_words)
        
    except: pass

