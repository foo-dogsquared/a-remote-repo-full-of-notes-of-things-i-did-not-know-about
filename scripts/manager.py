# native packages
from datetime import date
from functools import reduce
import logging
from multiprocessing import cpu_count
from os import chdir, getcwd
from os.path import relpath
from shutil import copy, copytree, rmtree
from platform import system
from queue import Queue
import queue
import sqlite3
from string import Template
from subprocess import run, Popen, PIPE
from threading import Thread

# custom packages
import scripts.constants as constants
import scripts.exceptions as exceptions
from .helper import kebab_case, init_db, use_db, regex_match, deduplicate_list

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


def create_symbolic_link(_link, _target):
    """Simply creates a relative symbolic link through the shell. Cross-platform support is down to a minimum
    so expect some bugs to pop up often.

    :param _link: The path to be linked.
    :type _link: Path

    :param _target: The target or the destination of the symbolic link to be created.
    :type _target: Path

    :return: The results from a `subprocess.run` invocation. For more information, visit the following page
             (https://docs.python.org/3/library/subprocess.html#subprocess.run).
    """
    os_platform = system()
    symbolic_link_creation_process = None
    link = relpath(_link, _target)
    target = _target

    if os_platform == "Windows":
        symbolic_link_creation_process = run(["ln", "--symbolic", link, target.__str__()])
    elif os_platform == "Linux":
        symbolic_link_creation_process = run(["ln", "--symbolic", link, target])
    else:
        symbolic_link_creation_process = run(["ln", "--symbolic", link, target])

    return symbolic_link_creation_process


def get_subject(subject, delete_in_db=True, db=None):
    """Get a subject if it exists in the database and automatically handles the case if
    the directory is deleted while the subject is found in the database.

    :param subject: The subject to be searched.
    :type subject: str

    :param delete_in_db: Simply deletes the subject entry in database if it's found to be a dangling subject. It is
                         enabled by default.
    :type delete_in_db: bool

    :param db: The database connection to be used.
    :type db: sqlite3.Connection

    :return: A dictionary of the subject query from the SQLite database along with an instance of Path of their
             filepath.
    :rtype: dict

    :raises NoSubjectFoundError: Raised if the subject is not found in the database.
    :raises DanglingSubjectError: Raised if the subject is found in the database but not found in the filesystem.
    """
    with use_db(db) as (notes_cursor, notes_db):
        subject_slug = kebab_case(subject)

        notes_cursor.execute("SELECT id, name, datetime_modified FROM subjects WHERE name == :name;",
                             {"name": subject})

        subject_query = notes_cursor.fetchone()
        if subject_query is None:
            raise exceptions.NoSubjectFoundError(subject)

        subject_path = constants.NOTES_DIRECTORY / subject_slug

        subject_value = dict(subject_query)
        subject_value["slug"] = subject_slug
        subject_value["path"] = subject_path

        if subject_path.is_dir() is False:
            if delete_in_db is True:
                notes_cursor.execute("DELETE FROM subjects WHERE id == :subject_id;", {"subject_id": subject_query["id"]})
                notes_db.commit()
            raise exceptions.DanglingSubjectError(subject_value)

        return subject_value


def convert_subject_query_to_dictionary(subject_query):
    subject_query = dict(subject_query)
    subject_query["slug"] = kebab_case(subject_query["name"])
    subject_query["path"] = constants.NOTES_DIRECTORY / subject_query["slug"]
    return subject_query


def convert_note_query_to_dictionary(note_query, subject_query):
    note = dict(note_query)
    note["subject"] = subject_query["name"]
    note["slug"] = kebab_case(note["title"])
    note["path"] = subject_query["path"] / (note["slug"] + ".tex")
    return note


