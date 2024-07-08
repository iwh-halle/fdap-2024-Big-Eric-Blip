# Packages used in this notebook
import requests
from nltk.sentiment import SentimentIntensityAnalyzer
from bs4 import BeautifulSoup
import collections
from datetime import datetime, timedelta
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import nltk
import numpy as np
import pandas as pd
import configparser
import openai
import json
from datetime import datetime

SCRAPER_API_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'  # Replace with your Scraper API key

def get_wg_links(pages=2):
    links = []
    for i in range(pages):
        url = f"https://www.wg-gesucht.de/wg-zimmer-in-Aachen.1.0.1.{i}.html?offer_filter=1&city_id=1&sort_order=0&noDeact=1&categories%5B%5D=0&pagination=1&pu="
        scraper_api_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"
        response = requests.get(scraper_api_url)
        
        if response.status_code != 200:
            print(f"Failed to retrieve {url}, status code: {response.status_code}")
            print(response.text)
            continue

        # Parse results
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extracting all Anzeigen
        anzeigen_raw = soup.find_all('div', class_='col-sm-8 card_body')
        for anzeige in anzeigen_raw:
            anchor_tag = anzeige.find('a')
            if anchor_tag and 'href' in anchor_tag.attrs:
                links.append("https://www.wg-gesucht.de" + anchor_tag['href'])

    return links

def get_anzeigen_html(links):
    anzeigen_html = []
    for link in links:
        scraper_api_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={link}"
        response = requests.get(scraper_api_url)
        
        if response.status_code != 200:
            print(f"Failed to retrieve {link}, status code: {response.status_code}")
            print(response.text)
            continue

        # Convert the BeautifulSoup object to a string
        soup = BeautifulSoup(response.text, 'html.parser')
        anzeigen_html.append({'html': str(soup), 'link': link})

    # Save the list of dictionaries to a JSON file
    with open('html_pages.json', 'w', encoding='utf-8') as file:
        json.dump(anzeigen_html, file, ensure_ascii=False, indent=4)

    return pd.DataFrame(anzeigen_html)

def analyze_sentiment(article_text):
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(article_text)
    return sentiment

def calculate_composite_sentiment(zimmer_text,lage_text,wg_leben_text,sonstiges_text):
    texts = {
        'zimmer': zimmer_text,
        'lage': lage_text,
        'wg_leben': wg_leben_text,
        'sonstiges': sonstiges_text
    }

    sentiments = {}
    valid_compound_scores = []

    for key, text in texts.items():
        if text != 'Unknown':
            sentiment = analyze_sentiment(text)
            sentiments[key] = sentiment
            valid_compound_scores.append(sentiment['compound'])
        else:
            sentiments[key] = {'compound': None, 'neg': None, 'neu': None, 'pos': None}

    if valid_compound_scores:
        overall_sentiment = sum(valid_compound_scores) / len(valid_compound_scores)
    else:
        overall_sentiment = None

    sentiments['overall_sentiment'] = overall_sentiment

    return sentiments

FRATERNITIES=[
    "Studentenverbindung", 
    "Burschenschaft", 
    "Corps", 
    "Landsmannschaft", 
    "Akademische Verbindung", 
    "Studentische Verbindung", 
    "Studentenbund",
    "Studentenverein", 
    "Studentenvereinigung", 
    "Kadergemeinschaft",
    "Akademische Vereinigung", 
    "Studierendenverband", 
    "Akademische Gemeinschaft",
    "Studentenbruderschaft", 
    "Universitätsgesellschaft"
]

def contains_any_words(texts):
    # Convert all texts to lower case for case-insensitive comparison
    lower_texts = [text.lower() for text in texts]
    
    # Convert the words to lower case for case-insensitive comparison
    lower_words = [word.lower() for word in FRATERNITIES]
    
    for text in lower_texts:
        if any(word in text for word in lower_words):
            return True
    return False

def load_anzeigen_html(filename='html_pages.json'):
    with open(filename, 'r', encoding='utf-8') as file:
        anzeigen_html = json.load(file)

    # Convert the HTML strings back to BeautifulSoup objects
    for anzeige in anzeigen_html:
        anzeige['html'] = BeautifulSoup(anzeige['html'], 'html.parser')

    return pd.DataFrame(anzeigen_html)

