import requests
import trafilatura
from copy import deepcopy
from trafilatura.settings import DEFAULT_CONFIG
from selenium import webdriver
from selenium_stealth import stealth
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv
import os
import justext
from newspaper import Article
import requests
from bs4 import BeautifulSoup
import time

def extractMainText(body, formatting = 'txt'):

    _algo1 = algo1(body, formatting)

    _algo2 = algo2(body, formatting)

    if len(_algo2) > len(_algo1):
        return _algo2
    else:
        return  _algo1


def algo1(body, formatting = 'txt'):
    config = deepcopy(DEFAULT_CONFIG)
    config['DEFAULT']['EXTRACTION_TIMEOUT'] = '0'

    # use formatting only with markdown
    if (formatting == 'markdown'):
        formatting = True
    else:
        formatting = False

    result = trafilatura.extract(body, include_formatting=formatting,
                                 config=config, )

    return result

def algo2(body, formatting = 'txt'):



    text = ""
    contents = justext.justext(body, justext.get_stoplist("English"))

    for content in contents:
        if not content.is_boilerplate and not content.is_heading:
            text += content.text + "\n\n"

        if not content.is_boilerplate and content.is_heading:
            if formatting == 'markdown':
                text += "\n\n<h2>" + content.text + "</h2>\n\n"
            else:
                text += "\n\n" + content.text + "\n\n"

    return text

def algo3(body, formatting = 'txt'):
    article = Article('')
    article.set_html(body)
    article.parse()
    text = article.text
    return text

def isSinglePage(html_content):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all <noscript> tags
    noscript_tags = soup.find_all('noscript')

    # Check the count of <noscript> tags
    if len(noscript_tags) == 1:
        # Check if the <noscript> tag has text content
        noscript_text = noscript_tags[0].get_text()
        if noscript_text.strip():
            return True  # There's one <noscript> tag with content
    return False  # Either no <noscript> tags or more than one


def getPageTitle(html_content):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the <title> tag
    title_tag = soup.find('title')

    # Check if a <title> tag was found
    if title_tag:
        title_text = title_tag.get_text(strip=True)
        return title_text
    else:
        return ""  # No <title> tag found

def getWebBodyWithChrome(url):

    print('using chrome')

    load_dotenv()

    # Get the paths from environment variables
    chrome_path = os.getenv("CHROME_PATH")

    chromedriver_path = os.getenv("CHROME_DRIVER_PATH")
    service = Service(chromedriver_path)

    # Set up options for Chrome in headless mode
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU for headless mode
    chrome_options.add_argument("--disable-extensions")  # Disable extensions
    chrome_options.add_argument('--disable-image-loading') # disable image loading
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Initialize the Chrome WebDriver with stealth capabilities


    # Use the provided Chrome and Chrome WebDriver paths
    chrome_options.binary_location = chrome_path
    driver = webdriver.Chrome(service=service, options=chrome_options)


    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)

    try:
        # Set the timeout for implicit waits (100 seconds)
        driver.implicitly_wait(100)

        # Navigate to the URL
        driver.get(url)

        time.sleep(20)

        # Get the page source (body)
        page_body = driver.page_source

        # Close the WebDriver
        driver.quit()

        # Create a BeautifulSoup object
        soup = BeautifulSoup(page_body, 'html.parser')

        # Find and remove all <noscript> tags
        noscript_tags = soup.find_all('noscript')
        for tag in noscript_tags:
            tag.extract()

        return str(soup)

    except Exception as e:
        print(e)
        # Handle the timeout error here
        raise Exception(f"Error fetching URL: {url}")



