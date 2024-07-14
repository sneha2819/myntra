#extract data from wiki page
from bs4 import BeautifulSoup
import requests
import csv
import string

# Function to scrape attributes from an individual aesthetic page
def scrape_aesthetic(aesthetic_url):
    try:
        response = requests.get(aesthetic_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.content, 'html.parser')

        aesthetic_name = soup.find('h1', class_='page-header__title').text.strip()

        decade_element = soup.find('h3', text='Decade of origin')
        decade = decade_element.find_next_sibling('div').text.strip() if decade_element else 'null'

        motifs_element = soup.find('h3', text='Key motifs')
        motifs = motifs_element.find_next_sibling('div').text.strip() if motifs_element else 'null'

        colours_element = soup.find('h3', text='Key colours')
        colours = colours_element.find_next_sibling('div').text.strip() if colours_element else 'null'

        related_aesthetics_element = soup.find('h3', text='Related aesthetics')
        related_aesthetics = related_aesthetics_element.find_next_sibling('div').text.strip() if related_aesthetics_element else 'null'

        related_media_element = soup.find('h3', text='Related media')
        related_media = related_media_element.find_next_sibling('div').text.strip() if related_media_element else 'null'

        return [aesthetic_name, decade, motifs, colours, related_aesthetics, related_media]

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {aesthetic_url}: {e}")
        return None

# Main script to scrape aesthetics Y-Z
base_url = 'https://aesthetics.fandom.com'
start_url = base_url + '/wiki/Category:Fashion?from='

data = []

try:
    # Generate URLs for each letter from Y-Z
    for char in string.ascii_uppercase[string.ascii_uppercase.index('Y'):]:
        next_page = start_url + char

        while next_page:
            response = requests.get(next_page)
            response.raise_for_status()  # Raise an exception for HTTP errors
            soup = BeautifulSoup(response.content, 'html.parser')

            aesthetics = soup.find_all('a', class_='category-page__member-link')

            for aesthetic in aesthetics:
                aesthetic_url = base_url + aesthetic['href']
                data.append(scrape_aesthetic(aesthetic_url))

            # Check for next page link
            next_page_link = soup.find('a', class_='category-page__pagination-next')
            next_page = base_url + next_page_link['href'] if next_page_link else None

except requests.exceptions.RequestException as e:
    print(f"Error with request: {e}")

# Write data to CSV
headers = ['Aesthetic', 'Decade of origin', 'Key motifs', 'Key colours', 'Related aesthetics', 'Related media']

with open('aesthetics_data_Y-Z.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows([item for item in data if item is not None])