def get_subjects(*subjects, **kwargs):
    """
    Retrieves a list of subjects. Query data results are similar to the `get_subject` function.

    :param subjects: A list of subjects to be searched.
    :type subjects: list[str]

    :keyword strict: Indicates that the function will raise an exception if there are missing and dangling subjects.
                     It is disabled by default.

    :keyword delete_in_db: Deletes the subject entry in the database if it's found to be a dangling subject. It is
                           enabled by default.

    :return: A tuple that is made up of three items: a list of dictionaries similar to the data returned
             from `get_subject` function, a list of subjects that are not found, and a list of dangling subjects
             with their data similar to the first list.
    :rtype: tuple[list]

    :raises MultipleSubjectError: Raises an exception if the function is in strict mode and there's invalid and
                                 dangling subjects.
    """

    db = kwargs.pop("db", None)

    with use_db(db) as (notes_cursor, notes_db):
        # this will eventually be the list for subjects that are not found
        subjects_set = deduplicate_list(subjects)

        subject_set_valid_sql_string = "(" + ", ".join(str(f"'{subject}'") for subject in subjects_set) + ")"
        notes_cursor.execute(f"SELECT id, name, datetime_modified FROM subjects WHERE name "
                             f"IN {subject_set_valid_sql_string};")

        subjects_query = notes_cursor.fetchall()

        # getting the valid keyword arguments handling for this function
        strict = kwargs.pop("strict", False)
        delete_in_db = kwargs.pop("delete_in_db", True)

        # this list will first receive the index of the dangling notes before the note dictionaries
        dangling_subjects = []

        for (index, subject) in enumerate(subjects_query):
            subject = convert_subject_query_to_dictionary(subject)
            subjects_query[index] = subject

            # remove the subjects that are found in the set
            # the remaining subject names are the one that is not found in the database
            try:
                subject_index = subjects_set.index(subject["name"])
                subjects_set.pop(subject_index)
            except ValueError:
                continue

            if subject["path"].is_dir() is False:
                dangling_subjects.append(index)

                if delete_in_db is True:
                    notes_cursor.execute("DELETE FROM subjects WHERE id == :subject_id;", {"subject_id": subject["id"]})
                    notes_db.commit()
                continue

        dangling_subjects[:] = [subjects_query.pop(index) for index in dangling_subjects]

        if (len(subjects_set) > 0 or len(dangling_subjects) > 0) or len(subjects_query) > 0:
            if strict is True:
                raise exceptions.MultipleSubjectError(subjects_set, dangling_subjects)

        return subjects_query, subjects_set, dangling_subjects


def get_all_subjects(sort_by=None, strict=False, delete_in_db=True, db=None):
    """Retrieve all of the subjects from the notes database.

    :param sort_by: Lists note in a particular order. Only accepts a limited range of keywords. Such keywords
                    include "id", "name", and "date". Any invalid choices are not sorted in any way.
    :type sort_by: str

    :param strict: Indicates that the function will raise an exception if there are missing and/or dangling subjects.
                   It is disabled by default.
    :type strict: bool

    :param delete_in_db: If enabled, let the function handle dangling subjects simply by deleting their entry in the
                       database. It is enabled by default.
    :type delete_in_db: bool

    :param db: The database connection to be used. If none was provided, it'll use the default connection.
    :type db: sqlite3.Connection

    :return: A tuple made up of the following: a list of dictionaries similar of structure
            from "get_subject" function and a list of dangling subjects.
    :rtype: tuple[list]

    :raises DanglingSubjectError: When the function is in strict mode and there are dangling subjects
                                  found in the database.
    """
    with use_db(db) as (notes_cursor, notes_db):
        select_all_notes_sql_statement = "SELECT id, name, datetime_modified FROM subjects "

        if sort_by == "id":
            select_all_notes_sql_statement += "ORDER BY id;"
        elif sort_by == "name":
            select_all_notes_sql_statement += "ORDER BY name;"
        elif sort_by == "date":
            select_all_notes_sql_statement += "ORDER BY datetime_modified;"

        notes_cursor.execute(select_all_notes_sql_statement)

        # take note that this list will receive list indices before the metadata
        dangled_subjects = []

        subjects_query = notes_cursor.fetchall()
        for (index, _subject) in enumerate(subjects_query):
            subject = convert_subject_query_to_dictionary(_subject)
            subjects_query[index] = subject

            if subject["path"].is_dir() is False:
                dangled_subjects.append(index)

                if delete_in_db is True:
                    notes_cursor.execute("DELETE FROM subjects WHERE id == :subject_id;",
                                         {"subject_id": subject["subject_id"]})
                    notes_db.commit()
                continue

        # putting all of the dangling subjects in the array
        dangled_subjects[:] = [subjects_query.pop(index) for index in dangled_subjects]

        if len(dangled_subjects) > 0 and strict is True:
            raise exceptions.DanglingSubjectError(dangled_subjects)

        return subjects_query, dangled_subjects


def get_subject_note(subject, note, delete_in_db=True, db=None):
    """Simply finds the note from the given subject.
    :param subject: The subject from where the note to be retrieved.
    :type subject: str

    :param note: The title of the note to be searched.
    :type note: str

    :param delete_in_db: If given true, let the function delete the dangling subject entry in the database before
                         raises an exception. It is enabled by default.
    :type delete_in_db: bool

    :param db: The SQLite3 database connection to be used. If none was given, it'll create and use the default
               connection.
    :type db: sqlite3.Connection

    :return: A dictionary of the subject note as retrieved from the SQLite database along with the path
              assigned in the key "path".
    :rtype: dict

    :raises NoSubjectFoundError: When the subject is not found in the database.
    :raises DanglingSubjectError: When the subject is found in the database but not in the filesystem.
    :raises NoSubjectNoteFoundError: When the subject note is not found in the database.
    :raises DanglingSubjectNoteError: When the subject is found in the database but the corresponding file is missing.
    """
    try:
        subject_query = get_subject(subject, delete_in_db=delete_in_db, db=db)
    except (exceptions.NoSubjectFoundError, exceptions.DanglingSubjectError) as error:
        raise error

    with use_db(db) as (notes_cursor, notes_db):
        note = note.strip()

        note_query_arguments = {"subject_id": subject_query["id"], "title": note}

        notes_cursor.execute("SELECT id, subject_id, title, datetime_modified FROM notes WHERE "
                             "subject_id == :subject_id AND title == :title;", note_query_arguments)
        note_query = notes_cursor.fetchone()

        if note_query is None:
            raise exceptions.NoSubjectNoteFoundError(subject, [note])

        note_value = convert_note_query_to_dictionary(note_query, subject_query)

        if note_value["path"].is_file() is False:
            if delete_in_db:
                notes_cursor.execute("DELETE FROM notes WHERE id == :note_id;", {"note_id": note_query["id"]})
                notes_db.commit()
            raise exceptions.DanglingSubjectNoteFoundError(subject, [note_value])

        return note_value


