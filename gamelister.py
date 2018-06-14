#!/usr/bin/env python

# Name: gamelister.py
# Desc: Interfaces with the IGDB.com API

import json
import logging
import sys
import csv
import datetime

import pygsheets

from igdb_api_python import igdb

# API credential files
igdb_key_file = '.igdb_api_key'
gsheet_json_file = '.gsheet.service.json'

# Array of desired field names
get_fields = ['id', 'name', 'rating', 'rating_count', 'total_rating', 'total_rating_count', 'category', 'genres', 'platforms', 'first_release_date']

# Logger creation
logger = logging.getLogger(__name__)


def igdb_api_connect():
    """
    Establish a connection to the IGDB API
    :return: active IGDB API connection object
    """

    try:
        api_file = open(igdb_key_file, "r")
    except FileNotFoundError:
        sys.exit("API key file '{}' not found. Aborting.".format(igdb_key_file))

    return igdb.igdb(api_file.readline())


def open_sheet(sheet_title, sheet_name=None):
    """
    Establish a connection to the Google Sheets API
    :param sheet_title: name of the spreadsheet to open
    :param sheet_name: name of the individual sheet to open
    :return: active sheet object
    """

    sheet_api = pygsheets.authorize(service_file=gsheet_json_file)

    if sheet_name:
        google_sheet = sheet_api.open(sheet_title).worksheet_by_title(sheet_name)
    else:
        google_sheet = sheet_api.open(sheet_title).worksheet('index', '0')

    return google_sheet


