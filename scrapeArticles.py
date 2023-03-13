from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from newsScraper import Article, start_requests, extractNews, saveNews, getScreenshot

# CONFIG =============================================================
date = "2023-02-17"
# If the date lies farther in the past prefer to crawl legally at:
# https://commoncrawl.org/the-data/get-started/

search_queries = [
    "Letzte Generation",
    #"Klima Kleber"
]

filename = f"News_{date}.txt"
filename_screenshot = f"News_{date}.png"

# press "more results" button n times
extendResultsTimes = 0 

# domains to ignore
url_blocklist = [
    "duckduckgo.com",
    "letztegeneration.de"
]

# requirements for articles
article_has_to_include = {
    'all of': ["Klima", "Letzte Generation"],
    'one of': ["Klima Aktivisten", "Klima Kleber", "Klima Protest", "Blockade", "Straßenblockade", "Protestaktion"]
}
# ====================================================================

options = Options()
options.add_argument('-headless')
driver = webdriver.Firefox(options=options)

""" OpenVPN
sudo apt-get install openvpn unzip
sudo openvpn --config ../Surfshark_Config/de-fra.prod.surfshark.com_tcp.ovpn --auth-user-pass ../pass.txt
"""
urls = start_requests(filename, search_queries, date)

articles = []
for (i, url) in enumerate(urls):
    # Connect to VPN?
    # For debugging:
    #getScreenshot(driver, url, filename_screenshot)

    articles = extractNews(driver, url, extendResultsTimes, url_blocklist, article_has_to_include)

    if articles:
        saveNews(articles, filename)

driver.quit()

