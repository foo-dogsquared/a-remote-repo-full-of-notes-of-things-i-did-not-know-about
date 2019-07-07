# native packages
from argparse import ArgumentParser, HelpFormatter, RawTextHelpFormatter
from configparser import ConfigParser
from datetime import date
from os import path
from pathlib import Path
from re import compile
from subprocess import run
from string import Template
import sys
from textwrap import dedent
import tempfile

# common constants
CURRENT_DIRECTORY = Path("./")
NOTES_DIRECTORY = CURRENT_DIRECTORY / "notes/"
EXIT_CODES = {
    "SUCCESS": "Program execution was successful.",
    "NO_SUBJECT_FOUND": "There's no subject found within the notes directory.",
    "NO_NOTE_FOUND": "There's no note found within the notes directory.",
    "NO_LATEX_COMPILER_FOUND": "No LaTeX compiler found. If you don't have a LaTeX distribution installed on your "
                               "machine, you can install one. If you're not entirely familiar with LaTeX, I recommend "
                               "looking to this guide (https://www.ctan.org/starter) and broaden your search from "
                               "there.",
    "FILE_CONFLICT": "Certain files are detected but they are the wrong type of files (or perhaps it is a directory "
                     "instead of a file).",
    "UNKNOWN_ERROR": "An error has occurred for unknown reasons. Try to remember and replicate the steps on what "
                     "made you got this error and report it to the developer at the following GitHub repo "
                     "(https://github.com/foo-dogsquared/a-remote-repo-full-of-notes-of-things-i-do-not-know-about).",
}

SQL_SCHEMA = r"""
CREATE TABLE templates(
    template_id INTEGER,
    name TEXT UNIQUE NOT NULL,  
    template TEXT UNIQUE NOT NULL,
    description TEXT,
    PRIMARY KEY(template_id),
    CHECK(
        -- checking the name is a string less than or equal to 128 characters
        typeof(name) == "text" AND 
        length(name) <= 128 AND 
        
        typeof(template) == "text" AND 
        
        -- checking the description if it's either empty or a string less than or equal to 1024 characters
        (typeof(description) == "null" OR 
        (typeof(description) == "text" AND 
        length(description) <= 1024))
    )
)
"""

# this is just for backup in case the .default_tex_template is not found
DEFAULT_LATEX_SOURCE_CODE = r"""\documentclass[class=${__class__}, crop=false, oneside]{standalone}

% all of the packages to be used
\usepackage[subpreambles=true]{standalone}
\usepackage[colorlinks=true, linkcolor=., urlcolor=blue]{hyperref}
\usepackage{minted}
\usepackage{pgfplots}
\usepackage{amsmath}
\usepackage{tikz}
\usepackage{fancyhdr}
\usepackage[utf8]{inputenc}
\usepackage[english]{babel}
\usepackage{import}

% use Kepler fonts set
\usepackage{kpfonts}

% document metadata
\author{${__author__}}
\title{${__title__}}
\date{${__date__}}

% using the fancy header package
% http://linorg.usp.br/CTAN/macros/latex/contrib/fancyhdr/fancyhdr.pdf
\pagestyle{fancy}

% fill the header with the format
\fancyhead[L]{${__title__}}
\fancyhead[R]{\nouppercase{\rightmark}}

% fill the footer with the format
\fancyfoot[C]{\nouppercase{\leftmark}}
\fancyfoot[L]{\thepage}

% set the width of the horizontal bars in the header
\renewcommand{\headrulewidth}{2pt}
\renewcommand{\footrulewidth}{1pt}

% set the paragraph formatting
\setlength{\parskip}{10pt}
\renewcommand{\baselinestretch}{1.45}

% change the title page format from \maketitle
\makeatletter
\renewcommand*{\maketitle}{%
\begin{titlingpage}
\raggedleft
\vspace{1.5cm}
{\huge\bfseries\@title\unskip\strut\par}
\vspace{2cm}
{\Large\itshape\@author\unskip\strut\par}

\vfill

{\large \@date\par}
\end{titlingpage}
}
\makeatother

\begin{document}
% Frontmatter of the class note
\renewcommand{\abstractname}{Summary}
\maketitle
\newpage

\frontmatter
\begin{abstract}
\addcontentsline{toc}{chapter}{Summary}

\end{abstract}
\newpage

\tableofcontents
\newpage

\listoffigures
\newpage

\mainmatter

% Core content (HINT: always start with chapter LaTeX tag)

\end{document}
"""

