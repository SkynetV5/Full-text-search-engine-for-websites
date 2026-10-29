import requests
from bs4 import BeautifulSoup


def crawl_url(url):
    headers = {"user-agent": "my-app/0.0.1"}

    robot_file_split = url.split("/")
    robot_file = robot_file_split[0] + "//" + robot_file_split[2] + "/robots.txt"
    print(robot_file)

    r = requests.get(url=robot_file, headers=headers)

    robot_file_html = r.text

    print(robot_file_html)
    # r = requests.get(url=url, headers=headers)

    # if r.status_code != 200:
    #     return ConnectionError

    # html = r.text
    # soup = BeautifulSoup(html, features="html.parser")
    # for a in soup.find_all("a", href=True):
    #     if a["href"] != "#" and a["href"].startswith("https"):
    #         print(a["href"])


print(crawl_url("https://pl.wikipedia.org/wiki/Siogun"))
