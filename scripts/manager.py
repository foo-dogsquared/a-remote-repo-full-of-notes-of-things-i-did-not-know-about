# native packages
from datetime import date
import logging
from os import chdir, getcwd
from os.path import relpath, islink
from shutil import copy, copytree, rmtree
from platform import system
import sqlite3
from subprocess import run, PIPE

# custom packages
import scripts.constants as constants
from .helper import kebab_case, sys_error_print, init_db

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
    """
    Simply creates a symbolic link through the shell. Cross-platform support is down to a minimum
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

    if target.exists() is True and target.is_dir() is True:
        return False

    if os_platform == "Windows":
        symbolic_link_creation_process = run(["mklink", "/D", link, target])
    elif os_platform == "Linux":
        symbolic_link_creation_process = run(["ln", "--symbolic", link, target])
    else:
        symbolic_link_creation_process = run(["ln", "--symbolic", link, target])

    return symbolic_link_creation_process


def get_subject(subject, strict=False):
    """
    Get a subject if it exists in the database and automatically handles the case if
    the directory is deleted while the subject is found in the database.

    :param subject: The subject to be searched.
    :type subject: str

    :param strict: Makes the program exit on first encounter of error.
    :type strict: bool

    :return: A dictionary of the subject query from the SQLite database along with an instance of Path of their
             filepath.
    :rtype: dict
    """
    with init_db() as notes_db:
        subject = subject.strip()
        subject_slug = kebab_case(subject)

        notes_db.execute("SELECT id, name, slug FROM subjects WHERE name == :name AND "
                         "slug == :slug;",
                         {"name": subject, "slug": subject_slug})

        subject_query = notes_db.fetchone()
        if subject_query is None:
            sys_error_print("NO_SUBJECT_FOUND",
                            f"Subject \"{subject}\" is not found in the database.", strict=strict)
            return None

        subject_path = constants.NOTES_DIRECTORY / subject_slug
        if subject_path.is_dir() is False:
            notes_db.execute("DELETE FROM subjects WHERE name == :name AND "
                             "slug == :slug",
                             {"name": subject, "slug": subject_slug})
            return None

        stylesheets_symbolic_link = subject_path / "stylesheets/"
        if stylesheets_symbolic_link.is_dir() is False:
            create_symbolic_link(constants.STYLE_DIRECTORY, subject_path)

        subject_value = dict(subject_query)
        subject_value["path"] = subject_path
        return subject_value


def get_all_subjects(sort_by=None):
    """
    Retrieve all of the subjects from the notes database.

    :param sort_by: Lists note in a particular order. Only accepts a limited range of keywords. Such keywords
                    include "id" and "name". Any invalid choices are not sorted in any way.
    :type sort_by: str

    :return: A list of dictionaries similar of structure from "get_subject" function.
    :rtype: list[dict]
    """
    with init_db() as notes_db:
        select_all_notes_sql_statement = "SELECT id, name, slug FROM subjects "

        if sort_by == "id":
            select_all_notes_sql_statement += "ORDER BY id"
        elif sort_by == "name":
            select_all_notes_sql_statement += "ORDER BY name"

        notes_db.execute(select_all_notes_sql_statement)

        subjects_query = notes_db.fetchall()
        for (index, _subject) in enumerate(subjects_query):
            subject_slug = kebab_case(_subject["name"])
            subject_directory_path = constants.NOTES_DIRECTORY / subject_slug

            if subject_directory_path.is_dir() is False:
                notes_db.execute("DELETE FROM subjects WHERE id == :subject_id;",
                                 {"subject_id": _subject["subject_id"]})
                logging.info(f"Subject \"{_subject['name']}\" has no directory in the binder. Database "
                             f"entry of it has been deleted.")
                del subjects_query[index]
                continue

            subject = dict(_subject)
            subject["path"] = subject_directory_path
            subjects_query[index] = subject

        return subjects_query


def get_subject_note(subject, note, strict=False):
    """
    Simply finds the note from the given subject.
    :param subject: The subject from where the note to be retrieved.
    :type subject: str

    :param note: The title of the note to be searched.
    :type note: str

    :param strict: If the value is true, the program will abort at the first encounter of error.
    :type strict: bool

    :return: A dictionary of the subject note as retrieved from the SQLite database along with the path
              assigned in the key "path".
    :rtype: dict
    """
    subject_query = get_subject(subject, strict=strict)
    if subject_query is None:
        return None

    with init_db() as notes_db:
        note_title_slug = kebab_case(note)

        note_query_arguments = {"subject_id": subject_query["id"], "title": note, "slug": note_title_slug}

        notes_db.execute("SELECT id, subject_id, title, slug FROM notes WHERE subject_id == :subject_id AND "
                         "title == :title AND slug == :slug;", note_query_arguments)
        note_query = notes_db.fetchone()

        if note_query is None:
            return None

        note_filepath = subject_query["path"] / (note_title_slug + ".tex")
        if note_filepath.is_file() is False:
            notes_db.execute("DELETE FROM notes WHERE id == :note_id;", {"note_id": note_query["id"]})
            return None

        note = dict(note_query)
        note["path"] = note_filepath
        return note


def get_all_subject_notes(subject, sort_by=None):
    """
    Retrieve all notes under the given subject.

    :param subject: The subject to be retrieve all of the notes.
    :type subject: str

    :param sort_by: The column to be based how the results should be ordered. Choices include
                    "title", "id", and "date". Any invalid choices are not sorted in any way.
    :type sort_by: str

    :return: A list of dictionaries.
    :rtype: list[dict]
    """
    subject_query = get_subject(subject)

    if subject_query is None:
        return None

    with init_db() as notes_db:
        sql_statement = "SELECT title, subject_id, id, slug, datetime_modified FROM notes " \
                        "WHERE subject_id == :subject_id "

        if sort_by == "id":
            sql_statement += "ORDER BY id"
        elif sort_by == "title":
            sql_statement += "ORDER BY title"
        elif sort_by == "date":
            sql_statement += "ORDER BY datetime_modified"

        notes_db.execute(sql_statement, {"subject_id": subject_query["id"]})

        notes_query = notes_db.fetchall()

        for (index, _note) in enumerate(notes_query):
            note_filepath = subject_query["path"] / (_note["slug"] + ".tex")

            if note_filepath.is_file() is False:
                notes_db.execute("DELETE FROM notes WHERE id == :note_id;", {"note_id": _note["note_id"]})
                logging.error(f"Subject note \"{_note['title']}\" didn't exist in the filesystem. Deleting the "
                              f"entry in the database.")
                del notes_query[index]
                continue

            note = dict(_note)
            note["path"] = note_filepath
            notes_query[index] = note

        return notes_query


def create_subject(subject):
    """
    Formally adds the given subject into the binder. It will be added into the database and automate
    the creation of the template needed for the subject.

    :param subject: The subject to be added.
    :type subject: str

    :return: An integer of 0 for the success and non-zero number in case of failure.
    :rtype: int
    """
    with init_db() as notes_db:
        subject = subject.strip()
        subject_slug = kebab_case(subject)
        logging.info(f"Creating for the subject '{subject}' into the binder.")
        try:
            notes_db.execute("INSERT INTO subjects (name, slug) VALUES (:name, :slug);",
                             {"name": subject, "slug": subject_slug})
        except sqlite3.Error as error:
            logging.error(error)

        subject_folder_path = constants.NOTES_DIRECTORY / subject_slug

        # creating the folder for the subject
        subject_folder_path.mkdir(exist_ok=True)

        # creating the `graphics/` folder in the subject directory
        subject_graphics_folder_path = subject_folder_path / "graphics/"
        subject_graphics_folder_path.mkdir(exist_ok=True)

        # creating the symbolic link for the stylesheet directory which should only
        # be two levels up in the root directory
        symbolic_link_creation_process = create_symbolic_link(constants.STYLE_DIRECTORY, subject_folder_path)

        if symbolic_link_creation_process is False:
            return 1
        elif symbolic_link_creation_process.returncode is not 0:
            rmtree(subject_folder_path)
            sys_error_print("OS_PLATFORM_UNSUPPORTED")
            return 1

        return 0


def create_subject_note(subject, *notes, **kwargs):
    """
    Formally adding all of the notes under the specified subject.

    :param subject: The subject where the note will be added.
    :type subject: str

    :param notes: The title of the note(s) to be added.
    :type notes: list[str]

    :param kwargs: Keyword arguments for extra options.

    :return: An integer of 0 for success and non-zero for failure.
    :rtype: int
    """
    subject_query = get_subject(subject)

    if subject_query is None:
        return 1

    if len(notes) == 0:
        print(f"There's no notes under {subject} to be created. Moving on.")
        return 0

    print(f"\nCreating notes under subject \"{subject}\":")

    force = kwargs.pop("force", False)
    subject_folder_path = subject_query["path"]

    with init_db() as notes_db:
        for note_title in notes:
            note_title_slug = kebab_case(note_title)
            logging.info(f"Inserting note with title '{note_title}' under subject '{subject}'.")
            try:
                notes_db.execute("INSERT INTO notes (title, slug, subject_id, datetime_modified) VALUES "
                                 "(:title, :slug, (SELECT id FROM subjects WHERE name == :subject), "
                                 "DATETIME());",
                                 {"title": note_title, "slug": note_title_slug, "subject": subject})
            except sqlite3.IntegrityError as error:
                error_msg = f"There's already a note titled '{note_title}' under the subject '{subject}'."
                print(error_msg)
                logging.error(error_msg)
                continue
            except sqlite3.Error as error:
                logging.error(error)
                continue

            note_title_filepath = subject_folder_path / (note_title_slug + ".tex")

            if note_title_filepath.is_file() is False or force is True:
                note_title_filepath.touch(exist_ok=True)

                logging.info(rf"Creating the file for the note '{note_title}'.")
                with note_title_filepath.open(mode="w") as note_file:
                    today = date.today()
                    print(f"Writing file for the note '{note_title}'")

                    custom_config = {}
                    for config_key, config_value in constants.DEFAULT_LATEX_DOC_CONFIG.items():
                        custom_config[f"__{config_key}__"] = config_value

                    note_file.write(
                        constants.DEFAULT_LATEX_SUBFILE_TEMPLATE.safe_substitute(__date__=today.strftime("%B %d, %Y"),
                                                                                 __title__=note_title,
                                                                                 **custom_config)
                    )
            else:
                logging.info(f"Corresponding note file for the note '{note_title}' under subject "
                             f"'{subject}' already exists and no forcing option has been passed.")

    return 0


def create_subject_graphics(subject, *figures, **kwargs):
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


def remove_subject_folder(subject, delete):
    """
    Simply removes the subject from the binder.

    :param subject: The subject to be removed.
    :type subject: str

    :param delete: Specifies if the program deletes the subject folder in the filesystem as well.
    :type delete: bool

    :return: An integer of 0 for success and non-zero for failure.
    :rtype: int
    """
    subject_query = get_subject(subject)

    if subject_query is None:
        return 1

    with init_db() as notes_db:
        notes_db.execute("DELETE FROM subjects WHERE id == :subject_id;",
                         {"subject_id": subject_query["id"]})

    if delete:
        logging.info("Deleting files on disk is enabled.")
        rmtree(subject_query["path"], ignore_errors=True)

    return 0


def remove_subject_notes(subject, *notes, **kwargs):
    """
    Removes the notes from a subject in the binder.

    :param subject: The subject where the notes are located.
    :type subject: str

    :param notes: The title of the note(s) to be deleted.
    :type notes: list[str]

    :param kwargs: Keyword arguments for extra options.
    :param kwargs["delete"]: Opt

    :return:
    :rtype: int
    """
    subject_query = get_subject(subject)

    if subject_query is None:
        return None

    delete_on_disk = kwargs.pop("delete", False)
    with init_db() as notes_db:
        for note in notes:
            note_query = get_subject_note(subject, note)

            if note_query is None:
                continue

            notes_db.execute("DELETE FROM notes WHERE id == :note_id", {"note_id": note_query["id"]})

            if delete_on_disk is True:
                note_query["path"].unlink()
                print(f"LaTeX file of note \"{note}\" under subject \"{subject}\" has been deleted.")


def add_note(note_metalist=None, subject_metalist=None, force=False, strict=False, **kwargs):
    """
    It'll add a note (.tex file) on the corresponding note directory.
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
    if subject_metalist is not None:
        for subjects in subject_metalist:
            for subject in subjects:
                create_subject(subject, strict)

    if note_metalist is not None:
        for subject_note_list in note_metalist:
            subject = subject_note_list[0]
            notes = subject_note_list[1:]

            create_subject_note(subject, *notes, force=force, strict=strict)


