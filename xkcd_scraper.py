import time
import threading
import os
import sys
import requests

sys.path.append("./dependencies")
from bs4 import BeautifulSoup


def get_xkcd_image(number: int):
    # Reads the xkcd comic page and gets the source code
    html = requests.get("https://xkcd.com/" + str(number)).content

    # New soup object on html source
    soup = BeautifulSoup(html, "html.parser")

    # Get's the image address of the comic
    attributes = soup.find(id="comic").find("img").attrs
    img_source = "https:" + attributes["src"]

    # Gets the name of the comic
    title = "_".join(soup.find(id="ctitle").getText().split())

    if "?" in title:
        title = "".join(title.split("?"))
    if "/" in title:
        title = "_".join(title.split("/"))

    return title, img_source


def save_xkcd_comic(number: int):
    title, img_source = get_xkcd_image(number)

    # Writes image to file
    img_data = requests.get(img_source).content
    with open("./xkcd_comics/" + title + ".png", "wb") as handler:
        handler.write(img_data)


def main(start=1, stop=10, comics=[]):
    if (comics == []):
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
    if (os.path.isdir("xkcd_comics") == False):
        os.mkdir("xkcd_comics")

    before = time.time()
    main(1, 100)
    after = time.time()
    seconds = (after - before) % 60
    print("time took: ", int(((after - before) - seconds) / 60), " minutes and ", seconds, " seconds", sep="")
