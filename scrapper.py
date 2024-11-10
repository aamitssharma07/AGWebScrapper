from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from datetime import datetime
import json
import pandas as pd

def scrape_agriculture_article(url):
    # Step 1: Setup Selenium WebDriver for Firefox with options to ignore SSL errors
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--ignore-certificate-errors')  # Ignore SSL errors
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Initialize the Firefox WebDriver
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

    # Step 2: Load the page
    driver.get(url)

    # Step 3: Parse the page source with Beautiful Soup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Step 4: Close the driver
    driver.quit()

    # Step 5: Extract the headline, subheadline, date, and content
    headline = soup.select_one('h1.Page-headline').get_text(strip=True) if soup.select_one('h1.Page-headline') else 'Not found'
    subheadline = soup.select_one('h2.Page-subHeadline').get_text(strip=True) if soup.select_one('h2.Page-subHeadline') else 'Not found'
    date_str = soup.select_one('div.Page-datePublished').get_text(strip=True) if soup.select_one('div.Page-datePublished') else None

    # Convert the date string to datetime format
    if date_str:
        try:
            date = datetime.strptime(date_str, '%B %d, %Y %I:%M %p')  # Adjust format as needed
        except ValueError as e:
            print(f"Date parsing error: {e}")
            date = 'Invalid date format'
    else:
        date = 'Not found'

    content_div = soup.find('div', class_='RichTextArticleBody RichTextBody')
    content = ' '.join([p.get_text(strip=True) for p in content_div.find_all('p')]) if content_div else 'Not found'

    # Step 6: Create a dictionary for the data
    data = {
        'headline': headline,
        'subheadline': subheadline,
        'date': date if isinstance(date, str) else date.strftime('%Y-%m-%d %H:%M:%S'),
        'content': content
    }

    # Step 7: Save data as JSON
    with open('output.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    # Step 8: Save data as CSV
    df = pd.DataFrame([data])  # Create a DataFrame with the data dictionary
    df.to_csv('output.csv', index=False, encoding='utf-8')

    # Print confirmation
    print("Data has been saved to output.json and output.csv")
    return data

# Example usage
url = 'https://www.agweb.com/news/crops/soybeans/u-s-agriculture-faces-growing-trade-deficit-usda-projects-record-ag-trade-def'
article_data = scrape_agriculture_article(url)
print(article_data)
