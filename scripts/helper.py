# native packages
from contextlib import contextmanager
import logging
from re import compile
import sqlite3
import sys

# program constants
import scripts.constants as constants


# helper functions
def sys_error_print(error, message=None, strict=False, file=sys.stderr):
    """
    Prints an error message and exit if so desired.
    :param error: The exit code from the EXIT_CODES constant. If the error from the map is not found, it'll
                  redirect to being an error with exit code 'UNKNOWN_ERROR' instead.
    :param message: The message to be printed. If there's no message, it'll use the message found on the EXIT_CODE map.
    :param strict: A boolean parameter that'll simply make the program exit after the error message has been printed.
    :param file: The file to be written off the message. By default, it'll print in the 'stderr' stream.
    :return: None
    """
    error_message = message if message is not None else constants.EXIT_CODES.get(error,
                                                                                 constants.EXIT_CODES["UNKNOWN_ERROR"])
    logging.error(error_message)
    print("\nError: {error}\n{error_message}".format(error=error, error_message=error_message), file=file)

    if strict:
        sys.exit(constants.EXIT_CODES[error])


def kebab_case(string, separator="-"):
    """
    Simply converts the string into snake_case.
    :param string: The string to be converted.
    :param separator: The separator for the resulting list of words to be joined.
    :return: str
    """
    whitespace_characters = compile(r"\s+|-+")
    invalid_characters = compile(r"[^a-zA-Z0-9]")

    word_list = whitespace_characters.split(string)
    filtered_word_list = []

    for word in word_list[:]:
        if not word:
            continue

        stripped_word = invalid_characters.sub("", word)
        if not stripped_word:
            continue

        filtered_word = stripped_word.lower()
        filtered_word_list.append(filtered_word)

    return separator.join(filtered_word_list)


def build_prefix_array(pattern):
    """
    Returns a list of numbers (indexes) of the location where the given pattern from the text was found.
    Similar to the built-in string (`str`) function `find`), it'll return -1 when no match has found.
    :param text:
    :param pattern:
    :return: [int]
    """

    # building the prefix array
    pattern_length = len(pattern)
    prefix_array = [0] * pattern_length
    j = 0

    for i in range(1, pattern_length):
        if pattern[j] == pattern[i]:
            prefix_array[i] = j + 1
            j += 1
        else:
            j = prefix_array[j - 1]
            prefix_array[i] = j
            continue

        i += 1

    return prefix_array

def substring_search(text, pattern):
    prefix_array = build_prefix_array(pattern)

    # TODO:
    # Compare the text with pattern
    # Start by comparing the characters in the text and the pattern
    # If the character doesn't match, go back to the previous value and start the comparison
    #   in the index that the previous value pointed to
    # If it's the same, then take not of the index of the text and move to the next character

    # for index in characters:
    pass


def latex_fill_template(_doctype="SUBMAIN", **kwargs):
    """
    Returns a string filled with the LaTeX document code.
    :param _doctype: Indicates whether it needs the main or the submain template. Choices include
                    "MAIN" or "SUBMAIN".
    :param kwargs: Keywords to be used from the configured template keys from DEFAULT_LATEX_DOC_KEY_LIST.
    :return: str
    """

    _doctype = _doctype.lower()
    template_dict = {}
    for key, value in kwargs.items():
        template_dict["__" + key + "__"] = value

    latex_template = None

    if _doctype is "main":
        latex_template = constants.DEFAULT_LATEX_MAIN_FILE_TEMPLATE.safe_substitute(template_dict)
    if _doctype is "submain":
        latex_template = constants.DEFAULT_LATEX_SUBFILE_TEMPLATE.safe_substitute(template_dict)

    return latex_template


def regex_match(string, pattern):
    regex_pattern = compile(pattern)
    return regex_pattern.search(string) is not None


@contextmanager
def init_db(db_path=constants.NOTES_DB_FILEPATH):
    notes_db = sqlite3.connect(db_path)
    notes_db.row_factory = sqlite3.Row

    notes_db.create_function("REGEXP", 2, regex_match)
    notes_db.create_function("SLUG", 1, kebab_case)
    notes_db.executescript(constants.NOTES_DB_SQL_SCHEMA)
    try:
        cursor = notes_db.cursor()
        yield cursor
        cursor.close()
        notes_db.commit()
    except sqlite3.DatabaseError as error:
        notes_db.rollback()
        raise error
    finally:
        notes_db.close()
