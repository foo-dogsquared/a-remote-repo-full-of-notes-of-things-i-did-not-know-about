from pathlib import Path
from string import Template

__all__ = ["CURRENT_DIRECTORY", "NOTES_DIRECTORY", "STYLE_DIRECTORY", "NOTE_ATTRIBUTE_NAME", "SUBJECT_ATTRIBUTE_NAME",
           "SUBCOMMAND_ATTRIBUTE_NAME", "DEFAULT_LATEX_DOC_CONFIG", "DEFAULT_LATEX_DOC_KEY_LIST",
           "DEFAULT_LATEX_MAIN_FILE_DOC_KEY_LIST", "DEFAULT_LATEX_SUBFILE_DOC_KEY_LIST", "MAIN_SUBJECT_TEX_FILENAME",
           "EXIT_CODES",

           # LaTeX raw source code
           "DEFAULT_LATEX_MAIN_FILE_SOURCE_CODE", "DEFAULT_LATEX_SUBFILE_SOURCE_CODE",

           # LaTeX source code template
           "DEFAULT_LATEX_MAIN_FILE_TEMPLATE", "DEFAULT_LATEX_SUBFILE_TEMPLATE",

           # preferences
           "DEFAULT_MANAGER_PREFERENCES", "MANAGER_PREFERENCES_FILENAME",
           ]

# common constants
CURRENT_DIRECTORY = Path("./")
NOTES_DIRECTORY = CURRENT_DIRECTORY / "notes/"
STYLE_DIRECTORY = CURRENT_DIRECTORY / "stylesheets/"
NOTE_ATTRIBUTE_NAME = "note_metalist"
SUBJECT_ATTRIBUTE_NAME = "subject_metalist"
SUBCOMMAND_ATTRIBUTE_NAME = "subcommand"

DEFAULT_LATEX_DOC_CONFIG = {
    "author": "Gabriel Arazas",
}

DEFAULT_LATEX_DOC_KEY_LIST = ["author", "date", "title"]

# TODO: Make configurable templates for main and subfiles
DEFAULT_LATEX_MAIN_FILE_DOC_KEY_LIST = []
DEFAULT_LATEX_SUBFILE_DOC_KEY_LIST = []

MAIN_SUBJECT_TEX_FILENAME = ".main.tex"