def remove_note(note_metalist=None, subject_metalist=None, delete=False, **kwargs):
    """
    Removes a note from the notes directory.
    :param note_metalist: A multidimensional list of notes with the subject as the first item and
                          the title of the notes to be removed as the last.
    :type note_metalist: list[list]

    :param subject_metalist: A multidimensional list of subjects to be deleted.
    :type subject_metalist: list[list]

    :param delete: Delete the files on disk.
    :type delete: bool

    :return: None
    """

    if subject_metalist is not None:
        for subject_list in subject_metalist:
            for subject in subject_list:
                remove_subject_folder(subject, delete)

    if note_metalist is not None:
        for subject_note_list in note_metalist:
            subject = subject_note_list[0]
            notes = subject_note_list[1:]
            remove_subject_notes(subject, *notes, delete=delete)


# this serves as an environment for note compilation
class TempCompilingDirectory:
    def __init__(self):
        # copy every main files to be copied in the temp dir
        self.temp_dir = constants.TEMP_DIRECTORY.resolve()
        if self.temp_dir.exists() is False:
            self.temp_dir.mkdir()

        if constants.OUTPUT_DIRECTORY.exists() is False:
            constants.OUTPUT_DIRECTORY.mkdir()

        self.subject_folders = []

    def add_subject(self, subject, *notes):
        with init_db() as notes_db:
            logging.info("Adding subject \"{subject}\" into the compiling environment.".format(subject=subject))
            logging.info("Checking subject \"{subject}\" in the database.")
            notes_db.execute("SELECT id FROM subjects WHERE name == :subject;",
                             {"subject": subject})
            subject_query = notes_db.fetchone()

            if subject_query is None:
                print("Subject \"{subject}\" is not found in the database. Moving on."
                      .format(subject=subject))
                return

            subject_slug = kebab_case(subject)
            subject_folder = constants.NOTES_DIRECTORY / subject_slug

            if subject_folder.exists() is not True or subject_folder.is_file() is True:
                notes_db.execute("DELETE FROM subjects WHERE id == :subject_id;",
                                 {"subject_id": subject_query['subject_id']})
                print("Subject \"{subject}\" does exist in the database but its folder in the "
                      "binder is not found. Deleting the entry in the database.")
                return

            subject_graphics_folder = subject_folder / "graphics/"
            if subject_graphics_folder.exists() is False:
                subject_graphics_folder.mkdir()

            # creating the appropriate folder for the subject
            subject_temp_folder = self.temp_dir / subject_slug
            subject_temp_folder.mkdir(exist_ok=True)

            # copying the graphics into
            copytree(subject_graphics_folder, self.temp_dir / subject_slug / "graphics/")
            self.subject_folders.append(subject_temp_folder)
            stylesheets_dir = constants.STYLE_DIRECTORY
            if stylesheets_dir.exists() is False:
                stylesheets_dir.mkdir()

            for child in stylesheets_dir.iterdir():
                if child.is_dir():
                    continue

                if child.suffix == ".cls" or child.suffix == ".sty":
                    copy(child, subject_temp_folder)

            for note in notes:
                notes_db.execute("SELECT title, slug FROM notes WHERE subject_id == :subject_id AND "
                                 "title == :title;", {"subject_id": subject_query["subject_id"], "title": note})
                subject_note_query = notes_db.fetchone()

                if subject_note_query is None:
                    print("There's no note titled \"{title}\" under subject \"{subject}\""
                          .format(title=note, subject=subject))
                    continue

                note_filepath = subject_folder / (subject_note_query['slug'] + ".tex")

                if note_filepath.exists() is False:
                    print("Note entry with the title \"{title}\" does exists in the database "
                          "but its file is nowhere to be found in the subject folder."
                          .format(title=subject_note_query['title']))
                    continue

                copy(note_filepath, subject_temp_folder)

    def compile_notes(self, output_directory=constants.OUTPUT_DIRECTORY):
        owd = getcwd()
        for subject in self.subject_folders:
            for file in subject.iterdir():
                chdir(subject.resolve())
                if file.is_file() is True and file.suffix == ".tex":
                    latex_compilation_process = run(["latexmk",
                                                     file.name,
                                                     "--shell-escape",
                                                     "-pdf"], stdin=PIPE, capture_output=True)

                    chdir(owd)
                    note_output_filepath = output_directory / subject.stem
                    note_output_filepath.mkdir(exist_ok=True)

                    if latex_compilation_process.returncode is not 0:
                        print("Not being able to compile. Check the resulting log ({file}.log)."
                              .format(file=file.stem))
                        subject_note_log = subject / (file.stem + ".log")
                        copy(subject_note_log.__str__(), note_output_filepath.__str__())
                        continue

                    print("Successfully compiled LaTeX file {file}".format(file=file.name))
                    compiled_pdf = subject / (file.stem + ".pdf")

                    copy(compiled_pdf.__str__(), note_output_filepath.__str__())

    def close(self):
        rmtree(self.temp_dir)


