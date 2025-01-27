"""googlesearch is a Python library for searching Google, easily."""
import time
import logging
import random
from bs4 import BeautifulSoup
from requests import get, RequestException
from urllib.parse import unquote
from googlesearch.user_agents import get_useragent

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def _req(term, results, lang, start, proxies, timeout, safe, ssl_verify, region):
    """Handle the request to Google with proper error handling"""
    try:
        resp = get(
            url="https://www.google.com/search",
            headers={
                "User-Agent": get_useragent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": f"{lang},en-US;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            },
            params={
                "q": term,
                "num": results + 2,
                "hl": lang,
                "start": start,
                "safe": safe,
                "gl": region,
            },
            proxies=proxies,
            timeout=timeout,
            verify=ssl_verify,
            cookies = {
                'CONSENT': f'YES+cb.{time.strftime("%Y%m%d")}-04-p0.en+FX+{random.randint(100, 999)}',
                'SOCS': 'CAESHAgBEhJnd3NfMjAyMzA2MjctMF9SQzIaAmZpIAEaBgiA_LyaBg',
            }
        )
        resp.raise_for_status()
        return resp
    except RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        raise

class SearchResult:
    def __init__(self, url, title, description):
        self.url = url
        self.title = title
        self.description = description

    def __repr__(self):
        return f"SearchResult(url={self.url}, title={self.title}, description={self.description})"

def search(term, num_results=10, lang="en", proxy=None, advanced=False, sleep_interval=0, timeout=5, safe="active", ssl_verify=None, region=None, start_num=0, unique=False):
    """Search the Google search engine with improved error handling and rate limiting"""
    try:
        # Proxy setup
        proxies = {"https": proxy, "http": proxy} if proxy and (proxy.startswith("https") or proxy.startswith("http")) else None

        start = start_num
        fetched_results = 0
        fetched_links = set()
        
        while fetched_results < num_results:
            try:
                # Add random delay between requests to avoid rate limiting
                if sleep_interval > 0:
                    time.sleep(sleep_interval + random.uniform(0.5, 1.5))
                
                resp = _req(term, num_results - start, lang, start, proxies, timeout, safe, ssl_verify, region)
                soup = BeautifulSoup(resp.text, "html.parser")
                result_block = soup.find_all("div", class_="ezO2md")
                
                if not result_block:
                    logger.warning(f"No results found for query: {term}")
                    break

                new_results = 0

                for result in result_block:
                    try:
                        link_tag = result.find("a", href=True)
                        title_tag = link_tag.find("span", class_="CVA68e") if link_tag else None
                        description_tag = result.find("span", class_="FrIlee")

                        if not all([link_tag, title_tag, description_tag]):
                            continue

                        link = unquote(link_tag["href"].split("&")[0].replace("/url?q=", ""))
                        
                        if link in fetched_links and unique:
                            continue
                            
                        fetched_links.add(link)
                        title = title_tag.text
                        description = description_tag.text
                        
                        fetched_results += 1
                        new_results += 1
                        
                        if advanced:
                            yield SearchResult(link, title, description)
                        else:
                            yield link

                        if fetched_results >= num_results:
                            break

                    except Exception as e:
                        logger.error(f"Error processing search result: {str(e)}")
                        continue

                if new_results == 0:
                    logger.info(f"Only {fetched_results} results found for query requiring {num_results} results")
                    break

                start += 10

            except Exception as e:
                logger.error(f"Error during search: {str(e)}")
                raise

    except Exception as e:
        logger.error(f"Fatal error in search: {str(e)}")
        raise