DEFAULT_LATEX_TEMPLATE = Template(DEFAULT_LATEX_SOURCE_CODE)

# constants for preferences
# TODO:
# use xdg-open (or x-www-browser) if it doesn't work for opening default files
# add support for common text (specifically LaTeX) editors
DEFAULT_MANAGER_PREFERENCES = {
    "latex-template": DEFAULT_LATEX_SOURCE_CODE,
    "latex-builder": "latexmk",
    "latex-engine": "pdflatex",
    "latex-engine-enable-shell-escape": True,
    "latex-engine-enable-synctex": True,
}
MANAGER_PREFERENCES_FILE = CURRENT_DIRECTORY / "latex-note-manager.pref.json"


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
    error_message = message if message is not None else EXIT_CODES.get(error, EXIT_CODES["UNKNOWN_ERROR"])
    print("\nError: {error}\n{error_message}".format(error=error, error_message=error_message), file=file)

    if strict:
        sys.exit(EXIT_CODES[error])


# string functions
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

def add_subject(subject):
    # TODO:
    # With the given subject, search for the corresponding folder in 'notes' dir
    # If the subject doesn't exist, create the folder
    # Otherwise, leave with an exception
    pass


"""
All of the note functions accepts a metalist of notes with the subject as the first item in each
individual list.

[[SUBJECT_1, TITLE_1.1, TITLE_1.2, ..., TITLE_1.x], [SUBJECT_2, TITLE_2.1, TITLE_2.2, ..., TITLE_2.y], ...]

Example:
    - add_note([["Calculus", "Precalculus Review", "Introduction to Limits"], 
                ["Physics", "Introduction to Electronics"]])
    - remove_note([["Calculus", "Note that I don't need to"]])
    - compile_note([["Calculus", ":all:"], ["Physics", "A note that I need to compile right now", 
                    "Physics 2: Electric Boogaloo"]])

"""


def add_note(note_metalist, force=False, strict=False):
    """
    It'll add a note (.tex file) on the corresponding note directory.
    :param note_metalist: A list that consists of lists with the subject as the first item and then the notes
                          as the second item and beyond.
    :param force: Forces overwrite of notes that has been found to already exist. Turned off by default.
    :param strict: Exits at the first time it encounters an error (like an already existing note or a wrong type of
                   file for the specified filepath. Turned off by default.
    :return: None
    """
    for subject_note_list in note_metalist:
        subject = subject_note_list[0]
        subject_slug = kebab_case(subject)
        subject_folder_path = NOTES_DIRECTORY / subject_slug

        if subject_folder_path.exists() is not True:
            sys_error_print("NO_SUBJECT_FOUND", "No subject of name \"{subject}\" "
                                                "is in the directory.".format(subject=subject), strict)
            continue

        if subject_folder_path.exists() and subject_folder_path.is_dir() is not True:
            error = "FILE_CONFLICT"
            error_message = "Subject {subject} from the notes directory is detected to exist " \
                            "but it's not a directory. Please resolve the issue before continuing."
            sys_error_print(error, error_message, strict)

        notes = subject_note_list[1:]
        if len(notes) == 0:
            print("There's no notes under {subject} to be created. Moving on.".format(subject=subject))
            continue

        print("Creating notes under subject \"{subject}\"".format(subject=subject))

        for note_title in notes:
            note_title_slug = kebab_case(note_title)
            note_title_filepath = subject_folder_path / (note_title_slug + ".tex")

            if note_title_filepath.exists():
                print("Filename with the title \"{title}\" (at location {filepath}) "
                      "has been found.".format(title=note_title, filepath=note_title_filepath))
                if force is not True:
                    continue
            else:
                note_title_filepath.touch()

            with note_title_filepath.open(mode="r+") as note_file:
                today = date.today()
                print("Writing file for the note \"{title}\".".format(title=note_title))
                note_file.write(DEFAULT_LATEX_TEMPLATE.substitute(__class__="memoir", __author__="Gabriel Arazas",
                                                                  __date__=today.strftime("%B %d, %Y"),
                                                                  __title__=note_title))


