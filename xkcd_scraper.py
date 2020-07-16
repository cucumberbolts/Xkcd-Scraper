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


def get_xkcd_info(number: int) -> tuple:
    """ Gets the xkcd url for the comic number """
    source = requests.get(f"https://xkcd.com/{number}/info.0.json").content

    data = json.loads(source)

    # Get's the image address of the comic
    img_source = data["img"]

    # Gets the file name of the comic
    file_name = img_source[img_source.rfind("/") + 1:]

    return file_name, data


def save_xkcd_comic(number: int, output_dir: str, comic_num: bool) -> None:
    """ Saves the comic as an image """
    print(f"Saving comic {number}!")

    file_name, data = get_xkcd_info(number)

    # Prepends comic number to filename if wanted
    if comic_num:
        file_name = f"{number}_{file_name}"

    # Writes image to file
    img_data = requests.get(data["img"]).content
    with open(f"{output_dir}/{file_name}", "wb") as handler:
        handler.write(img_data)


def get_latest_comic() -> int:
    """ Returns the number of the latest comic """
    data = json.loads(requests.get("https://xkcd.com/info.0.json").content)

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
    comic_num = args.number

    comics.extend(range(start, stop))

    if args.random:
        for _ in range(args.random):
            comics.append(random.randint(1, get_latest_comic()))

    if args.latest:
        comics.append(get_latest_comic())

    if comics == []:
        comics.extend(range(1, 100))  # Default values when none are specified

    return comics, output_dir, comic_num


def main(comics: list, output_dir: str, comic_num: bool) -> None:
    """ Main function """
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    comics = list(set(comics))  # Removes any duplicates

    if 404 in comics:  # 404 is not a comic
        comics.remove(404)

    latest = get_latest_comic()

    for comic in comics:
        if comic < 1 or comic > latest:
            raise Exception(f"Number {comic} is not a comic!")

    threads = []
    print("Starting to download!")
    for comic in comics:
        thread = threading.Thread(target=save_xkcd_comic, args=(comic, output_dir, comic_num,))
        thread.start()
        threads.append(thread)

    print("Finished downloading!")

    for thread in threads:
        thread.join()

    print("Joined threads!")


if __name__ == "__main__":
    before = time.time()
    main(*parse_arguments())
    after = time.time()
    seconds = (after - before) % 60
    minutes = int(((after - before) - seconds) / 60)
    print(f"Time took: {minutes} minutes and {seconds} seconds", sep="")
    input("Press enter to continue: ")
