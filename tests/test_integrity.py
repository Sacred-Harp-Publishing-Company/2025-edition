import os
import glob
import sys

# add logging
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def current_directory():
    return os.getcwd()


def my_directory():
    return os.path.dirname(os.path.abspath(__file__))


def lyrics_directory():
    return os.path.join(my_directory(), "..", "lyrics")


def hyphenated_lyrics_directory():
    return os.path.join(my_directory(), "..", "hyphenated-lyrics")

def get_topmatter_directory():
    return os.path.join(my_directory(), "..", "topmatter")


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
        col3 = f"{parts[2]}.txt"
        files.add(col3)
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
        col3 = f"{parts[2]}.txt"
        col4 = parts[4]
        title_dict[col3] = col4
    return title_dict


def get_current_filenames(directory):
    files = set()
    for file_path in glob.glob(os.path.join(directory, "*.txt")):
        file_name = os.path.basename(file_path)
        files.add(file_name)
    return files

def test_topmatter():
    topmatter_directory = get_topmatter_directory()
    topmatter_path = os.path.join(topmatter_directory, "topmatter.tsv")
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
        if len(parts) != 11:
            strange_lines += 1
            logger.info(f"Strange line #{line_number} in topmatter.tsv: {line.strip()}")
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


if __name__ == "__main__":
    topmatter_directory = get_topmatter_directory()
    if not os.path.exists(topmatter_directory):
        logger.error(f"Top matter directory not found: {topmatter_directory}")
        sys.exit(1)
    topmatter_path = os.path.join(topmatter_directory, "topmatter.tsv")
    if not os.path.exists(topmatter_path):
        logger.error(f"topmatter.tsv not found in {topmatter_directory}")
        sys.exit(1)
    title_dict = get_2025_title_dictionary(topmatter_path)
    new_files = get_2025_filenames(topmatter_path)
    total_errors = 0
    logger.info(f"Checking topmatter integrity in {topmatter_path}...")
    total_errors += test_topmatter()
    logger.info(f"Checking {lyrics_directory()}...")
    total_errors += check(title_dict, new_files, lyrics_directory())
    logger.info(f"Checking {hyphenated_lyrics_directory()}...")
    total_errors += check(title_dict, new_files, hyphenated_lyrics_directory())
    if total_errors > 0:
        logger.error(f"Total errors found: {total_errors}")
        sys.exit(1)
    else:
        logger.info("Integrity check passed with no errors.")
        sys.exit(0)