def remove_note(note_metalist):
    """
    Removes a note from the notes directory.
    :param note_metalist: A two-dimensional list where the subject is the first item with the title of the notes can
                          vary in count.
    :return: None
    """
    for subject_note_list in note_metalist:
        subject = subject_note_list[0]
        subject_slug = kebab_case(subject)
        subject_folder_path = NOTES_DIRECTORY / subject_slug

        if subject_folder_path.exists() is False:
            sys_error_print("NO_SUBJECT_FOUND", "No subject of name \"{subject}\" "
                                                "is in the directory.".format(subject=subject))
            continue

        if subject_folder_path.exists() and subject_folder_path.is_dir() is not True:
            error = "FILE_CONFLICT"
            error_message = "Subject {subject} from the notes directory is detected to exist " \
                            "but it's not a directory. Please resolve the issue before continuing."
            sys_error_print(error, error_message)

        notes = subject_note_list[1:]
        if len(notes) == 0:
            print("There's no notes under {subject} to be removed. Moving on.".format(subject=subject))
            continue

        print("Removing notes under subject \"{subject}\"".format(subject=subject))

        for note_title in notes:
            note_title_slug = kebab_case(note_title)
            note_title_filepath = subject_folder_path / (note_title_slug + ".tex")

            if note_title_filepath.exists() is False:
                print("The note \"{title}\" ({slug}) under "
                      "subject {subject} does not exist.".format(title=note_title, subject=subject,
                                                                 slug=note_title_slug))
                continue

            if note_title_filepath.is_dir() is True:
                sys_error_print("FILE_CONFLICT")
                continue

            # if the conditions didn't meet, most likely it's a file and it's free to be removed
            print("Removing note with title \"{title}\" "
                  "({slug}) in subject {subject}.".format(title=note_title, slug=note_title_slug, subject=subject))
            note_title_filepath.unlink()


def compile_note(note_metalist):
    # TODO:
    # Given with the subject, search for the corresponding folder in the 'notes' dir
    # If the subject doesn't exist, abort the program execution
    # Otherwise, search for the .tex file with the given title
    # Then, from the config file, execute with the configured parser
    pass


def open_note(note_metalist):
    # TODO:
    # Given with the subject, search for the corresponding folder in the 'notes' dir
    # If the subject doesn't exist, abort the program execution
    pass


# Making between each option to have a newline for easier reading
# https://stackoverflow.com/q/29484443
class BlankLinesHelpFormatter(HelpFormatter):
    def _split_lines(self, text, width):
        return super()._split_lines(text, width) + ['']


