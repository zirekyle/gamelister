#!/usr/bin/env python

# Name: gamelister.py
# Desc: Interfaces with the IGDB.com API

import json
import logging
import sys
import csv

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


def get_all_games(igdb, filter_group, field_group):
    """
    Return all games from the API, iterating through via offsets.
    This is required because of the 50 response limit of the API.
    :param igdb: IGDB API connection
    :param filters: group of filters to request by
    :param fields: group of fields to return
    :return: list object of matching games
    """

    full_result = []
    offset = 0

    total = int(igdb.games({'filters': filter_group, 'scroll': 1}).headers['X-Count'])

    while offset < total:
        logger.info("Pulling results {} to {} (of {})...".format(offset, offset + 49, total))
        result = igdb.games({'filters': filter_group, 'fields': field_group, 'limit': 50, 'offset': offset})
        logger.debug(json.dumps(result.json(), indent=4))
        full_result += result.json()
        offset += 50

    return full_result


def write_to_csv(csv_filename, object_input, field_names, sort_field):
    """
    Write the keys/values of an object into a given .csv
    :param csv_filename: the filename to write to
    :param object_input: the object to write
    :param field_names: list of fields to write
    :param sort_field: field to sort by
    :return: success code (0: success, 1: failed)
    """

    with open(csv_filename, 'wt', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        for obj in sorted(object_input, key=lambda x: x[sort_field]):
            obj['name'] = str(obj['name'].encode())
            try:
                writer.writerow(dict(obj.items()))
            except UnicodeEncodeError:
                print(json.dumps(obj, indent=4))
    return 1


def main():
    """
    Main function to gather information from IGDB API
    :return: null
    """

    db = api_connect(key_file)

    filters = {'[platforms][eq]': 11}

    fields = ['id', 'name', 'platforms', 'time_to_beat',
              'rating', 'rating_count',
              'aggregated_rating', 'aggregated_rating_count']

    games = get_all_games(db, filters, fields)

    write_to_csv('all_xbox_games.csv', games, fields, 'name')


if __name__ == '__main__':

    logger.setLevel(logging.INFO)

    main()
