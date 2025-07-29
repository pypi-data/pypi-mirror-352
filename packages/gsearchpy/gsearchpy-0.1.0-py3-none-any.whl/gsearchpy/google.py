
import os
import time
import json
import random
import traceback

from seleniumbase import SB
from user_agent import generate_user_agent
from curl_cffi import requests
from bs4 import BeautifulSoup


ROOT = os.path.dirname(os.path.abspath(__file__))
cookies_path = os.path.join(ROOT, "cookies.json")


# Random keyword list
keywords = [
    "how to build a web scraper in python",
    "best VSCode extensions for productivity",
    "why do cats purr",
    "funniest AI fails",
    "top programming languages 2025",
    "how long can a snail sleep",
    "Python automation",
    "docker vs kubernetes",
    "is cereal a soup",
    "latest AI tools 2025",
    "how to deploy Django on AWS",
    "machine learning vs deep learning",
    "difference between Git and GitHub",
    "how do magnets work",
    "top 10 coding interview questions",
    "why JavaScript is weird",
    "should you learn Rust in 2025",
    "is pineapple on pizza good",
    "best Linux distros for developers",
    "how to contribute to open source",
    "what is quantum computing",
    "top VSCode themes for night coding",
    "build a chatbot with Python",
    "why is regex so hard",
    "what does an AI model see",
    "best keyboard shortcuts in VSCode",
    "how to stay focused while coding",
    "is ChatGPT replacing developers",
    "top 5 Python libraries for automation",
    "how does DNS work"
]


def human_typing(sb, selector, text, delay=0.1):
    for char in text:
        sb.send_keys(selector, char)
        time.sleep(random.uniform(delay - 0.05, delay + 0.05))


def human_typing(sb, selector, text):
    for char in text:
        sb.type(selector, char, by="css selector", timeout=1)
        time.sleep(random.uniform(0.05, 0.15))


def create_cookies():
    random_keyword = random.choice(keywords)
    user_agent = generate_user_agent(navigator='chrome')

    with SB(uc=True, headless=True, cft=True) as sb:
        sb.driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": user_agent})
        url = "https://www.google.com"
        sb.activate_cdp_mode(url)
        try:
            sb.open(url)

            # List of possible consent buttons in various languages
            accept_buttons = [
                'button:contains("Acceptă tot")',
                'button:contains("Accept all")',
                'button:contains("Aceptar todo")',
                'button:contains("Alle akzeptieren")',
                'button#L2AGLb'
            ]

            # Flag to track if any consent popup was found and clicked
            accept_clicked = False

            for btn in accept_buttons:
                try:
                    sb.wait_for_element_visible(btn, timeout=3)
                    sb.click(btn)
                    # print(f"✅ Clicked accept button: {btn}")
                    time.sleep(1)
                    accept_clicked = True
                    break  # Exit loop after first successful click
                except Exception as e:
                    pass
                    # print(f"⚠️ Not found: {btn} | Skipping...")

            # if not accept_clicked:
            #     print("No accept popup found. Continuing without clicking.")

            # Wait for the search box, type the keyword
            sb.wait_for_element("textarea.gLFyf", timeout=10)
            human_typing(sb, "textarea.gLFyf", random_keyword)

            # Submit the search using JavaScript
            sb.execute_script("document.querySelector('textarea.gLFyf').form.submit();")

            sb.wait_for_element("#search", timeout=10)
            time.sleep(random.uniform(2, 4))

            # Get cookies and save to file
            ck = sb.get_cookies()
            cookies = {c.get('name'): c.get('value') for c in ck}

            with open(cookies_path, "w") as f:
                json.dump(cookies, f, indent=4)

            # print("Cookies saved to cookies.json")

        except Exception as e:
            traceback.print_exc()
            print("Kuch gadbad ho gaya:", e)
            sb.save_screenshot("debug_screenshot.png")

    return cookies_path


def get_header():
    return {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'downlink': '10',
        'priority': 'u=0, i',
        'referer': 'https://www.google.com/',
        'rtt': '50',
        'sec-ch-prefers-color-scheme': 'dark',
        'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-form-factors': '"Desktop"',
        'sec-ch-ua-full-version': '"135.0.7049.114"',
        'sec-ch-ua-full-version-list': '"Google Chrome";v="135.0.7049.114", "Not-A.Brand";v="8.0.0.0", "Chromium";v="135.0.7049.114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Linux"',
        'sec-ch-ua-platform-version': '"6.11.0"',
        'sec-ch-ua-wow64': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'upgrade-insecure-requests': '1',
        'user-agent': generate_user_agent(navigator='chrome'),
        'x-browser-channel': 'stable',
    }

def read_cookies(path):
    with open(path, "r") as f:
        cookies = json.load(f)
    return cookies