def cli(arguments):
    # A bunch of constants
    NOTE_ATTRIBUTE_NAME = "note"
    SUBCOMMAND_ATTRIBUTE_NAME= "subcommand"

    argument_parser = ArgumentParser(description="A simple LaTeX notes manager "
                                                 "specifically created for my workflow.",
                                     prog="personal-lecture-manager-cli",
                                     formatter_class=BlankLinesHelpFormatter)

    # add the parsers for the subcommands
    subparsers = argument_parser.add_subparsers(title="subcommands", dest=SUBCOMMAND_ATTRIBUTE_NAME,
                                                help="You can append a help option (-h) for each subcommand "
                                                     "to see their arguments and available options.")

    # add the subcommand 'add'
    add_note_parser = subparsers.add_parser("add", formatter_class=BlankLinesHelpFormatter,
                                            help="Add a note in the appropriate location at the notes directory.")
    add_note_parser.add_argument(*("--note", "-n"), action="append", nargs="+", type=str,
                                 metavar=("SUBJECT", "TITLE"), dest=NOTE_ATTRIBUTE_NAME,
                                 help="Takes a subject as the first argument "
                                      "then the title of the note(s) to be added. \n\n"
                                      "This option can also be passed multiple times in one command query.")
    add_note_parser.add_argument("--force", action="store_true", help="Force to write the file if the note exists.")
    add_note_parser.add_argument("--strict", action="store_true", help="Set the program to abort execution once it "
                                                                       "encounters an error.")
    add_note_parser.set_defaults(subcmd_func=add_note, subcmd_parser = add_note_parser)


    # add the subcommand 'remove'
    remove_note_parser = subparsers.add_parser("remove", aliases=["rm"],
                                               formatter_class=BlankLinesHelpFormatter,
                                               help="Remove a note from the appropriate "
                                                    "location at the notes directory.")
    remove_note_parser.add_argument("--note", "-n", action="append", nargs="+", type=str,
                                    metavar=("SUBJECT", "TITLE"), dest=NOTE_ATTRIBUTE_NAME,
                                    help="Takes a subject as the first argument and the title of the note(s) "
                                         "to be deleted as the rest. You can delete all of the notes on a "
                                         "subject by providing one of the argument as ':all:'. "
                                         "This option can also be passed multiple times in one command query.")
    remove_note_parser.set_defaults(subcmd_func=remove_note, subcmd_parser = remove_note_parser)

    # add the subcommand 'compile'
    compile_note_parser = subparsers.add_parser("compile", aliases=["make"], formatter_class=BlankLinesHelpFormatter,
                                                help="Compile specified notes from a subject or a variety of them.")
    compile_note_parser.add_argument("--note", "-n", action="append", nargs="+", type=str,
                                     metavar=("SUBJECT", "TITLE"), dest=NOTE_ATTRIBUTE_NAME,
                                     help="Takes a subject as the first argument then the title of the note(s) "
                                          "to be compiled which can vary in count. "
                                          "You can compile all of the notes by providing the argument ':all:' as the "
                                          "first argument (i.e., '--note :all:'). "
                                          "You can compile all of the notes under a subject by providing ':all:' as "
                                          "the second argument (i.e., '--note <SUBJECT_NAME> :all:'). "
                                          "This option can also be passed multiple times in one command query.")
    compile_note_parser.set_defaults(subcmd_func=compile_note, subcmd_parser=compile_note_parser)

    # add the subcommand 'open'
    open_note_parser = subparsers.add_parser("open", formatter_class=BlankLinesHelpFormatter,
                                             help="Open up specified note with the default/configured text editor.")
    open_note_parser.add_argument("--note", "-n", action="append", nargs="+", type=str,
                                  metavar=("SUBJECT", "TITLE"), dest=NOTE_ATTRIBUTE_NAME,
                                  help="Takes a subject and a title of the note(s) to be opened with "
                                       "the default/configured editor.")
    open_note_parser.set_defaults(subcmd_func=open_note, subcmd_parser=open_note_parser)

    args = vars(argument_parser.parse_args())

    passed_subcommand = args.pop(SUBCOMMAND_ATTRIBUTE_NAME, None)
    if passed_subcommand is None or len(arguments) == 1:
        argument_parser.print_help()
        sys.exit(0)

    if passed_subcommand is not None:
        note_metalist = args.pop(NOTE_ATTRIBUTE_NAME, [])

        note_function = args.pop("subcmd_func", None)

        passed_subcommand_parser = args.pop("subcmd_parser", None)

        # Printing the help message if there's no value added
        if len(arguments) == 2:
            passed_subcommand_parser.print_help()
            sys.exit(0)

        note_function(note_metalist, **args)


if __name__ == "__main__":
    cli(sys.argv)
