# Note: This code is part of a test suite for verifying the integrity of song lyrics and metadata.
# Run with python tests/test_integrity.py (not pytest)
import os
import glob
import sys
import csv

# add logging
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def current_directory():
    return os.getcwd()


def my_directory():
    return os.path.dirname(os.path.abspath(__file__))


def lyrics_directory():
    return os.path.join(my_directory(), "..", "lyrics")


def hyphenated_lyrics_directory():
    return os.path.join(my_directory(), "..", "hyphenated-lyrics")


def get_metadata_directory():
    return os.path.join(my_directory(), "..", "metadata")


def get_first_line(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        first_line = file.readline().strip()
    return first_line


def get_2025_filenames(file_path):
    files = set()
    with open(file_path, "r") as f:
        topmatter = f.readlines()
    # skip the header
    topmatter = topmatter[1:]
    for line in topmatter:
        parts = line.strip().split("\t")
        if len(parts) < 3:
            continue
        name = f"{parts[0]}.txt"
        files.add(name)
    return files


def get_2025_title_dictionary(file_path):
    title_dict = {}
    with open(file_path, "r") as f:
        topmatter = f.readlines()
    # skip the header
    topmatter = topmatter[1:]
    for line in topmatter:
        parts = line.strip().split("\t")
        if len(parts) < 5:
            continue
        col3 = f"{parts[0]}.txt"
        col4 = parts[2]
        title_dict[col3] = col4
    return title_dict

def get_2025_page_titles(file_path):
    # read the topmatter file and return dict of page to title
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        page_title_dict = {row[1]: row[2] for i, row in enumerate(reader) if i > 0}
    return page_title_dict


def get_current_filenames(directory):
    files = set()
    for file_path in glob.glob(os.path.join(directory, "*.txt")):
        file_name = os.path.basename(file_path)
        files.add(file_name)
    return files


def test_topmatter():
    metadata_directory = get_metadata_directory()
    topmatter_path = os.path.join(metadata_directory, "topmatter.tsv")
    # make sure the file is not empty
    if os.path.getsize(topmatter_path) == 0:
        logger.error(f"topmatter.tsv is empty: {topmatter_path}")
        return 1
    # count the number of strange lines in the file
    with open(topmatter_path, "r") as f:
        topmatter = f.readlines()
    strange_lines = 0
    for line_number, line in enumerate(topmatter):
        parts = line.strip().split("\t")
        if len(parts) != 9:
            strange_lines += 1
            logger.info(
                f"Strange line #{line_number} It has {len(parts)} parts, in topmatter.tsv:, {line.strip()}"
            )
    return strange_lines


def check(title_dict, new_files, directory):
    number_of_errors = 0
    current_files = get_current_filenames(directory)
    mismatched_titles = 0
    for current_file in current_files:
        current_title = (
            get_first_line(os.path.join(directory, current_file))
            .replace("# ", "")
            .strip()
        )
        proper_title = title_dict.get(current_file, "Unknown Title")
        if current_title != proper_title:
            mismatched_titles += 1
            logger.info(
                f"Title mismatch for {current_file}: {current_title} != {proper_title}"
            )
    logger.info(f"Mismatched titles: {mismatched_titles}")
    number_of_errors += mismatched_titles
    missing_files = new_files - current_files
    if missing_files:
        logger.error(f"Missing files: {len(missing_files)}")
    else:
        logger.info("No missing files.")
    number_of_errors += len(missing_files)
    for file in missing_files:
        logger.info(f"Missing file: {file}")
    files_to_delete = current_files - new_files
    number_of_errors += len(files_to_delete)
    if not files_to_delete:
        logger.info("No files to delete.")
    else:
        logger.error(f"Files to delete: {len(files_to_delete)}")
    for file in files_to_delete:
        logger.info(f"File to delete: {file}")
    return number_of_errors


PAGES_1991 = [
    24.1,
    24.2,
    25,
    26,
    27,
    28.1,
    28.2,
    29.1,
    29.2,
    30.1,
    30.2,
    31.1,
    31.2,
    32.1,
    32.2,
    33.1,
    33.2,
    34.1,
    34.2,
    35,
    36.1,
    36.2,
    37.1,
    37.2,
    38.1,
    38.2,
    39.1,
    39.2,
    40,
    41,
    42,
    43,
    44,
    45.1,
    45.2,
    46,
    47.1,
    47.2,
    48.1,
    48.2,
    49.1,
    49.2,
    50.1,
    50.2,
    51,
    52.1,
    52.2,
    53,
    54,
    55,
    56.1,
    56.2,
    57,
    58,
    59,
    60,
    61,
    62,
    63,
    64,
    65,
    66,
    67,
    68.1,
    68.2,
    69.1,
    69.2,
    70.1,
    70.2,
    71,
    72.1,
    72.2,
    73.1,
    73.2,
    74.1,
    74.2,
    75,
    76.1,
    76.2,
    77.1,
    77.2,
    78,
    79,
    80.1,
    80.2,
    81.1,
    81.2,
    82.1,
    82.2,
    83.1,
    83.2,
    84,
    85,
    86,
    87,
    88.1,
    88.2,
    89,
    90,
    91,
    92,
    93,
    94,
    95,
    96,
    97,
    98,
    99,
    100,
    101.1,
    101.2,
    102,
    103,
    104,
    105,
    106,
    107,
    108.1,
    108.2,
    109,
    110,
    111.1,
    111.2,
    112,
    113,
    114,
    115,
    116,
    117,
    118,
    119,
    120,
    121,
    122,
    123.1,
    123.2,
    124,
    125,
    126,
    127,
    128,
    129,
    130,
    131.1,
    131.2,
    132,
    133,
    134,
    135,
    136,
    137,
    138.1,
    138.2,
    139,
    140,
    141,
    142,
    143,
    144,
    145.1,
    145.2,
    146,
    147.1,
    147.2,
    148,
    149,
    150,
    151,
    152,
    153,
    154,
    155,
    156,
    157,
    158,
    159,
    160.1,
    160.2,
    161,
    162,
    163.1,
    163.2,
    164,
    165,
    166,
    167,
    168,
    169,
    170,
    171,
    172,
    173,
    174,
    175,
    176.1,
    176.2,
    177,
    178,
    179,
    180,
    181,
    182,
    183,
    184,
    185,
    186,
    187,
    188,
    189,
    191,
    192,
    193,
    195,
    196,
    197,
    198,
    200,
    201,
    202,
    203,
    204,
    205,
    206,
    207,
    208,
    209,
    210,
    211,
    212,
    213.1,
    213.2,
    214,
    215,
    216,
    217,
    218,
    220,
    222,
    223,
    224,
    225.1,
    225.2,
    227,
    228,
    229,
    230,
    231,
    232,
    234,
    235,
    236,
    240,
    242,
    245,
    250,
    254,
    260,
    263,
    266,
    267,
    268,
    269,
    270,
    271.1,
    271.2,
    272,
    273,
    274.1,
    274.2,
    275.1,
    275.2,
    276,
    277,
    278.1,
    278.2,
    279,
    280,
    282,
    283,
    284,
    285.1,
    285.2,
    286,
    287,
    288,
    289,
    290,
    291,
    292,
    293,
    294,
    295,
    296,
    297,
    298,
    299,
    300,
    301,
    302,
    303,
    304,
    306,
    308,
    309,
    310,
    311,
    312.1,
    312.2,
    313.1,
    313.2,
    314,
    315,
    316,
    317,
    318,
    319,
    320,
    321,
    322,
    323.1,
    323.2,
    324,
    325,
    326,
    327,
    328,
    329,
    330.1,
    330.2,
    331,
    332,
    333,
    334,
    335,
    336,
    337,
    338,
    339,
    340,
    341,
    342,
    343,
    344,
    345.1,
    345.2,
    346,
    347,
    348.1,
    348.2,
    349,
    350,
    351,
    352,
    353,
    354.1,
    354.2,
    355,
    358,
    359,
    360,
    361,
    362,
    365,
    367,
    368,
    369,
    370,
    371,
    372,
    373,
    374,
    375,
    376,
    377,
    378.1,
    378.2,
    379,
    380,
    381,
    382,
    383,
    384,
    385.1,
    385.2,
    386,
    387,
    388,
    389,
    390,
    391,
    392,
    393,
    394,
    395,
    396,
    397,
    398,
    399.1,
    399.2,
    400,
    401,
    402,
    403,
    404,
    405,
    406,
    407,
    408,
    409,
    410.1,
    410.2,
    411,
    412,
    413,
    414,
    415,
    416,
    417,
    418,
    419,
    420,
    421,
    422,
    423,
    424,
    425,
    426.1,
    426.2,
    428,
    429,
    430,
    431,
    432,
    433,
    434,
    435,
    436,
    437,
    438,
    439,
    440,
    441,
    442,
    444,
    445,
    446,
    447,
    448.1,
    448.2,
    449,
    450,
    451,
    452,
    453,
    454,
    455,
    456,
    457,
    458,
    459,
    460,
    461,
    462,
    463,
    464,
    465,
    466,
    467,
    468,
    470,
    471,
    472,
    473,
    474,
    475,
    476,
    477,
    478,
    479,
    480,
    481,
    482,
    483,
    484,
    485,
    486,
    487,
    488,
    489,
    490,
    491,
    492,
    493,
    494,
    495,
    496,
    497,
    498,
    499,
    500,
    501,
    502,
    503,
    504,
    505,
    506,
    507,
    510,
    511,
    512,
    513,
    515,
    516,
    517,
    518,
    521,
    522,
    523,
    524,
    527,
    528,
    530,
    531,
    532,
    534,
    535,
    536,
    538,
    539,
    540,
    541,
    542,
    543,
    544,
    545,
    546,
    547,
    548,
    549,
    550,
    551,
    553,
    556,
    558,
    560,
    562,
    564,
    565,
    566,
    567,
    568,
    569.1,
    569.2,
    570,
    571,
    572,
    573,
]


def test_translation_table():
    errors = (
        test_translation_table_1()
        + test_translation_table_2()
        + test_translation_table_3()
        + test_translation_table_4()
    )
    return errors


def test_translation_table_1():
    logger.info("Checking translation_table.tsv for column integrity...")
    metadata_directory = get_metadata_directory()
    translation_table_path = os.path.join(metadata_directory, "translation_table.tsv")
    # make sure the file is not empty
    if os.path.getsize(translation_table_path) == 0:
        logger.error(f"translation_table.tsv is empty: {translation_table_path}")
        return 1
    # count the number of strange lines in the file
    with open(translation_table_path, "r") as f:
        translation_table = f.readlines()
    strange_lines = 0
    for line_number, line in enumerate(translation_table):
        parts = line.strip().split("\t")
        if len(parts) != 3:
            strange_lines += 1
            logger.info(
                f"Strange line #{line_number} It has {len(parts)} parts, in translation_table.tsv:, {line.strip()}"
            )
    return strange_lines


def test_translation_table_2():
    logger.info(
        "Checking that every 1991 page is accounted for in translation_table.tsv..."
    )
    errors = 0
    metadata_directory = get_metadata_directory()
    translation_table_path = os.path.join(metadata_directory, "translation_table.tsv")
    # make sure the file is not empty
    if os.path.getsize(translation_table_path) == 0:
        logger.error(f"translation_table.tsv is empty: {translation_table_path}")
        return 1
    # read the translation table
    with open(translation_table_path, "r") as f:
        translation_table = f.readlines()
    # skip the header
    translation_table = translation_table[1:]
    # create a set of pages in the translation table
    pages_in_translation_table = set()
    for line in translation_table:
        parts = line.strip().split("\t")
        if len(parts) < 2:
            continue
        page = parts[0]
        pages_in_translation_table.add(page)
    # check that every page in PAGES_1991 is in the translation table
    missing_pages = []
    for page in PAGES_1991:
        page_str = str(page)
        if page_str not in pages_in_translation_table:
            missing_pages.append(page_str)
            logger.info(f"Missing page {page_str} in translation_table.tsv")
    errors += len(missing_pages)
    # check that every page in the translation table is in PAGES_1991
    extra_pages = []
    for page in pages_in_translation_table:
        if page == "-":
            continue
        if float(page) not in PAGES_1991:
            extra_pages.append(page)
            logger.info(f"Extra page {page} in translation_table.tsv")
    errors += len(extra_pages)
    return errors


def test_translation_table_3():
    logger.info(
        "Checking that every page in translation_table.tsv has a valid action..."
    )
    errors = 0
    metadata_directory = get_metadata_directory()
    translation_table_path = os.path.join(metadata_directory, "translation_table.tsv")
    # make sure the file is not empty
    if os.path.getsize(translation_table_path) == 0:
        logger.error(f"translation_table.tsv is empty: {translation_table_path}")
        return 1
    # read the translation table
    with open(translation_table_path, "r") as f:
        translation_table = f.readlines()
    # skip the header
    translation_table = translation_table[1:]
    valid_actions = {
        "keep",
        "replace",
        "replace-inner",
        "insert",
        "renumber",
        "new",
        "remove",
    }
    for line_number, line in enumerate(translation_table):
        parts = line.strip().split("\t")
        if len(parts) < 3:
            logger.info(
                f"Strange line #{line_number} in translation_table.tsv: {line.strip()}"
            )
            errors += 1
            continue
        action = parts[2]
        if action not in valid_actions:
            logger.info(
                f"Invalid action '{action}' on line {line_number + 1} in translation_table.tsv: {line.strip()}"
            )
            errors += 1
    return errors


def test_translation_table_4():
    logger.info(
        "Checking that every page in the 2025 translation table is accounted for..."
    )
    errors = 0
    metadata_directory = get_metadata_directory()
    translation_table_path = os.path.join(metadata_directory, "translation_table.tsv")
    # make sure the file is not empty
    if os.path.getsize(translation_table_path) == 0:
        logger.error(f"translation_table.tsv is empty: {translation_table_path}")
        return 1
    # read the translation table
    with open(translation_table_path, "r") as f:
        translation_table = f.readlines()
    # skip the header
    translation_table = translation_table[1:]
    # get the file names in the lyrics directory
    current_files = get_current_filenames(lyrics_directory())
    # create a set of pages in the translation table
    pages_in_translation_table = set()
    for line in translation_table:
        parts = line.strip().split("\t")
        if len(parts) < 2:
            continue
        page = parts[1]
        if page == "-":
            continue
        pages_in_translation_table.add(page)
    # check that every page in the translation table is in the current files
    missing_pages = []
    for page in pages_in_translation_table:
        page_str = f"{page}.txt"
        if page_str not in current_files:
            missing_pages.append(page_str)
            logger.info(f"Missing file {page_str} in lyrics directory")
    errors += len(missing_pages)
    # check that every file in the current files is in the translation table
    extra_files = []
    for file in current_files:
        if file == "README.md":
            continue
        # remove the .txt extension
        file_base = file[:-4]  # remove .txt
        if file_base not in pages_in_translation_table:
            extra_files.append(file)
            logger.info(
                f"Extra file {file} in lyrics directory not in translation table"
            )
    errors += len(extra_files)
    return errors

def test_song_titles():
    metadata_directory = get_metadata_directory()
    topmatter_path = os.path.join(metadata_directory, "topmatter.tsv")
    title_pages = get_2025_page_titles(topmatter_path)
    song_title_path = os.path.join(metadata_directory, "song_titles.tsv")
    # read the csv file of song titles, ignoring the header
    with open(song_title_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        # create a dict of page to title
        song_title_pages = {row[0]: row[2] for i, row in enumerate(reader) if i > 0}
    errors = 0
    if len(song_title_pages) != len(title_pages):
        logger.error(f"song_titles.tsv has {len(song_title_pages)} entries, but topmatter.tsv has {len(title_pages)} entries")
        errors += 1
    for page in song_title_pages:
        if page not in title_pages:
            logger.info(f"Page {page} in song_titles.tsv not found in topmatter.tsv")
            errors += 1
        else:
            if song_title_pages[page] != title_pages[page]:
                logger.info(f"Title mismatch for page {page}: '{song_title_pages[page]}' != '{title_pages[page]}'")
                errors += 1
    return errors

if __name__ == "__main__":
    metadata_directory = get_metadata_directory()
    if not os.path.exists(metadata_directory):
        logger.error(f"Top matter directory not found: {metadata_directory}")
        sys.exit(1)
    topmatter_path = os.path.join(metadata_directory, "topmatter.tsv")
    if not os.path.exists(topmatter_path):
        logger.error(f"topmatter.tsv not found in {metadata_directory}")
        sys.exit(1)
    title_dict = get_2025_title_dictionary(topmatter_path)
    new_files = get_2025_filenames(topmatter_path)
    total_errors = 0
    logger.info(f"Checking topmatter integrity in {topmatter_path}...")
    total_errors += test_topmatter()
    logger.info(f"Checking {lyrics_directory()}...")
    total_errors += check(title_dict, new_files, lyrics_directory())
    # Restore if we restore the hyphenated lyrics
    # logger.info(f"Checking {hyphenated_lyrics_directory()}...")
    # total_errors += check(title_dict, new_files, hyphenated_lyrics_directory())
    logger.info(f"Checking translation table in {metadata_directory}...")
    total_errors += test_translation_table()
    logger.info(f"Checking song titles in {metadata_directory}...")
    total_errors += test_song_titles()
    if total_errors > 0:
        logger.error(f"Total errors found: {total_errors}")
        sys.exit(1)
    else:
        logger.info("Integrity check passed with no errors.")
        sys.exit(0)