# Exit codes with their generic message
EXIT_CODES = {
    "SUCCESS": "Program execution was successful.",
    "NO_SUBJECT_FOUND": "There's no subject found within the notes directory.",
    "SUBJECT_ALREADY_EXISTS": "There's a subject already found in ",
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

# TODO: I might make use of a SQLite database someday
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
DEFAULT_LATEX_SUBFILE_SOURCE_CODE = r"""\documentclass[class=memoir, crop=false, oneside, 12pt]{standalone}

% all of the packages to be used
\usepackage[subpreambles=true]{standalone}
\usepackage{chngcntr}
\usepackage{import}
\usepackage[utf8]{inputenc}
\usepackage{fontawesome}
\usepackage[english]{babel}
\usepackage[rgb]{xcolor}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsthm}
\usepackage{tikz}
\usepackage{pgfplots}
\usepackage{fancyhdr}
\usepackage{minted}
\usepackage[most]{tcolorbox}
\usepackage[colorlinks=true, linkcolor=., urlcolor=blue]{hyperref}


% this one doesn't have a dependency and it is needed for the subfiles to
% compile consistently in various situations
% this also provides the \if macro for \rootdocument
\usepackage{docs-ifrootdocument}

\ifrootdocument
    % using the Kepler fonts set if the document is compiled as standalone
    \usepackage{kpfonts}

    % using my own packages
    \usepackage{docs-admonition-blocks}
\fi

% document metadata
\ifrootdocument
    \author{${__author__}}
    \title{${__title__}}
    \date{${__date__}}

    % change the default title page format from \maketitle
    \makeatletter
    \renewcommand*{\maketitle}{%
    \begin{titlingpage}
        \raggedleft
        \vspace{20pt}
        {\huge\bfseries\textsf{\@title}\unskip\strut\par}
        \vspace{25pt}
        {\Large\itshape\@author\unskip\strut\par}

        \vfill

        {\large \@date\par}
    \end{titlingpage}
    }

    % also define a variable for the document title since the variable for the title is erase after the \maketitle command
    \let\doctitle\@title
    \let\docauthor\@author
    \makeatother

    % using the fancy header package
    % http://linorg.usp.br/CTAN/macros/latex/contrib/fancyhdr/fancyhdr.pdf
    \pagestyle{fancy}

    % fill the header with the format
    \fancyhead[L]{\doctitle}
    \fancyhead[R]{\nouppercase{\rightmark}}

    % fill the footer with the format
    \fancyfoot[C]{\nouppercase{\leftmark}}
    \fancyfoot[R]{\thepage}

    % set the width of the horizontal bars in the header
    \renewcommand{\headrulewidth}{2pt}
    \renewcommand{\footrulewidth}{1pt}

    % set the paragraph formatting
    \setlength{\parskip}{10pt}
    \renewcommand{\baselinestretch}{1.45} 

    % set chapter style
    \chapterstyle{bianchi}

    % set chapter spacing for easier reading on digital screen
    \setlength{\beforechapskip}{-\beforechapskip}
\fi 


\begin{document}
% Frontmatter of the class note if it's compiled standalone
\ifrootdocument
    \renewcommand{\abstractname}{Summary}
    \maketitle
    \newpage

    \frontmatter
    \chapter{Preface}

    \newpage

    \tableofcontents
    \newpage

    \listoffigures
    \newpage

    \mainmatter
\fi
% Core content (HINT: always start with chapter LaTeX tag)


\end{document}
"""

DEFAULT_LATEX_MAIN_FILE_SOURCE_CODE = r"""\documentclass[class=memoir, crop=false, oneside, 12pt]{standalone}

% all of the packages to be used
\usepackage[subpreambles=true, sort=true, print=true, nocomments]{standalone}
\usepackage{chngcntr}
\usepackage{import}
\usepackage[utf8]{inputenc}
\usepackage{fontawesome}
\usepackage[english]{babel}
\usepackage[rgb]{xcolor}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsthm}
\usepackage{tikz}
\usepackage{pgfplots}
\usepackage{fancyhdr}
\usepackage{minted}
\usepackage[most]{tcolorbox}
\usepackage[colorlinks=true, linkcolor=., urlcolor=blue]{hyperref}

% using the Kepler fonts set
\usepackage{kpfonts}

% this is needed for documents to identify if the document isjjjjjj
\usepackage{docs-ifrootdocument}

% using my own packages
\usepackage{docs-title-page}
\usepackage{docs-admonition-blocks}

% document metadata
\author{${__author__}}
\title{${__subject__}}
\date{${__date__}}

% change the default title page format from \maketitle
\makeatletter
\renewcommand*{\maketitle}{%
\begin{titlingpage}
    \raggedleft
    \vspace{20pt}
    {\huge\bfseries\textsf{\@title}\unskip\strut\par}
    \vspace{25pt}
    {\Large\itshape\@author\unskip\strut\par}

    \vfill

    {\large \@date\par}
\end{titlingpage}
}

% also define a variable for the document title since the variable for the title is erase after the \maketitle command
\let\doctitle\@title
\let\docauthor\@author
\makeatother

% using the fancy header package
% http://linorg.usp.br/CTAN/macros/latex/contrib/fancyhdr/fancyhdr.pdf
\pagestyle{fancy}

% fill the header with the format
\fancyhead[L]{\doctitle}
\fancyhead[R]{\nouppercase{\rightmark}

% fill the footer with the format
\fancyfoot[C]{\nouppercase{\leftmark}}
\fancyfoot[R]{\thepage}

% set the width of the horizontal bars in the header
\renewcommand{\headrulewidth}{2pt}
\renewcommand{\footrulewidth}{1pt}

% set the paragraph formatting
\setlength{\parskip}{10pt}
\renewcommand{\baselinestretch}{1.45}

% set chapter style
\chapterstyle{bianchi}

% set chapter spacing for easier reading on digital screen
\setlength{\beforechapskip}{-\beforechapskip}


\begin{document}
% Frontmatter of the class note
\renewcommand{\abstractname}{Summary}
\maketitle
\newpage

\frontmatter
\chapter{Preface}

\newpage

\tableofcontents
\newpage

\listoffigures
\newpage

\mainmatter

% Content of the note
% __START__

\end{document}
"""

DEFAULT_LATEX_MAIN_FILE_TEMPLATE = Template(DEFAULT_LATEX_MAIN_FILE_SOURCE_CODE)
DEFAULT_LATEX_SUBFILE_TEMPLATE = Template(DEFAULT_LATEX_SUBFILE_SOURCE_CODE)

# constants for preferences
# TODO:
# use xdg-open (or x-www-browser) if it doesn't work for opening default files
# add support for common text (specifically LaTeX) editors
DEFAULT_MANAGER_PREFERENCES = {
    "latex-template": DEFAULT_LATEX_SUBFILE_SOURCE_CODE,
    "latex-builder": "latexmk",
    "latex-engine": "pdflatex",
    "latex-engine-enable-shell-escape": True,
    "latex-engine-enable-synctex": True,
}
MANAGER_PREFERENCES_FILENAME = CURRENT_DIRECTORY / "latex-note-manager.pref.json"
