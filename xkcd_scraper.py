"""
A program for automatically downloading xkcd comics
"""

import time
import threading
import os
import sys
import requests

sys.path.append("./dependencies")
from bs4 import BeautifulSoup


def get_xkcd_source(number: int) -> tuple:
    """ Gets the xkcd url for the comic number """
    # Reads the xkcd comic page and gets the source code
    html = requests.get("https://xkcd.com/" + str(number)).content

    # New soup object on html source
    soup = BeautifulSoup(html, "html.parser")

    # Get's the image address of the comic
    attributes = soup.find(id="comic").find("img").attrs
    img_source = "https:" + attributes["src"]

    # Gets the name of the comic
    title = img_source[img_source.rfind("/") + 1:]

    return title, img_source


def save_xkcd_comic(number: int) -> None:
    """ Saves the comic as an image """
    title, img_source = get_xkcd_source(number)

    # Writes image to file
    img_data = requests.get(img_source).content
    with open("./xkcd_comics/" + title, "wb") as handler:
        handler.write(img_data)


def main(start: int = 1, stop: int = 10, comics: None = None) -> None:
    """ Main function """
    comics = []

    if not os.path.isdir("xkcd_comics"):
        os.mkdir("xkcd_comics")

    if comics == []:
        comics = list(range(start, stop))
    if 404 in comics:  # 404 is not a comic
        comics.remove(404)

    threads = []
    for comic in comics:
        thread = threading.Thread(target=save_xkcd_comic, args=(comic,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    before = time.time()
    main(1, 100)
    after = time.time()
    seconds = (after - before) % 60
    minutes = int(((after - before) - seconds) / 60)
    print(f"Time took: {minutes} minutes and {seconds} seconds", sep="")
    input()