def compile_note(note_metalist, **kwargs):
    temp_compile_dir = TempCompilingDirectory()
    for subject_note_list in note_metalist:
        subject = subject_note_list[0]
        notes = subject_note_list[1:]

        temp_compile_dir.add_subject(subject, *notes)

    temp_compile_dir.compile_notes()
    temp_compile_dir.close()


def list_note(subjects, **kwargs):
    """
    Simply prints out a list of notes of a subject.
    :param subjects: A list of string of subjects to be searched for.
    :type subjects: list[str]

    :return:
    """
    subjects_query = None
    sort_by = kwargs.pop("sort", None)

    if ":all:" in subjects:
        subjects_query = get_all_subjects()
    else:
        subjects_query = []
        for subject in subjects:
            subject_query = get_subject(subject)

            if subject_query is None:
                continue

            subjects_query.append(subject_query)

    if len(subjects_query) == 0:
        print("There's no subjects listed in the database.")
        return None

    for subject in subjects_query:
        subject_notes_query = get_all_subject_notes(subject["name"], sort_by)
        note_count = len(subject_notes_query)
        print(f"\nSubject \"{subject['name']}\" has {note_count} {'notes' if note_count > 1 else 'note'}.")
        for note in subject_notes_query:
            print(f"  - {note['title']}")


def open_note(note, **kwargs):
    # TODO:
    # Given with the subject, search for the corresponding folder in the 'notes' dir
    # If the subject doesn't exist, abort the program execution
    subject = note[0]
    note_title = note[1]

    note_query = get_subject_note(subject, note_title, strict=True)
    if note_query is None:
        return None

    note_absolute_filepath = note_query["path"].absolute().__str__()

    execute_cmd = kwargs.pop("execute", None)
    if execute_cmd is not None:
        note_editor_instance = run(execute_cmd.format(note=note_absolute_filepath).split())
    else:
        note_editor_instance = run([constants.DEFAULT_NOTE_EDITOR, note_absolute_filepath])

    if note_editor_instance.returncode is True:
        logging.info("Text editor has been opened.")
