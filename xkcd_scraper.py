"""
A program for automatically downloading xkcd comics.
"""

import time
import random
import os
import json
import argparse
from itertools import repeat
import urllib.request
from concurrent.futures import ThreadPoolExecutor


def get_xkcd_info(number: int) -> tuple:
    """ Gets the xkcd url for the comic number """
    source = urllib.request.urlopen(f"https://xkcd.com/{number}/info.0.json")

    data = json.loads(source.read())

    # Get's the image address of the comic
    img_source = data["img"]

    # Gets the file name of the comic
    file_name = img_source[img_source.rfind("/") + 1:]

    return file_name, data


def save_xkcd_comic(number: int, output_dir: str, numbered: bool) -> None:
    """ Saves the comic as an image """
    file_name, data = get_xkcd_info(number)

    # Prepends comic number to filename if wanted
    if numbered:
        file_name = f"{number}_{file_name}"

    # Tells the user what comic
    print(f"Saving comic number {number} as {output_dir}/{file_name}!")

    # Writes image to file
    img_data = urllib.request.urlopen(data["img"])
    with open(f"{output_dir}/{file_name}", "wb") as handler:
        handler.write(img_data.read())


def get_latest_comic() -> int:
    """ Returns the number of the latest comic """
    data = json.loads(urllib.request.urlopen("https://xkcd.com/info.0.json").read())

    return data["num"]


def parse_arguments() -> tuple:
    """ Parses the command-line arguments """
    # New parser object
    parser = argparse.ArgumentParser(description="A program for automatically downloading xkcd comics")

    # Arguments with default parameters
    parser.add_argument("-o", "--output", help="The path to save comics", default="./xkcd_comics")
    parser.add_argument("-r", "--range", help="Range of comics to download(Inclusive, exclusive).",
                        type=int, nargs=2, default=(1, 1))
    parser.add_argument("-l", "--list", help="List of comics to download",
                        type=int, nargs="+", default=[])
    parser.add_argument("--latest", help="Download the latest comic", action="store_true")
    parser.add_argument("--random", help="Download a random comic", nargs="?", type=int, const=1)
    parser.add_argument("-n", "--numbered", help="Prepend comic number to filename",
                        action="store_true")

    args = parser.parse_args()

    output_dir = args.output
    start, stop = args.range
    comics = args.list
    numbered = args.numbered  # Option to prepend number (bool)

    comics.extend(range(start, stop))

    if args.random:
        for _ in range(args.random):
            comics.append(random.randint(1, get_latest_comic()))

    if args.latest:
        comics.append(get_latest_comic())

    return comics, output_dir, numbered


def main(comics: list, output_dir: str, numbered: bool) -> None:
    """ Main function """
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    comics = list(set(comics))  # Removes any duplicates

    latest = get_latest_comic()

    for comic in comics:
        if comic < 1 or comic > latest:
            comics.remove(comic)
        if comic == 404:  # 404 is not a comic
            comics.remove(404)

    if comics == []:
        # Asks for confirmation if no arguments specified
        p = input("No command line arguments were entered. You you want to download the first 100 comics (yes or no)?")
        if p.lower()[0] == 'y':
            comics = list(range(1, 100))  # Default values when none are specified

    before = time.time()

    print("Starting to download!")

    with ThreadPoolExecutor(max_workers=10) as executer:
        executer.map(save_xkcd_comic, comics, repeat(output_dir), repeat(numbered))

    print("Finished downloading!")

    after = time.time()
    seconds = (after - before) % 60
    minutes = int((after - before - seconds) / 60)
    print(f"Time took: {minutes} minutes and {seconds} seconds", sep="")


if __name__ == "__main__":
    main(*parse_arguments())
    input("Press enter to continue: ")