def find_platform(search):
    """
    Bi-directional function to return platform ID or name from an array
    :param search: ID or name to search for
    :return: ID or name to return
    """

    # Initialize full platform ID array

    all_platforms = {
        3: 'Linux',
        4: 'Nintendo 64',
        5: 'Wii',
        6: 'PC (Microsoft Windows)',
        7: 'PlayStation',
        8: 'PlayStation 2',
        9: 'PlayStation 3',
        11: 'Xbox',
        12: 'Xbox 360',
        13: 'PC DOS',
        14: 'Mac',
        15: 'Commodore C64/128',
        16: 'Amiga',
        18: 'Nintendo Entertainment System (NES)',
        19: 'Super Nintendo Entertainment System (SNES)',
        20: 'Nintendo DS',
        21: 'Nintendo GameCube',
        22: 'Game Boy Color',
        23: 'Dreamcast',
        24: 'Game Boy Advance',
        25: 'Amstrad CPC',
        26: 'ZX Spectrum',
        27: 'MSX',
        29: 'Sega Mega Drive/Genesis',
        30: 'Sega 32X',
        32: 'Sega Saturn',
        33: 'Game Boy',
        34: 'Android',
        35: 'Sega Game Gear',
        36: 'Xbox Live Arcade',
        37: 'Nintendo 3DS',
        38: 'PlayStation Portable',
        39: 'iOS',
        41: 'Wii U',
        42: 'N-Gage',
        44: 'Tapwave Zodiac',
        45: 'PlayStation Network',
        46: 'PlayStation Vita',
        47: 'Virtual Console (Nintendo)',
        48: 'PlayStation 4',
        49: 'Xbox One',
        50: '3DO Interactive Multiplayer',
        51: 'Family Computer Disk System',
        52: 'Arcade',
        53: 'MSX2',
        55: 'Mobile',
        56: 'WiiWare',
        57: 'WonderSwan',
        58: 'Super Famicom',
        59: 'Atari 2600',
        60: 'Atari 7800',
        61: 'Atari Lynx',
        62: 'Atari Jaguar',
        63: 'Atari ST/STE',
        64: 'Sega Master System',
        65: 'Atari 8-bit',
        66: 'Atari 5200',
        67: 'Intellivision',
        68: 'ColecoVision',
        69: 'BBC Microcomputer System',
        70: 'Vectrex',
        71: 'Commodore VIC-20',
        72: 'Ouya',
        73: 'BlackBerry OS',
        74: 'Windows Phone',
        75: 'Apple II',
        77: 'Sharp X1',
        78: 'Sega CD',
        79: 'Neo Geo MVS',
        80: 'Neo Geo AES',
        82: 'Web browser',
        84: 'SG-1000',
        85: 'Donner Model 30',
        86: 'TurboGrafx-16/PC Engine',
        87: 'Virtual Boy',
        88: 'Odyssey',
        89: 'Microvision',
        90: 'Commodore PET',
        91: 'Bally Astrocade',
        92: 'SteamOS',
        93: 'Commodore 16',
        94: 'Commodore Plus/4',
        95: 'PDP-1',
        96: 'PDP-10',
        97: 'PDP-8',
        98: 'DEC GT40',
        99: 'Family Computer (FAMICOM)',
        100: 'Analogue electronics',
        101: 'Ferranti Nimrod Computer',
        102: 'EDSAC',
        103: 'PDP-7',
        104: 'HP 2100',
        105: 'HP 3000',
        106: 'SDS Sigma 7',
        107: 'Call-A-Computer time-shared mainframe computer system',
        108: 'PDP-11',
        109: 'CDC Cyber 70',
        110: 'PLATO',
        111: 'Imlac PDS-1',
        112: 'Microcomputer',
        113: 'OnLive Game System',
        114: 'Amiga CD32',
        115: 'Apple IIGS',
        116: 'Acorn Archimedes',
        117: 'Philips CD-i',
        118: 'FM Towns',
        119: 'Neo Geo Pocket',
        120: 'Neo Geo Pocket Color',
        121: 'Sharp X68000',
        122: 'Nuon',
        123: 'WonderSwan Color',
        124: 'SwanCrystal',
        125: 'PC-8801',
        126: 'TRS-80',
        127: 'Fairchild Channel F',
        128: 'PC Engine SuperGrafx',
        129: 'Texas Instruments TI-99',
        130: 'Nintendo Switch',
        131: 'Nintendo PlayStation',
        132: 'Amazon Fire TV',
        133: 'Philips Videopac G7000',
        134: 'Acorn Electron',
        135: 'Hyper Neo Geo 64',
        136: 'Neo Geo CD',
        137: 'New Nintendo 3DS',
        138: 'VC 4000',
        139: '1292 Advanced Programmable Video System',
        140: 'AY-3-8500',
        141: 'AY-3-8610',
        142: 'PC-50X Family',
        143: 'AY-3-8760',
        144: 'AY-3-8710',
        145: 'AY-3-8603',
        146: 'AY-3-8605',
        147: 'AY-3-8606',
        148: 'AY-3-8607',
        149: 'PC-98',
        150: 'Turbografx-16/PC Engine CD',
        151: 'TRS-80 Color Computer',
        152: 'FM-7',
        153: 'Dragon 32/64',
        154: 'Amstrad PCW',
        155: 'Tatung Einstein',
        156: 'Thomson MO5',
        157: 'NEC PC-6000 Series',
        158: 'Commodore CDTV',
        159: 'Nintendo DSi',
        160: 'Nintendo eShop',
        161: 'Windows Mixed Reality',
        162: 'Oculus VR',
        163: 'SteamVR',
        164: 'Daydream',
        165: 'PlayStation VR'
    }

    result_value = all_platforms.get(search)                            # Attempt to find the ID in the array (sets to None if not found)

    if not result_value:                                                # If not found, assume it is a name provided, and look for the ID

        for platform_id, platform_name in all_platforms.items():        # Iterate all platforms

            if platform_name.lower() == str(search).lower():            # Match found! Set return_value to the platform ID
                result_value = platform_id

    if not result_value:                                                # Found nothing, use 0
        result_value = 0

    return result_value


def readable_genre(genre_id):

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


def readable_time(epoch_ms):
    """
    Convert an epoch time to a clean local time
    :param epoch_ms: epoch time in milliseconds
    :return: YYYY-MM-DD HH:MM:SS in local time
    """
    epoch_ms /= 1000         # Convert to seconds
    epoch_ms += 3600 * 6     # Add 6 hours to adjust for GMT

    return datetime.datetime.fromtimestamp(int(epoch_ms)).strftime('%B %d, %Y')


