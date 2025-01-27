"""googlesearch is a Python library for searching Google, easily."""
from time import sleep
import logging
from bs4 import BeautifulSoup
from requests import get, RequestException
from urllib.parse import unquote
from .user_agents import get_useragent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def _req(term, results, lang, start, proxies, timeout, safe, ssl_verify, region):
    try:
        resp = get(
            url="https://www.google.com/search",
            headers={
                "User-Agent": get_useragent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": f"{lang};q=0.8,en-US;q=0.5,en;q=0.3",
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
                'CONSENT': 'YES+cb.20210328-17-p0.en+FX+{}'.format(region if region else '410'),
                'SOCS': 'CAESHAgBEhJaAB',
                'NID': '511=random_string', # Add random string for NID cookie
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
    """Search the Google search engine with improved error handling and rate limiting avoidance"""
    
    try:
        # Proxy setup with rotation support
        proxies = {"https": proxy, "http": proxy} if proxy and (proxy.startswith("https") or proxy.startswith("http")) else None

        start = start_num
        fetched_results = 0
        fetched_links = set()
        retry_count = 0
        max_retries = 3

        while fetched_results < num_results:
            try:
                # Implement exponential backoff for retries
                if retry_count > 0:
                    sleep_time = min(300, (2 ** retry_count) + random.uniform(0, 1))
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    sleep(sleep_time)

                resp = _req(term, num_results - start,
                          lang, start, proxies, timeout, safe, ssl_verify, region)
                
                soup = BeautifulSoup(resp.text, "html.parser")
                result_block = soup.find_all("div", attrs={"class": ["ezO2md", "g"]})  # Multiple class support
                
                if not result_block:
                    logger.warning("No results found in the response")
                    if retry_count < max_retries:
                        retry_count += 1
                        continue
                    break

                new_results = 0
                
                for result in result_block:
                    link_tag = result.find("a", href=True)
                    title_tag = result.find(["h3", "span"], class_=["CVA68e", "DKV0Md"]) if link_tag else None
                    description_tag = result.find(["span", "div"], class_=["FrIlee", "VwiC3b"])

                    if not all([link_tag, title_tag, description_tag]):
                        continue

                    link = unquote(link_tag["href"].split("&")[0].replace("/url?q=", ""))
                    
                    if not link.startswith(('http://', 'https://')):
                        continue

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

                if new_results == 0:
                    logger.info(f"Found {fetched_results} results out of {num_results} requested")
                    break

                start += 10
                sleep(sleep_interval + random.uniform(0, 2))  # Add randomization to sleep
                retry_count = 0  # Reset retry count after successful request

            except Exception as e:
                logger.error(f"Error during search: {str(e)}")
                if retry_count < max_retries:
                    retry_count += 1
                    continue
                raise

    except Exception as e:
        logger.error(f"Fatal error in search: {str(e)}")
        raise