def get_all_subject_notes(subject, sort_by=None, strict=False, delete_in_db=True, db=None):
    """Retrieve all notes under the given subject.

    :param subject: The subject to be retrieve all of the notes.
    :type subject: str

    :param sort_by: The column to be based how the results should be ordered. Choices include
                    "title", "id", and "date". Any invalid choices are not sorted in any way.
    :type sort_by: str

    :param strict: Indicates if the program should raise if there's dangling subject/notes in the database.
    :type strict: bool

    :param delete_in_db: Indicates if the function should delete dangling subject/notes entry in the database.
    :type delete_in_db: bool

    :param db: The database connection to be used. If none is given, it'll create and use the default connection.
    :type db: sqlite3.Connection

    :return: A tuple made up of two items: a list of valid subject notes and a list of dangling items.
    :rtype: tuple[list]

    :raises NoSubjectFoundError: When the given subject is not found in the database.
    :raises DanglingSubjectError: When the given subject is found to be dangling.
    :raises DanglingSubjectNotesError: When there are dangling subjects note found and the function is set to strict mode.
    """
    try:
        subject = subject.strip(" -")
        subject_query = get_subject(subject, delete_in_db=True, db=db)
    except (exceptions.NoSubjectFoundError, exceptions.DanglingSubjectError) as error:
        raise error

    with use_db(db) as (notes_cursor, notes_db):
        sql_statement = "SELECT id, title, subject_id, datetime_modified FROM notes " \
                        "WHERE subject_id == :subject_id "

        if sort_by == "id":
            sql_statement += "ORDER BY id"
        elif sort_by == "title":
            sql_statement += "ORDER BY title"
        elif sort_by == "date":
            sql_statement += "ORDER BY datetime_modified"

        # getting the subject notes
        notes_cursor.execute(sql_statement, {"subject_id": subject_query["id"]})

        notes_query = notes_cursor.fetchall()
        dangling_notes = []

        for (index, _note) in enumerate(notes_query):
            note = convert_note_query_to_dictionary(_note, subject_query)
            notes_query[index] = note

            if note["path"].is_file() is False:
                if delete_in_db:
                    notes_cursor.execute("DELETE FROM notes WHERE id == :note_id;", {"note_id": _note["note_id"]})
                    notes_db.commit()

                dangling_notes.append(index)
                continue

        dangling_notes[:] = [notes_query.pop(index) for index in dangling_notes]

        if len(dangling_notes) > 0 and strict is True:
            raise exceptions.DanglingSubjectNoteFoundError(dangling_notes)

        return notes_query, dangling_notes


def create_subject(subject, db=None):
    """Formally adds the given subject into the binder. It will be added into the database and automate
    the creation of the template needed for the subject.

    :param subject: The subject to be added.
    :type subject: str

    :param db: The database connection to be used. If no database connection given, it'll get one within the `use_db`
               function.
    :type db: sqlite3.Connection

    :return: The newly added subject data similar to the data from `get_subject` function.
    :rtype: dict

    :raises ValueError: When the given subject name is not valid.
    :raises SubjectAlreadyExistsError: When the given subject already exists in the database.
    """
    subject = subject.strip(" -")

    if subject.lower() in constants.INVALID_SUBJECT_NAMES is False:
        raise ValueError(f"Given name is one of the keywords.")
    elif regex_match(subject, constants.SUBJECT_NAME_REGEX) is False:
        raise ValueError(f"Given name contains invalid characters.")

    with use_db(db) as (notes_cursor, notes_db):
        subject_slug = kebab_case(subject)
        try:
            notes_cursor.execute("INSERT INTO subjects (name, datetime_modified) VALUES (:name, DATETIME());",
                             {"name": subject})
            notes_db.commit()
        except sqlite3.IntegrityError as error:
            raise exceptions.SubjectAlreadyExists(subject)
        except sqlite3.Error as error:
            raise error

        subject_folder_path = constants.NOTES_DIRECTORY / subject_slug

        # creating the folder for the subject
        subject_folder_path.mkdir(exist_ok=True)

        # creating the `graphics/` folder in the subject directory
        subject_graphics_folder_path = subject_folder_path / "graphics/"
        subject_graphics_folder_path.mkdir(exist_ok=True)

        # creating the symbolic link for the stylesheet directory which should only
        # be two levels up in the root directory
        stylesheets_symbolic_link_path = subject_folder_path / "stylesheets/"

        if stylesheets_symbolic_link_path.is_file():
            stylesheets_symbolic_link_path.unlink()

        symbolic_link_creation_process = create_symbolic_link(constants.STYLE_DIRECTORY, subject_folder_path)

        return get_subject(subject)


