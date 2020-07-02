"""
A program for automatically downloading xkcd comics.
"""

import time
import random
import threading
import os
import json
import argparse
import requests


def get_xkcd_info(number: str) -> tuple:
    """ Gets the xkcd url for the comic number """
    source = requests.get(f"https://xkcd.com/{number}/info.0.json").content

    data = json.loads(source)

    # Get's the image address of the comic
    img_source = data["img"]

    # Gets the file name of the comic
    file_name = img_source[img_source.rfind("/") + 1:]

    return file_name, data


def save_xkcd_comic(number: str, output_dir: str) -> None:
    """ Saves the comic as an image """
    file_name, data = get_xkcd_info(number)

    # Writes image to file
    img_data = requests.get(data["img"]).content
    with open(f"{output_dir}/{file_name}", "wb") as handler:
        handler.write(img_data)


def get_latest_comic() -> str:
    """ Returns the number of the latest comic as a string"""
    data = json.loads(requests.get("https://xkcd.com/info.0.json").content)
    return str(data["num"])


def parse_arguments() -> tuple:
    """ Parses the command-line arguments """
    # Default arguments
    start, stop = 1, 100
    comics = []
    output_dir = "./xkcd_comics"

    # New parser object
    parser = argparse.ArgumentParser(description="A program for automatically downloading xkcd comics")

    parser.add_argument("-o", "--output", help="the path to save comics", default=output_dir)
    parser.add_argument("-r", "--range", help="range of comics", type=int, nargs=2, default=(start, stop))
    parser.add_argument("-l", "--list", help="list of comics", type=int, nargs="+", default=comics)
    parser.add_argument("--latest", help="latest comic", action="store_true")
    parser.add_argument("--random", help="a random comic", nargs="?", type=int, const=1)

    args = parser.parse_args()

    output_dir = args.output
    start, stop = args.range
    comics = args.list

    if args.random:
        for _ in range(args.random):
            comics.append(str(random.randint(1, int(get_latest_comic()))))

    if args.latest:
        comics.append(get_latest_comic())

    return start, stop, comics, output_dir


def main(start: str, stop: str, comics: list, output_dir: str) -> None:
    """ Main function """
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    if comics == []:
        comics = list(range(int(start), int(stop)))

    if 404 in comics:  # 404 is not a comic
        comics.remove(404)

    for comic in comics:
        if int(comic) < 1 or int(comic) > int(get_latest_comic()):
            raise Exception(f"Number {comic} is not a comic!")

    threads = []
    for comic in comics:
        thread = threading.Thread(target=save_xkcd_comic, args=(comic, output_dir,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    before = time.time()
    main(*parse_arguments())
    after = time.time()
    seconds = (after - before) % 60
    minutes = int(((after - before) - seconds) / 60)
    print(f"Time took: {minutes} minutes and {seconds} seconds", sep="")
    input("Press Enter to Continue: ")
