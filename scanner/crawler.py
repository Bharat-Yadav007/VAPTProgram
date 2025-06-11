# scanner/crawler.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import robotexclusionrulesparser
from time import sleep

class Crawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'VAPT-Scanner/1.0 (Educational Purpose Only)'
        })
        self.parser = robotexclusionrulesparser.RobotExclusionRulesParser()

    def check_robots_txt(self, url):
        try:
            domain = urlparse(url).scheme + "://" + urlparse(url).netloc
            robots_url = urljoin(domain, "/robots.txt")
            self.parser.fetch(robots_url)
            return True
        except Exception:
            return False

    def is_allowed(self, url):
        return self.parser.is_allowed("*", url)

def crawl(url, max_links=10, delay=1):
    print("\n[+] Crawling site for internal links...")
    crawler = Crawler()
    visited = set()
    internal_links = []

    # Check robots.txt
    if crawler.check_robots_txt(url):
        print("  [+] Found robots.txt, respecting rules")

    try:
        base_domain = urlparse(url).netloc
        res = crawler.session.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')

        from bs4.element import Tag

        for a_tag in soup.find_all("a", href=True):
            if len(internal_links) >= max_links:
                break

            if not isinstance(a_tag, Tag):
                continue
            href = a_tag.get("href")
            if not isinstance(href, str):
                continue
            full_url = urljoin(url, href)
            parsed = urlparse(full_url)
            
            if (parsed.netloc == base_domain and 
                full_url not in visited and 
                crawler.is_allowed(full_url)):
                
                try:
                    # Rate limiting
                    sleep(delay)
                    check = crawler.session.head(full_url, timeout=5)
                    if check.status_code == 200:
                        internal_links.append(full_url)
                        visited.add(full_url)
                        print(f"  [+] Found: {full_url}")
                except requests.RequestException as e:
                    print(f"  [-] Error checking {full_url}: {str(e)}")

    except requests.RequestException as e:
        print(f"  [!] Error crawling {url}: {str(e)}")
    except Exception as e:
        print(f"  [!] Unexpected error: {str(e)}")

    print(f"  [+] Found {len(internal_links)} valid internal links")
    return internal_links