def get_anzeigen_from_html():
    html_list = load_anzeigen_html()
    anzeigen = []
    errors = 0
    for soup in html_list['html']:
        try:
            titel_element = soup.find('h1', class_='headline headline-detailed-view-title')
            titel = titel_element.get_text().replace('\n', '').strip() if titel_element else 'Unknown'

            wg_groesse_element = soup.find('span', class_='mr5')
            wg_groesse = wg_groesse_element['title'].split('er')[0].split()[0] if (wg_groesse_element and 'title' in wg_groesse_element.attrs) else 'Unknown'

            key_facts = soup.find_all('b', class_='key_fact_value')
            groesse = key_facts[0].get_text().split('m')[0].strip() if key_facts and len(key_facts) > 0 else 'Unknown'
            miete = key_facts[1].get_text().split('€')[0].strip() if key_facts and len(key_facts) > 1 else 'Unknown'

            minor_facts = soup.find_all('span', class_='section_panel_value')
            kaltmiete = minor_facts[0].get_text().replace('€','').strip() if minor_facts and len(minor_facts) > 0 else 'Unknown'
            nebenkosten = minor_facts[1].get_text().replace('€','').strip() if minor_facts and len(minor_facts) > 1 else 'Unknown'
            sonstige_kosten = minor_facts[2].get_text().replace('€','').strip() if minor_facts and len(minor_facts) > 2 else 'Unknown'
            kaution = minor_facts[3].get_text().replace('€','').strip() if minor_facts and len(minor_facts) > 3 else 'Unknown'
            abloesevereinb = minor_facts[4].get_text().replace('€','').strip() if minor_facts and len(minor_facts) > 4 else 'Unknown'
            frei_ab = minor_facts[5].get_text().strip() if minor_facts and len(minor_facts) > 5 else 'Unknown'

            adresse = soup.find_all('a', href='#mapContainer')
            strasse = adresse[0].get_text().strip().split()[0] if adresse else 'Unknown'
            plz = next((text for text in adresse[0].get_text().strip().split() if re.fullmatch(r'\d{5}', text)), 'Unknown') if adresse else 'Unknown'

            online_seit = 'Unknown'
            green_style = soup.find('b', style='color: #218700;')
            grey_style = soup.find('b', style='color: #898989;')

            if green_style:
                online_seit = green_style.get_text().strip()
            elif grey_style:
                online_seit = grey_style.get_text().strip()

            if "Sekunde" in online_seit or "Sekunden" in online_seit:
                online_seit = 0,0
            elif "Minuten" in online_seit or "Minute" in online_seit:
                minutes = ''.join(filter(str.isdigit, online_seit))
                #online_seit = f"00:{minutes.zfill(2)}"
                online_seit = 0.01 * int(minutes)
            elif "Stunden" in online_seit or "Stunde" in online_seit:
                hours = ''.join(filter(str.isdigit, online_seit))
                #online_seit = f"{hours.zfill(2)}:00"
                online_seit = int(hours)
            elif "Tag" in online_seit or "Tage" in online_seit:
                days = ''.join(filter(str.isdigit, online_seit))
                online_seit = int(days) * 24
                #online_seit = f"{hours}:00"
            else:
                try:
                    date_format = "%d.%m.%Y"
                    online_date = datetime.strptime(online_seit, date_format)
                    current_date = datetime.now()
                    days_ago = (current_date - online_date).days
                    online_seit = int(days_ago)*24
                except ValueError:
                    # Handle the case where the date is not in the expected format
                    online_seit = "Unknown"


            zimmer = soup.find('div', id='freitext_0')
            zimmer = zimmer.find('p').get_text().strip() 
            zimmer = re.sub('[^a-zA-ZäöüÄÖÜß-]', ' ', zimmer) if zimmer else 'Unknown'

            lage = soup.find('div', id='freitext_1')
            lage = lage.find('p').get_text().strip() 
            lage = re.sub('[^a-zA-ZäöüÄÖÜß-]', ' ', lage) if lage else 'Unknown'

            wg_leben = soup.find('div', id='freitext_2')
            wg_leben = wg_leben.find('p').get_text().strip() 
            wg_leben = re.sub('[^a-zA-ZäöüÄÖÜß-]', ' ', wg_leben) if wg_leben else 'Unknown'

            sonstiges = soup.find('div', id='freitext_3')
            sonstiges = sonstiges.find('p').get_text().strip()
            sonstiges = re.sub('[^a-zA-ZäöüÄÖÜß-]', ' ', sonstiges) if sonstiges else 'Unknown'

            fraternity = contains_any_words([zimmer,lage,wg_leben,sonstiges])
            fraternity_likely = (int(wg_groesse)>5) & (int(miete)<500)
         
            sentiment=calculate_composite_sentiment(zimmer,lage,wg_leben,sonstiges)['overall_sentiment']

            link = html_list['link'].iloc[0]

            anzeigen.append({
                'titel': titel,
                'bewohner': int(wg_groesse),
                'groesse': int(groesse),
                'miete': int(miete),
                'strasse': strasse,
                'plz': int(plz),
                'online_seit': online_seit,
                'sentiment': float(sentiment),
                'verbindung': fraternity,
                'verbindung_moeglich': fraternity_likely,
                'zimmer': zimmer,
                'lage': lage,
                'wg_leben': wg_leben,
                'sonstiges': sonstiges,
                'link': link
                
            })

        except Exception as e:
            #print(f"An error occurred: {e}, link: {html_list['link'].iloc[0]}")
            errors += 1
            continue
            # Specify the file path
    file_path = 'anzeigen.csv'
    # Save DataFrame to CSV
    pd.DataFrame(anzeigen).to_csv(file_path, index=False, encoding='utf-8')

    return pd.DataFrame(anzeigen)

#Get new links, State how many pages (20 links per page) => Call with 20 -> 400 listings
#links = get_wg_links(20)

#Get the html
#anzeigen_html = get_anzeigen_html(links)

#Get Dataframe
anzeigen = get_anzeigen_from_html()
display(anzeigen)