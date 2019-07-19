# native packages
from argparse import ArgumentParser, HelpFormatter
import logging
import sys

# custom packages
import scripts.constants as constants
from scripts.manager import add_note, remove_note, compile_note, open_note, list_note


# Making between each option to have a newline for easier reading
# https://stackoverflow.com/q/29484443
class BlankLinesHelpFormatter(HelpFormatter):
    def _split_lines(self, text, width):
        return super()._split_lines(text, width) + ['']


def cli(arguments):
    argument_parser = ArgumentParser(description="A simple LaTeX notes manager "
                                                 "specifically created for my workflow.",
                                     prog=constants.SHORT_NAME,
                                     formatter_class=BlankLinesHelpFormatter)

    # add the parsers for the subcommands
    subparsers = argument_parser.add_subparsers(title="subcommands", dest=constants.SUBCOMMAND_ATTRIBUTE_NAME,
                                                help="You can append a help option (-h) for each subcommand "
                                                     "to see their arguments and available options.")

    # add the subcommand 'get'
    list_note_parser = subparsers.add_parser("list", formatter_class=BlankLinesHelpFormatter,
                                             help="Get a list of notes/subjects from the database.")
    list_note_parser.add_argument("subjects", nargs="*", type=str,
                                  metavar=("SUBJECT"), default=":all:")
    list_note_parser.set_defaults(subcmd_func=list_note, subcmd_parser=list_note_parser)

    # add the subcommand 'add'
    add_note_parser = subparsers.add_parser("add", formatter_class=BlankLinesHelpFormatter,
                                            help="Add a note/subject in the appropriate location "
                                                 "at the notes directory.")
    add_note_parser.add_argument("--note", "-n", action="append", nargs="+", type=str,
                                 metavar=("SUBJECT", "TITLE"), dest=constants.NOTE_ATTRIBUTE_NAME,
                                 help="Takes a subject as the first argument "
                                      "then the title of the note(s) to be added. \n\n"
                                      "This option can also be passed multiple times in one command query.")
    add_note_parser.add_argument("--subject", "-s", action="append", nargs="*", type=str,
                                 metavar=("SUBJECT"),
                                 dest=constants.SUBJECT_ATTRIBUTE_NAME,
                                 help="Takes a list of subjects to be added into the notes directory.")
    add_note_parser.add_argument("--force", action="store_true", help="Force to write the file if the note exists.")
    add_note_parser.add_argument("--strict", action="store_true", help="Set the program to abort execution once it "
                                                                       "encounters an error.")
    add_note_parser.set_defaults(subcmd_func=add_note, subcmd_parser=add_note_parser)

    # add the subcommand 'remove'
    remove_note_parser = subparsers.add_parser("remove", aliases=["rm"],
                                               formatter_class=BlankLinesHelpFormatter,
                                               help="Remove a note from the appropriate "
                                                    "location at the notes directory.")
    remove_note_parser.add_argument("--note", "-n", action="append", nargs="+", type=str,
                                    metavar=("SUBJECT", "TITLE"), dest=constants.NOTE_ATTRIBUTE_NAME,
                                    help="Takes a subject as the first argument and the title of the note(s) "
                                         "to be deleted as the rest. You can delete all of the notes on a "
                                         "subject by providing one of the argument as ':all:'. "
                                         "This option can also be passed multiple times in one command query.")
    remove_note_parser.set_defaults(subcmd_func=remove_note, subcmd_parser=remove_note_parser)

    # add the subcommand 'compile'
    compile_note_parser = subparsers.add_parser("compile", aliases=["make"], formatter_class=BlankLinesHelpFormatter,
                                                help="Compile specified notes from a subject or a variety of them.")
    compile_note_parser.add_argument("--note", "-n", action="append", nargs="+", type=str,
                                     metavar=("SUBJECT", "TITLE"), dest=constants.NOTE_ATTRIBUTE_NAME,
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
                                  metavar=("SUBJECT", "TITLE"), dest=constants.NOTE_ATTRIBUTE_NAME,
                                  help="Takes a subject and a title of the note(s) to be opened with "
                                       "the default/configured editor.")
    open_note_parser.set_defaults(subcmd_func=open_note, subcmd_parser=open_note_parser)

    args = vars(argument_parser.parse_args())

    passed_subcommand = args.pop(constants.SUBCOMMAND_ATTRIBUTE_NAME, None)
    if passed_subcommand is None or len(arguments) == 1:
        argument_parser.print_help()
        sys.exit(0)

    if passed_subcommand is not None:
        note_function = args.pop("subcmd_func", None)

        passed_subcommand_parser = args.pop("subcmd_parser", None)

        # Printing the help message if there's no value added
        if len(arguments) == 2:
            passed_subcommand_parser.print_help()
            sys.exit(0)

        # setting up the logger for the file
        log = logging.getLogger(__name__)

        # setting up config for stream and file loggers
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.WARNING)

        file_handler = logging.FileHandler()
        file_handler.setLevel(logging.DEBUG)

        # adding the handlers to the root logger
        log.addHandler(stream_handler)
        log.addHandler(file_handler)

        note_function(**args)