def create_subject_note(subject, note_title, force=False, db=None):
    """Create a subject note in the binder.

    :param subject: The subject where the note will belong.
    :type subject: str

    :param note_title: The title of the note.
    :type note_title: str

    :param force: Force insertion of the file, if it already exist in the filesystem. Otherwise, the already existing
                  file is going to be the file associated with the note.
    :type force: bool

    :param db: The database connection to be used. If none was provided, the default connection will be used.
    :type db: sqlite3.Connection

    :return: A data from the `get_subject_note` of the newly inserted note.
    :rtype: dict

    :raises NoSubjectFoundError: When the subject given doesn't exist in the database.
    :raises DanglingSubjectError: When the subject is found to be dangling.
    :raises SubjectNoteAlreadyExistError: When the note under the given subject already exists in the database.
    :raises ValueError: When the note given is invalid (either it is one of the keywords, invalid characters,
                        or length is not at range.
    :raises sqlite3.Error: When the SQLite3 goes something wrong.
    """
    # searching for the subject
    try:
        subject_query = get_subject(subject, delete_in_db=True, db=db)
    except (exceptions.NoSubjectFoundError, exceptions.DanglingSubjectError) as error:
        raise error

    # making sure the note doesn't exists before continuing
    try:
        note = get_subject_note(subject, note_title, delete_in_db=True, db=db)
        raise exceptions.SubjectNoteAlreadyExistError(subject, [note])
    except (exceptions.NoSubjectFoundError, exceptions.DanglingSubjectError, exceptions.NoSubjectNoteFoundError,
            exceptions.DanglingSubjectNoteFoundError) as error:
        pass
    except exceptions.SubjectNoteAlreadyExistError as error:
        raise error

    if note_title in constants.INVALID_NOTE_TITLES or len(note_title) > 256:
        raise ValueError(subject, note_title)

    note_title = note_title.strip()
    with use_db(db) as (notes_cursor, notes_db):
        try:
            notes_cursor.execute("INSERT INTO notes (title, subject_id, datetime_modified) VALUES "
                                 "(:title, (SELECT id FROM subjects WHERE name == :subject), "
                                 "DATETIME());",
                                 {"title": note_title, "subject": subject})
        except sqlite3.DatabaseError as error:
            raise error

        note_title_slug = kebab_case(note_title)
        note_title_filepath = subject_query["path"] / (note_title_slug + ".tex")

        if note_title_filepath.is_file() is False or force is True:
            note_title_filepath.touch(exist_ok=True)

            with note_title_filepath.open(mode="w") as note_file:
                today = date.today()

                custom_config = {}
                for config_key, config_value in constants.DEFAULT_LATEX_DOC_CONFIG.items():
                    custom_config[f"__{config_key}__"] = config_value

                note_file.write(
                    constants.DEFAULT_LATEX_SUBFILE_TEMPLATE.safe_substitute(__date__=today.strftime("%B %d, %Y"),
                                                                             __title__=note_title,
                                                                             **custom_config)
                )

    return get_subject_note(subject, note_title)