def get_all_games(igdb_obj, filter_group, field_group):
    """
    Return all games from the API, iterating through via offsets.
    This is required because of the 50 response limit of the API.
    :param igdb_obj: IGDB API connection
    :param filter_group: group of filters to request by
    :param field_group: group of fields to return
    :return: list object of matching games
    """

    full_result = []
    offset = 0

    try:

        total = int(igdb_obj.games({'filters': filter_group, 'scroll': 1}).headers['X-Count'])

    except KeyError:

        total = 50

    while offset < total:

        logger.info("Pulling results {} to {} (of {})...".format(offset, offset + 49, total))
        result = igdb_obj.games({'filters': filter_group, 'fields': field_group, 'limit': 50, 'offset': offset})
        logger.debug(json.dumps(result.json(), indent=4))
        full_result += result.json()
        offset += 50

    return full_result


def get_platform_games(igdb_obj, platform_id, other_platforms_allowed):
    """
    Return an array of games for a given platform from the API
    :param igdb_obj: IGDB API connection
    :param platform_id: Platform to search for
    :param other_platforms_allowed: Allowed platforms to list
    :return: array of matched games
    """

    offset = 0
    limit = 50      # Max = 50

    all_matched_games = []

    platforms_allowed = other_platforms_allowed
    platforms_allowed.append(platform_id)

    filters = {'[platforms][eq]': platform_id}

    try:

        total = int(igdb_obj.games({'filters': filters, 'scroll': 1}).headers['X-Count'])

    except KeyError:

        total = 0

    while offset <= 10:

        logger.info("Scraping games {} - {} (of {})...".format(offset, offset + 49, total))
        platform_games = igdb_obj.games({'filters': filters, 'fields': get_fields, 'limit': limit, 'offset': offset}).json()

        for game in platform_games:

            disallowed = False

            try:
                if game['category'] == 1 or game['category'] == 3:      # Skip DLC and bundles
                    continue
            except KeyError:
                continue

            for p_id in game['platforms']:
                if p_id not in platforms_allowed:                       # Skip non-allowed platforms
                    disallowed = True

            game['platforms'].insert(0, game['platforms'].pop(game['platforms'].index(platform_id)))

            if not disallowed:
                all_matched_games.append(game)

        offset += 50

    return all_matched_games


