#!/usr/bin/env python

# Name: gamelister.py
# Desc: Interfaces with the IGDB.com API

import json
import logging
import sys
import datetime

import pygsheets

from igdb_api_python import igdb

# API credential files
igdb_key_file = '.igdb_api_key'
gsheet_json_file = '.gsheet.service.json'

# Array of desired field names
get_fields = ['id', 'name', 'total_rating', 'total_rating_count', 'category', 'genres', 'platforms', 'first_release_date']

# Logger creation
logger = logging.getLogger(__name__)

genre_db = {
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

all_genres = list(genre_db.values())

platform_db = {
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

all_platforms = list(platform_db.values())

computer_platforms = ['PC (Microsoft Windows)', 'Mac', 'Linux', 'SteamOS']

xbox_platforms = ['Xbox', 'Xbox 360', 'Xbox One', 'Xbox Live Arcade']

playstation_platforms = ['PlayStation', 'PlayStation 2', 'PlayStation 3', 'PlayStation 4', 'PlayStation Portable',
                         'PlayStation Network', 'PlayStation Vita', 'PlayStation VR']

nintendo_platforms = ['Nintendo Entertainment System (NES)', 'Super Nintendo Entertainment System (SNES)',
                      'Nintendo 64', 'Nintendo GameCube', 'Wii U', 'Nintendo Switch', 'Nintendo DS', 'Nintendo 3DS',
                      'Virtual Console (Nintendo)', 'New Nintendo 3DS', 'Nintendo DSi', 'Nintendo eShop', 'Game Boy',
                      'Game Boy Advance', 'Game Boy Color']


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


def lookup(database, search):
    """
    Bi-directional function to return ID or name from an array
    :param database: which array to search
    :param search: ID or name to search for
    :return: ID or name to return
    """
    
    if database == 'platforms':
        db_obj = platform_db
    elif database == 'genres':
        db_obj = genre_db
    else:
        return 0
    
    result_value = db_obj.get(search)                            # Attempt to find the ID in the array (sets to None if not found)

    if not result_value:                                                # If not found, assume it is a name provided, and look for the ID

        for database_id, database_name in db_obj.items():        # Iterate all platforms

            if database_name.lower() == str(search).lower():            # Match found! Set return_value to the platform ID
                result_value = database_id

    if not result_value:                                                # Found nothing, use 0
        result_value = 0

    return result_value


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


def search_games(igdb_obj, options):
    """
    Return an array of games for a given platform from the API
    :param igdb_obj: IGDB API connection
    :param options: array of options to search for and filter by
    :return: array of matched games
    """

    offset = 0
    limit = 50      # Max = 50

    time_now = (datetime.datetime.now().microsecond - (3600 * 6))

    all_matched_games = []

    filters = {}

    if 'search_platforms' in options.keys():
        platform_ids = []

        for platform in options['search_platforms']:
            platform_ids.append(str(lookup('platforms', platform)))

        platform_string = ','.join(platform_ids)

        if 'search_platform_mode' in options.keys():
            if options['search_platform_mode'] == 'any':
                filters['[platforms][any]'] = platform_string
            elif options['search_platform_mode'] == 'all':
                filters['[platforms][all]'] = platform_string
            else:
                raise ValueError("Invalid platform search mode input.")
        else:
            filters['[platforms][any]'] = platform_string

    if 'search_genres' in options.keys():
        genre_ids = []

        for genre in options['search_genres']:
            genre_ids.append(str(lookup('genres', genre)))

        genre_string = ','.join(genre_ids)

        if 'search_genre_mode' in options.keys():
            if options['search_genre_mode'] == 'any':
                filters['[genres][any]'] = genre_string
            elif options['search_genre_mode'] == 'all':
                filters['[genre][all]'] = genre_string
            else:
                raise ValueError("Invalid genre search mode input.")
        else:
            filters['[genres][any]'] = genre_string

    if 'release_status' in options.keys():
        if options['release_status'] == 'RELEASED':
            filters['[first_released_date][le]']: time_now
        elif options['release_status'] == 'UNRELEASED':
            filters['[first_released_date][gt]']: time_now
        else:
            if options['release_status'] != 'ALL':
                raise ValueError("Invalid release status input. Valid statuses: RELEASED, UNRELEASED, ALL.")

    try:

        total = int(igdb_obj.games({'filters': filters, 'scroll': 1}).headers['X-Count'])

    except KeyError:

        total = 0

    while offset < (total + 1):

        logger.info("Scraping games {} - {} (of {})...".format(offset, offset + 49, total))
        matched_games = igdb_obj.games({'filters': filters, 'fields': get_fields, 'limit': limit, 'offset': offset}).json()

        if len(matched_games) == 0:
            sys.exit("No games found! Filter dump: {}".format(json.dumps(filters, indent=4)))

        for game in matched_games:

            disallowed = False

            if 'error' in game.keys() or 'name' not in game.keys():                         # Malformed or missing game
                continue

            if 'category' in game.keys():
                if game['category'] == 1 or game['category'] == 3:                          # Skip DLC and bundles
                    disallowed = True

            if game['name'].startswith('duplicate'):                                        # Skip duplicates
                    disallowed = True

            if 'allowed_platforms' in options.keys():
                for platform in game['platforms']:
                    if lookup('platforms', platform) not in options['search_platforms'] + options['allowed_platforms']:
                        disallowed = True                                                   # Skip non-allowed platforms
                        # print("disallowed for platform")

            if 'disallowed_platforms' in options.keys():
                for platform in game['platforms']:
                    if lookup('platforms', platform) in options['disallowed_platforms']:    # Skip disallowed platforms
                        disallowed = True

            if 'allowed_genres' in options.keys():
                for genre in game['genres']:
                    if lookup('genres', genre) not in options['search_genres'] + options['allowed_genres']:
                        disallowed = True                                                   # Skip non-allowed genres

            if 'disallowed_genres' in options.keys():
                for genre in game['genres']:
                    if lookup('genres', genre) in options['disallowed_genres']:          # Skip disallowed genres
                        disallowed = True

            if 'search_platforms' in options.keys():                                        # Move searched platforms to front
                for platform in sorted(platform_db):
                    if platform in options['search_platforms']:
                        game['platforms'].insert(0, game['platforms'].pop(
                            game['platforms'].index(lookup('platforms', platform))))

            if 'search_genres' in options.keys():                                        # Move searched platforms to front
                for genre in sorted(platform_db):
                    if genre in options['search_genres']:
                        game['genres'].insert(0, game['genres'].pop(
                            game['genres'].index(lookup('genres', genre))))

            if not disallowed:
                all_matched_games.append(game)

        offset += 50

    return all_matched_games


def write_game_sheet(worksheet, games, options):
    """
    Build a game matrix and write it to a worksheet
    :param worksheet: worksheet to work on
    :param games: array of games to write
    :param options: array of options to add to the sheet info
    :return: 0
    """

    # Fixed sheet data
    data_start_row = 6
    rating_column = 'B'
    first_column = 'B'
    last_column = 'F'

    if len(games) == 0:
        sys.exit("No games found.")
    else:
        print("Writing {} games to worksheet...".format(len(games)))

    if len(games) > worksheet.rows + data_start_row:
        worksheet.rows = data_start_row + len(games)

    full_border = {
        'top': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.0, 'green': 0.0, 'blue': 0.0, 'alpha': 0.0}},
        'left': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.0, 'green': 0.0, 'blue': 0.0, 'alpha': 0.0}},
        'right': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.0, 'green': 0.0, 'blue': 0.0, 'alpha': 0.0}},
        'bottom': {'style': 'SOLID', 'width': 1, 'color': {'red': 0.0, 'green': 0.0, 'blue': 0.0, 'alpha': 0.0}}
    }

    rating_start = str("{}{}".format(rating_column, data_start_row))
    rating_end = str("{}{}".format(rating_column, data_start_row + len(games)))
    rating_cell_model = pygsheets.Cell(rating_start)
    rating_cell_range = worksheet.get_values(rating_start, rating_end, returnas='range')

    rating_cell_model.format = pygsheets.FormatType.NUMBER, '0"%"'
    rating_cell_model.set_text_alignment('CENTER')
    rating_cell_model.set_text_alignment('MIDDLE')
    rating_cell_range.apply_format(rating_cell_model)

    border_cell_model = pygsheets.Cell('A1')
    border_cell_range = worksheet.get_values(
        str('{}{}'.format(first_column, data_start_row)),
        str('{}{}'.format(last_column, data_start_row + len(games))), returnas='range')
    border_cell_model.borders = full_border
    border_cell_range.apply_format(border_cell_model)

    if 'sort' not in options.keys():
        sort_mode = 'name'
    else:
        sort_mode = options['sort']

    platform_count = {}
    genre_count = {}
    game_matrix = []

    for game in sorted(games, key=lambda n: n[sort_mode]):

        if 'platforms' in game.keys():
            platform_string = []
            for platform in game['platforms']:
                platform_string.append(str(lookup('platforms', platform)))

            platforms_text = ', '.join(platform_string)

            for platform in game['platforms']:
                if platform in platform_count.keys():
                    platform_count[platform] += 1
                else:
                    platform_count[platform] = 1
        else:
            platforms_text = ''

        if 'genres' in game.keys():
            genre_string = []
            for genre in game['genres']:
                genre_string.append(str(lookup('genres',genre)))

            genres_text = ', '.join(genre_string)

            for genre in game['genres']:
                if genre in genre_count.keys():
                    genre_count[genre] += 1
                else:
                    genre_count[genre] = 1
        else:
            genres_text = ''

        if 'first_release_date' in game.keys():
            release_text = readable_time(game['first_release_date'])
        else:
            release_text = ''

        if 'total_rating' in game.keys() and 'total_rating_count' in game.keys():
            if game['total_rating_count'] > 1:
                rating_text = game['total_rating']
                print("Raw rating: {}".format(game['total_rating']))
            else:
                rating_text = ''
        else:
            rating_text = ''

        game_matrix.append([rating_text, game['name'], genres_text, platforms_text, release_text])

    cell_range = str('B{}:F{}'.format(data_start_row, data_start_row + len(games)))

    worksheet.update_cells(crange=cell_range, values=game_matrix)

    return 0


def main():
    """
    Main function to gather information from IGDB API
    :return: null
    """

    sheet = open_sheet("Gamelister Test")

    db = igdb_api_connect()

    options = {
        'search_platforms': ['Nintendo Switch', 'Wii U'],
        'search_platform_mode': 'any',
        # 'search_genres': all_genres,
        # 'search_genre_mode': 'any',
        'allowed_platforms': computer_platforms,
        'disallowed_platforms': xbox_platforms + playstation_platforms + computer_platforms,
        'release_status': 'RELEASED',
        'sort': 'name',
    }

    found_games = search_games(db, options)

    write_game_sheet(sheet, found_games, options)

    sys.exit()


if __name__ == '__main__':

    logging.basicConfig(level=logging.CRITICAL, format='%(name)s %(message)s')

    main()