def create_main_note(subject, _preface=None, strict=False, location=constants.NOTES_DIRECTORY,  **kwargs):
    try:
        subject_query = get_subject(subject)
    except (exceptions.DanglingSubjectError, exceptions.NoSubjectFoundError) as error:
        raise error

    try:
        subject_notes_query = get_all_subject_notes(subject, strict=strict, delete_in_db=True)
    except exceptions.DanglingSubjectNoteFoundError as error:
        raise error

    custom_config = {}
    if _preface is not None:
        preface = f"\\chapter{{Preface}}\n{Template(_preface).safe_substitute(__subject__=subject)}\n\\newpage\n"
    else:
        preface_file = subject_query["path"] / "README.txt"
        if preface_file.is_file() is True:
            with preface_file.open(mode="r") as subject_preface_file:
                preface_text = subject_preface_file.read()
                preface = f"\\chapter{{Preface}}\n" \
                          f"{Template(preface_text).safe_substitute(__subject__=subject)}\n\\newpage\n"

    main_content = ""
    today = date.today()

    for note in subject_notes_query[0]:
        main_content += f"\\part{{{note['title']}}}\n\\inputchilddocument{{{note['slug']}}}\n\n"

    for key in constants.DEFAULT_LATEX_DOC_KEY_LIST:
        if key in constants.DEFAULT_LATEX_DOC_KEY_LIST_KEYWORDS:
            continue

        _value = constants.DEFAULT_LATEX_DOC_CONFIG.get(key, "")
        value = Template(_value).safe_substitute(__subject__=subject, __date__=today.strftime("%B %d, %Y"))
        custom_config[f"__{key}__"] = value

    for key in constants.DEFAULT_LATEX_MAIN_FILE_DOC_KEY_LIST:
        if key in constants.DEFAULT_LATEX_MAIN_FILE_DOC_KEY_LIST_KEYWORDS:
            continue

        _value = constants.DEFAULT_LATEX_MAIN_FILE_DOC_KEY_CONFIG.get(key, "")
        value = Template(_value).safe_substitute(__subject__=subject, __date__=today.strftime("%B %d, %Y"))
        custom_config[f"__{key}__"] = value

    main_note_filepath = location / constants.MAIN_SUBJECT_TEX_FILENAME
    main_note_filepath.touch(exist_ok=True)
    with main_note_filepath.open(mode="w") as main_note:
        main_note.write(
            constants.DEFAULT_LATEX_MAIN_FILE_TEMPLATE.safe_substitute(__date__=today.strftime("%B %d, %Y"),
                                                                       __title__=subject,
                                                                       __preface__=preface,
                                                                       __main__=main_content,
                                                                       **custom_config)
        )


def create_subject_graphics(subject, *figures, **kwargs):
    subject = subject.strip(" -")
    subject_query = get_subject(subject)

    if subject_query is None:
        return None

    # creating the figures
    for figure in figures:
        svg_filename = kebab_case(figure)
        svg_figure_path = subject_query["path"] / constants.FIGURES_DIRECTORY_NAME / (svg_filename + ".svg")
        svg_figure_path.touch(exist_ok=True)

        with svg_figure_path.open(mode="w") as svg_figure:
            svg_figure.write(constants.DEFAULT_SVG_TEMPLATE)


def remove_subject(subject, delete, db=None):
    """Simply removes the subject from the binder.

    :param subject: The subject to be removed.
    :type subject: str

    :param delete: Specifies if the program deletes the subject folder in the filesystem as well.
    :type delete: bool

    :param db: The database connection to be used.
    :type db: sqlite3.Connection

    :return: The data of the subject being deleted if found in the database.
    :rtype: dict

    :raises NoSubjectFoundError: When the subject doesn't exist in the database.
    """
    try:
        subject = subject.strip(" -")
        subject_query = get_subject(subject, delete_in_db=True, db=db)
    except (exceptions.NoSubjectFoundError, exceptions.DanglingSubjectError) as error:
        raise error

    with use_db(db) as (notes_cursor, notes_db):
        notes_cursor.execute("DELETE FROM subjects WHERE id == :subject_id;",
                         {"subject_id": subject_query["id"]})

    if delete:
        rmtree(subject_query["path"], ignore_errors=True)

    return subject_query


def remove_all_subjects(delete=False, db=None):
    """Simply removes all subject in the binder.

    :param delete: If given true, deletes the subject in disk.
    :type delete: bool

    :param db: The database connection to be used. If none was provided, it'll create and use the default connection.
    :type db: sqlite3.Connection

    :return: The data of the subjects being deleted.
    :rtype: int
    """
    subjects_query = get_all_subjects(db=db)

    for subject in subjects_query[0]:
        remove_subject(subject["name"], delete=delete, db=db)

    return subjects_query


def remove_subject_note(subject, note, delete_on_disk=False, db=None):
    """ Remove a single subject note in the binder.

    :param subject: The name of the subject where the note belongs.
    :type subject: str

    :param note: The title of the note to be removed.
    :type note: str

    :param delete_on_disk: If enabled, simply removes the associated file of the note from the disk.
    :type delete_on_disk: bool

    :param db: The database connection to be used. If none was provided, it'll use the default connection.
    :type db: sqlite3.Connection

    :return: The data of the removed subject note.
    :rtype: dict

    :raises NoSubjectFoundError: When the subject is not found in the database.
    :raises DanglingSubjectError: When the subject is not found in the filesystem.
    :raises NoSubjectNoteFoundError: When the subject note is not found in the database.
    :raises DanglingSubjectNoteError: When the subject is found in the database but the corresponding file is missing.
    """
    try:
        note_query = get_subject_note(subject, note, delete_in_db=True, db=db)
    except exceptions.Error as error:
        raise error

    with use_db(db) as (notes_cursor, notes_db):
        notes_cursor.execute("DELETE FROM notes WHERE id == :note_id;", {"note_id": note_query["id"]})

        if delete_on_disk is True:
            note_query["path"].unlink()

    return note_query


def remove_all_subject_notes(subject, delete_on_disk=False, db=None):
    notes_query = get_all_subject_notes(subject, delete_in_db=True, db=db)

    for note in notes_query[0]:
        remove_subject_note(subject, note["title"], delete_on_disk=delete_on_disk, db=db)

    return notes_query


