from collections import deque
import time
from urllib import response

import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse


class SimpleCrawler:
    def __init__(self, url, user_agent="MyFirstCrawler/1.0", depth=3, delay_limit=2):
        self.url = url
        self.user_agent = user_agent
        self.depth = depth
        self.delay_limit = delay_limit
        self.queue = deque([(url, 0)])
        self.visited = set()
        self.robots_parsers = {}
        self.downloaded_pages = []

    def _get_robots_parser(self):
        parser = urlparse(self.url)
        domain = f"{parser.scheme}://{parser.netloc}"

        if domain not in self.robots_parsers:
            robot_url = f"{domain}/robots.txt"
            headers = {"User-Agent": self.user_agent}
            try:
                response = requests.get(robot_url, headers=headers)
                if response.status_code == 200:

                    rp = RobotFileParser()
                    rp.set_url(robot_url)
                    rp.parse(response.text.splitlines())
                    self.robots_parsers[domain] = rp
                else:
                    self.robots_parsers[domain] = None
            except Exception as e:
                self.robots_parsers[domain] = None
                print(f"Nie udało się pobrać robots.txt dla domeny {domain}: {e}")

        return self.robots_parsers[domain]

    def can_fetch(self, user_agent):
        rp = self._get_robots_parser()

        if rp is None:
            return True

        can_rp = rp.can_fetch(user_agent, self.url)

        return can_rp

    def crawl_url(self):
        headers = {"user-agent": self.user_agent}

        while self.queue:
            current_url, current_depth = self.queue.popleft()

            if current_url in self.visited or current_depth > self.depth:
                continue

            if not self.can_fetch(self.user_agent):
                continue

            time.sleep(self.delay_limit)

            try:
                r = requests.get(url=current_url, headers=headers)

                if r.status_code != 200:
                    continue

                html = r.text
                soup = BeautifulSoup(html, features="html.parser")
                full_text = soup.get_text()

                self.visited.add(current_url)
                downloaded_page = {"path_url": current_url, "text": full_text}
                self.downloaded_pages.append(downloaded_page)
                print(f"📄 Ścieżka_URL: {current_url} (głębokość: {current_depth})")
                for a in soup.find_all("a", href=True):
                    if a["href"] != "#" and a["href"].startswith("https"):
                        next_url = urljoin(current_url, a["href"])
                        self.queue.append((next_url, current_depth + 1))

            except Exception as e:
                print(f"Nie udało się pobrać strony {current_url}: {e}")
                continue
        return self.downloaded_pages


if __name__ == "__main__":
    crawler = SimpleCrawler(url="https://pl.wikipedia.org/wiki/Siogun")
    crawler.crawl_url()