def write_platform_sheet(worksheet, platform_games):
    """
    Initialize dimensions on a given spreadsheet
    :param worksheet: worksheet to work on
    :param platform_games: array of games to write
    :return: 0
    """

    color_black = (0.0, 0.0, 0.0, 1.0)
    color_white = (1.0, 1.0, 1.0, 1.0)

    dark_cell_border = {
        'style': 'SOLID',
        'color': {'red': 1.0, 'green': 1.0, 'blue': 1.0, 'alpha': 1.0}
    }

    light_cell_border = {
        'style': 'SOLID',
        'color': {'red': 0.0, 'green': 0.0, 'blue': 0.0, 'alpha': 1.0}
    }

    fixed_cells = {
        'B2': {'label': 'Rating',               'upper': True,  'background': color_black, 'foreground': color_white, 'border': dark_cell_border,   'border_type': 'LR'},
        'C2': {'label': 'Name',                 'upper': True,  'background': color_black, 'foreground': color_white, 'border': dark_cell_border,   'border_type': 'LR'},
        'D2': {'label': 'Genres',               'upper': True,  'background': color_black, 'foreground': color_white, 'border': dark_cell_border,   'border_type': 'LR'},
        'E2': {'label': 'Release Date',         'upper': True,  'background': color_black, 'foreground': color_white, 'border': dark_cell_border,   'border_type': 'LR'},
        'G2': {'label': 'Rating',               'upper': True,  'background': color_black, 'foreground': color_white, 'border': dark_cell_border,   'border_type': 'LR'},
        'H2': {'label': 'Name',                 'upper': True,  'background': color_black, 'foreground': color_white, 'border': dark_cell_border,   'border_type': 'LR'},
        'J2': {'label': 'Number',               'upper': True,  'background': color_black, 'foreground': color_white, 'border': dark_cell_border,   'border_type': 'LR'},
        'K2': {'label': 'Statistic',            'upper': True,  'background': color_black, 'foreground': color_white, 'border': dark_cell_border,   'border_type': 'LR'},
        'L2': {'label': 'Percent',              'upper': True,  'background': color_black, 'foreground': color_white, 'border': dark_cell_border,   'border_type': 'LR'},
        'K3': {'label': 'Average Game Rating',  'upper': False, 'background': color_white, 'foreground': color_black, 'border': light_cell_border,  'border_type': 'UDLR'},
        'K4': {'label': 'Game Ratings of 90+',  'upper': False, 'background': color_white, 'foreground': color_black, 'border': light_cell_border,  'border_type': 'UDLR'},
        'K5': {'label': 'Game Ratings of 80+',  'upper': False, 'background': color_white, 'foreground': color_black, 'border': light_cell_border,  'border_type': 'UDLR'},
        'K6': {'label': 'Game Ratings of 70+',  'upper': False, 'background': color_white, 'foreground': color_black, 'border': light_cell_border,  'border_type': 'UDLR'},
        'K7': {'label': 'Game Ratings of 40-',  'upper': False, 'background': color_white, 'foreground': color_black, 'border': light_cell_border,  'border_type': 'UDLR'},
        'K8': {'label': 'Games Rated',          'upper': False, 'background': color_white, 'foreground': color_black, 'border': light_cell_border,  'border_type': 'UDLR'},
        'K9': {'label': 'Total Games',          'upper': False, 'background': color_white, 'foreground': color_black, 'border': light_cell_border,  'border_type': 'UDLR'},
    }

    # total_platform_games = len(platform_games)

    print("Adjusting column widths...")

    worksheet.adjust_column_width(0, 0, 25)     # Left margin
    worksheet.adjust_column_width(1, 1, 75)     # Left side game rating
    worksheet.adjust_column_width(2, 2, 300)    # Left side game name
    worksheet.adjust_column_width(3, 3, 250)    # Left side game genres
    worksheet.adjust_column_width(4, 4, 135)    # Left side game release date
    worksheet.adjust_column_width(5, 5, 50)     # Separator
    worksheet.adjust_column_width(6, 6, 75)     # Middle game rating
    worksheet.adjust_column_width(7, 7, 300)    # Middle game name
    worksheet.adjust_column_width(8, 8, 50)     # Separator
    worksheet.adjust_column_width(9, 9, 75)     # Right side number
    worksheet.adjust_column_width(10, 10, 200)  # Right side statistic name
    worksheet.adjust_column_width(11, 11, 75)   # Right side percentage

    print("Writing and formatting fixed cells...")

    # Write and format fixed cells
    for xy in sorted(fixed_cells.keys()):
        print("Writing fixed cell '{}'...".format(xy))
        c = worksheet.cell(xy)
        c.color = fixed_cells[xy]['background']
        c.text_format['foregroundColor'] = {'red': 1, 'blue': 1, 'green': 1}
        c.text_format['bold'] = True
        if fixed_cells[xy]['upper']:
            c.value = fixed_cells[xy]['label'].upper()
        else:
            c.value = fixed_cells[xy]['label']

    return 0


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

            try:
                new_genre_list = []
                for genre in obj['genres']:
                    new_genre_list.append(readable_genre(genre))
                obj['genres'] = ', '.join(new_genre_list)
            except KeyError:
                logging.info("No genre for {}".format(obj['name']))

            try:
                if obj['category'] == 1 or obj['category'] == 3:
                    continue
            except KeyError:
                continue

            try:
                obj['first_release_date'] = readable_time(int(obj['first_release_date'] / 1000))
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

    sheet = open_sheet("Gamelister Test")

    write_platform_sheet(sheet, None)

    sys.exit()

    db = igdb_api_connect()

    main_platform = 'Nintendo Switch'
    other_platforms = ['PC (Microsoft Windows)', 'Wii U']

    other_platform_ids = []

    for other_platform in other_platforms:
        other_platform_ids.append(find_platform(other_platform))

    platform_games = get_platform_games(db, find_platform(main_platform), other_platform_ids)

    row = 3

    for game in platform_games:
        platforms = []
        for platform in game['platforms']:
            platforms.append(find_platform(platform))
        print("ID: {0:<06d} Game: {1:<60s} Platforms: {2:<s}".format(game['id'], game['name'], ', '.join(platforms)))
        sheet.update_cell(str("B{}").format(row), str(game['name']))
        # sheet.update_cell(str("B{}").format(row), str(game['name']))
        sheet.update_cell(str("C{}").format(row), ', '.join(platforms))
        sheet.update_cell(str("D{}").format(row), readable_time(int(game['first_release_date'])))
        row += 1

    sys.exit()


if __name__ == '__main__':

    logging.basicConfig(level=logging.CRITICAL, format='%(name)s %(message)s')

    main()
