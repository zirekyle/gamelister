#!/usr/bin/env python

# Name: gamelister.py
# Desc: Interfaces with the IGDB.com API

import json
import logging
import sys
import csv
import datetime

from igdb_api_python import igdb

# Location of the API key file
key_file = '.igdb_api_key'

logger = logging.getLogger(__name__)


def api_connect(api_key_file):
    """
    Establish a connection to the IGDB API
    :param api_key_file: file containing the API key
    :return: active IGDB API connection object
    """

    try:
        api_file = open(api_key_file, "r")
    except FileNotFoundError:
        sys.exit("API key file '{}' not found. Aborting.".format(api_key_file))

    return igdb.igdb(api_file.readline())


def genre_name(genre_id):

    genre_ids = {
        2: 'Point-and-Click',
        4: 'Fighting',
        5: 'Shooter',
        7: 'Music',
        8: 'Platformer',
        9: 'Puzzle',
        10: 'Racing',
        11: 'RTS',
        12: 'RPG',
        13: 'Simulator',
        14: 'Sports',
        15: 'Strategy',
        16: 'Turn-based Strategy',
        24: 'Tactics',
        25: "Beat em up",
        26: 'Trivia',
        30: 'Pinball',
        31: 'Adventure',
        32: 'Indie',
        33: 'Arcade'
    }

    name = genre_ids.get(genre_id)

    return name


def clean_time(epoch_time_milliseconds):
    """
    Convert an epoch time to a clean local time
    :param epoch_time_milliseconds: epoch time
    :return: YYYY-MM-DD HH:MM:SS in local time
    """
    epoch_time_milliseconds += 3600 * 6     # Add 6 hours to adjust for GMT
    return datetime.datetime.fromtimestamp(int(epoch_time_milliseconds)).strftime('%B %d, %Y')


def get_all_games(igdb, filter_group, field_group):
    """
    Return all games from the API, iterating through via offsets.
    This is required because of the 50 response limit of the API.
    :param igdb: IGDB API connection
    :param filter_group: group of filters to request by
    :param field_group: group of fields to return
    :return: list object of matching games
    """

    full_result = []
    offset = 0

    try:
        total = int(igdb.games({'filters': filter_group, 'scroll': 1}).headers['X-Count'])
    except KeyError:
        total = 50

    while offset < total:
        logger.info("Pulling results {} to {} (of {})...".format(offset, offset + 49, total))
        result = igdb.games({'filters': filter_group, 'fields': field_group, 'limit': 50, 'offset': offset})
        logger.debug(json.dumps(result.json(), indent=4))
        full_result += result.json()
        offset += 50

    return full_result


def write_to_csv(csv_filename, object_input, field_names, sort_field, singlestons_only=False):
    """
    Write the keys/values of an object into a given .csv
    :param csv_filename: the filename to write to
    :param object_input: the object to write
    :param field_names: list of fields to write
    :param sort_field: field to sort by
    :param singlestons_only: only include games released for a single platform
    :return: success code (0: success, 1: failed)
    """

    with open(csv_filename, 'wt', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        for obj in sorted(object_input, key=lambda x: x[sort_field]):
            try:
                if singlestons_only and len(obj['platforms']) > 1:
                    continue
            except KeyError:
                continue

            try:
                new_genre_list = []
                for genre in obj['genres']:
                    new_genre_list.append(genre_name(genre))
                obj['genres'] = ', '.join(new_genre_list)
            except KeyError:
                logging.info("No genre for {}".format(obj['name']))

            try:
                obj['first_release_date'] = clean_time(int(obj['first_release_date'] / 1000))
            except KeyError:
                logging.info("No release date for {}".format(obj['name']))

            try:
                writer.writerow(dict(obj.items()))
            except UnicodeEncodeError:
                obj['name'] = str(obj['name'].encode('utf-8'))
                writer.writerow(dict(obj.items()))

    return 0


def main():
    """
    Main function to gather information from IGDB API
    :return: null
    """

    db = api_connect(key_file)

    filters = {'[platforms][eq]': 11}

    fields = ['id', 'name', 'platforms',
              'total_rating', 'genres', 'first_release_date']

    games = get_all_games(db, filters, fields)

    write_to_csv('all_xbox_games.csv', games, fields, 'name', singlestons_only=True)


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='%(name)s %(message)s')

    main()
