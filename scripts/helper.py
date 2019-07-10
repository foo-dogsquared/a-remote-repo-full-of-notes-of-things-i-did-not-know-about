# native packages
from datetime import date
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


def create_subject_folder(subject):
    subject_slug = kebab_case(subject)
    subject_folder_path = constants.NOTES_DIRECTORY / subject_slug
    if subject_folder_path.exists():
        sys_error_print("SUBJECT_ALREADY_EXISTS",
                        "Subject \"{subject}\" (with the resulting directory path \"{path}\") has been "
                        "already found in the notes folder.".format(subject=subject, path=subject_slug))
        return None

    # creating the folder for the subject
    try:
        subject_folder_path.mkdir()
    except FileExistsError:
        sys_error_print("MKDIR_FAILED",
                        "For some reason, the creation of the directory for subject \"{subject}\" "
                        "has failed. Please try again.".format(subject=subject))

    # creating the .main.tex file
    main_tex_file = subject_folder_path / constants.MAIN_SUBJECT_TEX_FILENAME
    main_tex_file.touch()

    with main_tex_file.open("w") as main_subject_tex_file:
        today = date.today()
        latex_string = constants.DEFAULT_LATEX_MAIN_FILE_TEMPLATE. \
            safe_substitute(__author__=constants.DEFAULT_LATEX_DOC_CONFIG["author"],
                            __date__=today.strftime("%B %d, %Y"),
                            __subject__=subject)
        main_subject_tex_file.write(latex_string)

