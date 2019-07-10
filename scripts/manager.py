# native packages
from datetime import date

# custom packages
import scripts.constants as constants
from scripts.helper import create_subject_folder, kebab_case, sys_error_print

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


def add_note(note_metalist=None, subject_metalist=None, force=False, strict=False):
    """
    It'll add a note (.tex file) on the corresponding note directory.
    :param note_metalist: A list that consists of lists with the subject as the first item and then the notes
                          as the second item and beyond.
    :param subject_metalist: A multidimensional list of subjects to be added.
    :param force: Forces overwrite of notes that has been found to already exist. Turned off by default.
    :param strict: Exits at the first time it encounters an error (like an already existing note or a wrong type of
                   file for the specified filepath. Turned off by default.
    :return: None
    """

    if subject_metalist is not None:
        for subjects in subject_metalist:
            for subject in subjects:
                create_subject_folder(subject)

    if note_metalist is not None:
        for subject_note_list in note_metalist:
            subject = subject_note_list[0]
            subject_slug = kebab_case(subject)
            subject_folder_path = constants.NOTES_DIRECTORY / subject_slug

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

            subject_main_tex_file = subject_folder_path / constants.MAIN_SUBJECT_TEX_FILENAME
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
                    note_file.write(
                        constants.DEFAULT_LATEX_SUBFILE_TEMPLATE.substitute(__author__="Gabriel Arazas",
                                                                            __date__=today.strftime("%B %d, %Y"),
                                                                            __title__=note_title)
                    )

                    with subject_main_tex_file.open("r+") as main_tex_file:
                        pass


def remove_note(note_metalist):
    """
    Removes a note from the notes directory.
    :param note_metalist: A multidimensional list of notes with the subject as the first item and
                          the title of the notes to be removed as the last.
    :return: None
    """
    for subject_note_list in note_metalist:
        subject = subject_note_list[0]
        subject_slug = kebab_case(subject)
        subject_folder_path = constants.NOTES_DIRECTORY / subject_slug

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