def update_subject(subject, new_subject, delete_in_db=True, db=None):
    pass


def update_subject_note(subject, note_title, new_note_title, delete_in_db=True, db=None):
    pass


def print_to_console_and_log(msg, logging_level=logging.INFO):
    logging.log(level=logging_level, msg=msg)
    print(msg)


def add_note(note_metalist=None, subject_metalist=None, force=False, strict=False, **kwargs):
    """Add a subject or a note in the binder.

    :param note_metalist: A list that consists of lists with the subject as the first item and then the notes
                          as the second item and beyond.
    :type note_metalist: list[list][str]

    :param subject_metalist: A multidimensional list of subjects to be added.
    :type subject_metalist: list[list][str]

    :param force: Forces overwrite of notes that has been found to already exist. Turned off by default.
    :type force: bool

    :param strict: Exits at the first time it encounters an error (like an already existing note or a wrong type of
                   file for the specified filepath. Turned off by default.
    :type strict: bool
    :return: None
    """
    db = kwargs.get("db", None)

    if subject_metalist is not None:
        subject_set = reduce(lambda _set, subject_list: _set | set(subject_list), subject_metalist, set())

        for subject in subject_set:
            try:
                create_subject(subject, db=db)

                success_msg = f"Subject '{subject}' added in the binder."
                print_to_console_and_log(success_msg)
            except exceptions.SubjectAlreadyExists:
                print_to_console_and_log(f"Subject '{subject}' already exists.", logging.ERROR)
            except ValueError:
                print_to_console_and_log(f"Given subject name '{subject}' is invalid.", logging.ERROR)
        print()

    if note_metalist is not None:
        for subject_note_list in note_metalist:
            subject = subject_note_list[0]
            notes = subject_note_list[1:]

            print_to_console_and_log(f"Creating notes for subject '{subject}':")

            for note in notes:
                try:
                    create_subject_note(subject, note, db=db)
                    print_to_console_and_log(f"Note '{note}' under subject '{subject}' added in the binder.")
                except exceptions.NoSubjectFoundError:
                    print_to_console_and_log(f"Subject '{subject}' is not found in the binder. Moving on...",
                                             logging.ERROR)
                    break
                except exceptions.DanglingSubjectError:
                    print_to_console_and_log(f"Subject '{subject}' is in the binder but its files are missing. " \
                                             f"Deleting the subject entry in the binder.", logging.ERROR)
                    break
                except exceptions.SubjectNoteAlreadyExistError:
                    print_to_console_and_log(f"Note with the title '{note}' under subject '{subject}' "
                                             f"already exists in the binder.", logging.ERROR)
                except ValueError:
                    print_to_console_and_log(f"Note title '{note}' is invalid.", logging.ERROR)
            print()


def remove_note(note_metalist=None, subject_metalist=None, delete=False, **kwargs):
    """Removes a subject or a note from the binder.

    :param note_metalist: A multidimensional list of notes with the subject as the first item and
                          the title of the notes to be removed as the last.
    :type note_metalist: list[list]

    :param subject_metalist: A multidimensional list of subjects to be deleted.
    :type subject_metalist: list[list]

    :param delete: Delete the files on disk.
    :type delete: bool

    :return: An integer of 0 for success and non-zero for failure.
    """
    db = kwargs.get("db", None)

    if delete:
        print_to_console_and_log("Deleting associated folders/files is enabled.\n")

    if subject_metalist is not None:
        subject_set = reduce(lambda _set, subject_list: _set | set(subject_list), subject_metalist, set())

        if ":all:" in subject_set:
            remove_all_subjects(delete, db=db)
            print_to_console_and_log("All subjects (and its notes) have been removed in the binder.")
            return

        for subject in subject_set:
            try:
                remove_subject(subject, delete, db=db)
                print_to_console_and_log(f"Subject '{subject}' has been removed from the binder.")
            except exceptions.NoSubjectFoundError:
                print_to_console_and_log(f"Subject '{subject}' doesn't exist in the database.", logging.ERROR)

        print()

    if note_metalist is not None:
        for subject_note_list in note_metalist:
            subject = subject_note_list[0]
            notes = subject_note_list[1:]

            print_to_console_and_log(f"Removing notes under subject '{subject}':")

            if ":all:" in notes:
                try:
                    remove_all_subject_notes(subject, delete, db=db)
                    print_to_console_and_log(f"All notes under '{subject}' have been removed from the binder.")
                except exceptions.NoSubjectFoundError:
                    print_to_console_and_log(f"Subject '{subject}' is not found in the database. Moving on...",
                                             logging.ERROR)
                except exceptions.DanglingSubjectError:
                    print_to_console_and_log(f"Subject '{subject}' is not found in the filesystem. Moving on...",
                                             logging.ERROR)
            else:
                for note in notes:
                    try:
                        remove_subject_note(subject, note, delete_on_disk=delete, db=db)
                        print_to_console_and_log(f"Note '{note}' under subject '{subject}' has been removed from the"
                                                 f"binder.")
                    except exceptions.NoSubjectFoundError:
                        print_to_console_and_log(f"Subject '{subject}' is not found in the database. Moving on...",
                                                 logging.ERROR)
                        break
                    except exceptions.DanglingSubjectError:
                        print_to_console_and_log(f"Subject '{subject}' is not found in the filesytem. Moving on...",
                                                 logging.ERROR)
                        break
                    except exceptions.NoSubjectNoteFoundError:
                        print_to_console_and_log(f"Note with the title '{note}' under subject '{subject}' "
                                                 f"does not exist in the binder.", logging.ERROR)
                    except exceptions.DanglingSubjectNoteFoundError:
                        print_to_console_and_log(f"Note with the title '{note}' under subject '{subject}' has its"
                                                 f"file missing. Deleting it in the binder.", logging.ERROR)
            print()

    return 0