def get_response_from_google(params, retry=3):
    try:
        cookies = None
        if os.path.exists(cookies_path):
            cookies = read_cookies(cookies_path)
        else:
            _ = create_cookies()
            cookies = read_cookies(cookies_path)
        

        headers = get_header()
        time.sleep(random.uniform(1, 3))
        response = requests.get("https://www.google.com/search", params=params, headers=headers, cookies=cookies, impersonate="chrome")
        data = response.content.decode("utf-8")
        if "SearchResultsPage" in data:
            return data, response
        else:
            if retry > 0:
                _ = create_cookies()
                print(f"Retrying...")
                return get_response_from_google(params, retry - 1)
            return None, response
    except Exception as e:
        traceback.print_exc()
        print(e)


def google_search(query, hl="en", gl="in", num=20, start=0, safe="active", unique="0", tbm=None, tbs=None, 
                  **kwargs):
    """
    Perform a Google search and return the search results.

    Parameters:
    ----------
    query : str
        The search query to be submitted to Google.
    hl : str, optional
        Interface language of the search results (default is "en").
    gl : str, optional
        Geolocation or country code for localizing search results (default is "in").
    num : int, optional
        Number of results to fetch per page (default is 20; max allowed is 100).
    start : int, optional
        The index of the first result to return (used for pagination; default is 0).
    safe : str, optional
        Enables or disables Google's SafeSearch (default is "active").
    unique : str, optional
        Enables duplicate content filtering ("1") or disables it ("0") (default is "0").
    tbm : str, optional
        Specifies the type of search (e.g., "isch" for images, "vid" for videos, "lcl" for local search).
    tbs : str, optional
        Applies additional search filters such as date range.
    **kwargs : dict
        Any additional parameters to be included in the search request.

    Returns:
    -------
    dict
        A dictionary of query parameters to be used in a Google search URL.
    """
    params = {
        "q": query,
        "hl": hl,
        "gl": gl,
        "num": num,
        "start": start,
        "safe": safe,
        "filter": unique,
    }

    if tbm:
        params["tbm"] = tbm
    if tbs:
        params["tbs"] = tbs

    params.update(kwargs)
    data, response =get_response_from_google(params)
    return data



def get_sponsor_data(sp_data):
    data = {}
    
    sponsor_data = sp_data.find('div', {'class': 'v5yQqb'})
    span = sponsor_data.find("span", {'class': 'OSrXXb'})
    header = span.text if span else None
    if header:
        data.update({"header": header})

    description_data = sp_data.find('div', {'class': 'p4wth'})
    description = description_data.text if description_data else None
    if description:
        data.update({"description": description})

    a_tag = sponsor_data.find('a')
    
    title = None
    link = None
    logo = None
    if a_tag:
        link = a_tag.get('href')
        title = a_tag.find('span').text if a_tag.find('span') else None
        logo = a_tag.find("img").get("src") if a_tag.find("img") else None

    if link:
        data.update({"link": link})
    
    if logo:
        data.update({"logo_link": logo})
    
    if title:
        data.update({"title": title})

    return data

def get_box_data(box):
    data = {}
    box_data = box.find("span", {"class": "V9tjod"})
    if not box_data:
        return data
    
    link = box_data.find("a").get("href")
    if link:
        data.update({"link": link})
    
    logo = box_data.find("img").get("src")
    if logo:
        data.update({"logo_link": logo})
    
    title = box_data.find("h3").text if box_data.find("h3") else None
    if title:
        data.update({"title": title})

    header_data = box_data.find('div', {'class': "CA5RN"})
    header = None
    header_details = None
    if header_data:
        header = header_data.find('span').text if header_data.find('span') else None
        header_div = header_data.find('div', {'class': 'byrV5b'})
        header_details = header_div.text if header_div else None

    if header:
        data.update({"header": header})

    if header_details:
        data.update({"header_details": header_details})

    description_data = box.find('div', {'class': 'kb0PBd A9Y9g'})
    description = None
    if description_data:
        description = description_data.find('span').text if description_data.find('span') else None

    if description:
        data.update({"description": description})

    return data

def filter_google_search_data(html):
    """
    Filters Google search data based on the provided HTML content.

    Parameters:
    -----------
    html : str
        The HTML content to filter.

    Returns:
    -------
    dict
        A dictionary containing the filtered Google search data.
    """
    if not html:
        return {"error": "Please pass proper html data"}
    
    soup = BeautifulSoup(html, "lxml")
    
    searchs = soup.find('div', {"id": "search"})
    containers = searchs.find_all("div", {"class": "MjjYud"})
    if not containers:
        return {"error": "No data found in google search! Please check the data!"}

    final_data = []

    taw = soup.find('div', {'id': 'taw'})
    if taw:
        dt = get_sponsor_data(taw)
        final_data.append(dt)
        
    for box in containers:
        if not box.find(True):
            continue
        dt = get_box_data(box)
        if dt:
            final_data.append(dt)
    
    return {"data": final_data}


