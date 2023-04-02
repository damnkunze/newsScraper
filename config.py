
# CONFIG =============================================================
date = "2023-03-15"
# If the date lies farther in the past prefer to crawl legally at:
# https://commoncrawl.org/the-data/get-started/

search_queries = [
    "Letzte Generation",
    "Klima Kleber",
    # "Klima Protest", 
    # "Last Generation", 
    # "German Climate Activists"
]

# File to save qualified news to
filename = f"Articles_{date}.txt"

# File for articles with pending review
filename_to_review = f"Articles_to_review_{date}.txt"

# press "more results" button n times
extendResultsTimes = 1

# threads improve the article checking performance drastically
threads = 5

# Amount of relevance points nessesary to be marked as qualified (relevant)
points_threshold_qualified = 8

# Relevance points to be marked as to be reviewed by a human
points_threshold_to_review = 3

# Amount of relevance points given
relevancy_rating_points = {
    'forbidden words': ["Österreich", "Austria", "Just Stop Oil"],
    'qualifying words': ["Letzte Generation", "Letzten Generation", "Letzte-Generation", "Letzten-Generation", "Klima Kleber", "Klimakleber", "Klima Klebern",  "Klimaklebern", "Klima-Kleber", "Klima-Klebern", "Klima Protest", "Klima-Protest", "Klima Aktivist", "Klima-Aktivist", "Klimaaktivist", "Last Generation", "German Climate Activists"],
    
    'query in url path': 5,
    'query in title': 5,
    'query in heading': 5,
    'query in body': 3,
    
    'qualifying words in html': 3,
    
    # "Protest" includes "Protestaktion" and "Blockade" includes "Straßenblockade"
    'bonus words in html': 2,
    'bonus words': ["Klima Bewegung", "Aktivist", "Blockade", "Straßenblockade", "Protest", ]
}

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

# ====================================================================