# this serves as an environment for note compilation
class TempCompilingDirectory:
    def __init__(self):
        """
        Creates a temporary compilation environment. For now in order to build the compilation environment, the
        program simply copies the needed directories to the compilation environment.

        The compilation takes place in the temporary directory (constants.TEMP_DIRECTORY) assigned by the
        user.
        """
        # copy every main files to be copied in the temp dir
        self.temp_dir = constants.TEMP_DIRECTORY.resolve()
        self.temp_dir.mkdir(exist_ok=True)

        constants.OUTPUT_DIRECTORY.mkdir(exist_ok=True)

        self.subjects = []

    def add_subject(self, subject, *notes):
        """
        Adds a subject to be noted within the compilation environment by adding it into the internal subject list and
        copy the appropriate directory into the temporary folder. It also adds an additional

        :param subject: The subject to be added. Take note that the subject data should contain the results from the
                        `get_subject()` function.
        :type subject: dict

        :param notes: A list of notes to be compiled. Take note that the notes data should come from the
                      `get_subject_notes()` (or similar function)

        :return: It's a void function.
        :rtype: None
        """
        try:
            subject = get_subject(subject, delete_in_db=True)
        except (exceptions.NoSubjectFoundError, exceptions.DanglingSubjectError) as error:
            raise error

        # creating the appropriate folder for the subject
        subject_temp_folder = self.temp_dir / subject["slug"]
        if subject_temp_folder.is_dir():
            rmtree(subject_temp_folder)
        elif subject_temp_folder.is_file():
            subject_temp_folder.unlink()

        # copying the subject folder into the temporary directory
        copytree(subject["path"], subject_temp_folder)

        notes = deduplicate_list(notes)
        try:
            notes.remove(":main:")
            main = True
        except ValueError:
            main = False

        if ":all:" in notes:
            notes_query = get_all_subject_notes(subject["name"])[0]
        else:
            notes_query = []
            for note in notes:
                notes_query.append(get_subject_note(subject["name"], note))

        if main is True:
            create_main_note(subject["name"], location=subject_temp_folder)

        subject["temp_path"] = subject_temp_folder
        subject["notes"] = notes_query
        subject["main"] = main
        self.subjects.append(subject)

    def compile_notes(self, output_directory=constants.OUTPUT_DIRECTORY):
        """
        Simply compiles the notes with the added subject notes.

        :param output_directory: The directory where the files of the notes will be sent.
        :type output_directory: Path

        :return: Has no return value
        :rtype: None
        """
        owd = getcwd()
        for subject in self.subjects:
            subject_output_directory = output_directory / subject['slug']

            print_to_console_and_log(f"Compiling notes under '{subject['name']}'. " \
                f"Output location is at {subject_output_directory.resolve()}.")

            subject_note_compile_queue = Queue()

            if subject["main"]:
                chdir(subject["temp_path"].resolve())
                latex_compilation_process = Popen(["latexmk", constants.MAIN_SUBJECT_TEX_FILENAME, "-shell-escape",
                                                   "-pdf"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
                latex_compilation_process.communicate()
                chdir(owd)
                if latex_compilation_process.returncode is not 0:
                    print_to_console_and_log(f"Main note of subject '{subject['name']}' has failed to compile.")
                else:
                    print_to_console_and_log(f"Main note of subject '{subject['name']}' has been compiled")
                    copy(subject["temp_path"] / "main.pdf", subject_output_directory)

            chdir(subject["temp_path"].resolve())

            for note in subject["notes"]:
                latex_compilation_processes = Popen(["latexmk", note["path"].name, "-shell-escape", "-pdf"],
                                                     stdin=PIPE, stdout=PIPE, stderr=PIPE)

                subject_note_compile_queue.put((latex_compilation_processes, note))

            available_threads = cpu_count()

            for _thread in range(0, available_threads):
                thread = Thread(target=self._compile, args=(subject, subject_note_compile_queue, output_directory, owd))
                thread.daemon = True
                thread.start()

            subject_note_compile_queue.join()

            print()

    def _compile(self, subject, subject_note_compile_queue, output_directory, original_working_directory):
        """
        Continuously compile notes from a subject notes task queue where it contains both the note information and the
        compile command to be executed. Once the task queue is empty, that's where it will break out.

        :param subject: The subject of the note to be compiled.
        :type subject: dict

        :param subject_note_compile_queue: The task queue.
        :type subject_note_compile_queue: Queue

        :param output_directory: The output directory where the compiled file(s) will be sent.
        :type output_directory: Path

        :param original_working_directory: The original working directory of the process. This is needed in order to
                                           copy the files correctly.
        :type original_working_directory: Path

        :return: Has no return value.
        :rtype: None
        """
        while True:
            try:
                command_metadata = subject_note_compile_queue.get()
            except queue.Empty:
                break

            latex_compilation_process = command_metadata[0]
            note = command_metadata[1]

            logging.info(f"Compilation process of note '{note['title']}' has started...")
            latex_compilation_process.communicate()

            chdir(original_working_directory)
            note_output_filepath = output_directory / subject["path"].stem
            note_output_filepath.mkdir(exist_ok=True)

            subject_note_log_filename = note['path'].stem + ".log"
            subject_note_log = subject["temp_path"] / subject_note_log_filename

            compiled_pdf_filename = note['path'].stem + ".pdf"
            compiled_pdf = subject["temp_path"] / compiled_pdf_filename

            if latex_compilation_process.returncode is not 0:
                logging.error(f"Compilation process of note '{note['title']}' has failed. No PDF has been produced.")
                print(f"Note '{note['title']}' not being able to compile. Check the resulting log for errors.")
                compiled_pdf_output = note_output_filepath / compiled_pdf_filename
                if compiled_pdf_output.exists():
                    compiled_pdf_output.unlink()

                copy(subject_note_log, note_output_filepath)
                subject_note_compile_queue.task_done()
                continue

            compile_success_msg = f"Successfully compiled note '{note['title']}' into PDF."
            logging.info(compile_success_msg)
            print(compile_success_msg)

            subject_note_output_log = note_output_filepath / subject_note_log_filename
            if subject_note_output_log.exists():
                subject_note_output_log.unlink()

            copy(compiled_pdf, note_output_filepath)
            subject_note_compile_queue.task_done()
            continue

    def close(self):
        rmtree(self.temp_dir)


def compile_note(note_metalist, cache=False, **kwargs):
    temp_compile_dir = TempCompilingDirectory()
    for subject_note_list in note_metalist:
        subject = subject_note_list[0]
        notes = subject_note_list[1:]

        temp_compile_dir.add_subject(subject, *notes)

    temp_compile_dir.compile_notes()

    if cache is False:
        temp_compile_dir.close()


def list_note(subjects, **kwargs):
    """
    Simply prints out a list of notes of a subject.
    :param subjects: A list of string of subjects to be searched for.
    :type subjects: list[str]

    :return:
    """

    if ":all:" in subjects:
        subjects_query = get_all_subjects(sort_by="name")[0]
    else:
        subjects_query = []
        for subject in subjects:
            subject_query = get_subject(subject)

            if subject_query is None:
                continue

            subjects_query.append(subject_query)

    if len(subjects_query) == 0:
        print_to_console_and_log("There's no subjects listed in the database.")
        return None

    sort_by = kwargs.get("sort", "title")
    for subject in subjects_query:
        subject_notes_query = get_all_subject_notes(subject["name"], sort_by=sort_by)[0]
        note_count = len(subject_notes_query)

        print_to_console_and_log(f"Subject \"{subject['name']}\" has "
                                 f"{note_count} {'notes' if note_count > 1 else 'note'}.")

        for note in subject_notes_query:
            logging.info(f"Subject '{subject['name']}': {note['title']}")
            print(f"  - {note['title']}")
        print()


def open_note(note, **kwargs):
    """Simply opens a single note in the default text editor.

    :param note: A tuple consist of the subject and the title of the note to be opened.
    :type note: tuple(str)

    :param kwargs: Keyword arguments for options.
    :keyword execute: A command string that serves as a replacement for opening the note, if given any. The title
                      of the note must be referred with '{note}'.

    :return: An integer of 0 for success and non-zero for failure.
    :rtype: int
    """
    subject = note[0]
    note_title = note[1]

    note_query = get_subject_note(subject, note_title, strict=True)
    if note_query is None:
        return 1

    note_absolute_filepath = note_query["path"].absolute().__str__()

    execute_cmd = kwargs.pop("execute", None)
    if execute_cmd is not None:
        note_editor_instance = run(execute_cmd.format(note=note_absolute_filepath).split())
    else:
        note_editor_instance = run([constants.DEFAULT_NOTE_EDITOR, note_absolute_filepath])

    if note_editor_instance.returncode is True:
        logging.info("Text editor has been opened.")
        return 0
