###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

import importlib.metadata
import os

import six

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:  # pragma: no cover
    # package is not installed
    __version__ = "unknown"

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _print_data_location():
    """
    Print the location of the `data` folder.
    """
    print(DATA_DIR)


def createProjectMakefile(dest, overwrite=False):
    """Write the generic Makefile for CMT projects.
    @param dest: the name of the destination file
    @param overwrite: flag to decide if an already present file has to be kept
                      or not (default is False)
    """
    import logging

    if overwrite or not os.path.exists(dest):
        logging.debug("Creating '%s'", dest)
        with open(dest, "w") as f:
            f.write(
                f"DEVTOOLS_DATADIR := {DATA_DIR}\n"
                "include $(DEVTOOLS_DATADIR)/Makefile-common.mk\n"
            )
        return True
    return False


def createToolchainFile(dest, overwrite=False):
    """Write the generic toolchain.cmake file needed by CMake-based projects.
    @param dest: destination filename
    @param overwrite: flag to decide if an already present file has to be kept
                      or not (default is False)
    """
    import logging

    if overwrite or not os.path.exists(dest):
        logging.debug("Creating '%s'", dest)
        with open(dest, "w") as f:
            f.write("include({})\n".format(os.path.join(DATA_DIR, "toolchain.cmake")))
        return True
    return False


def createGitIgnore(dest, overwrite=False, extra=None, selfignore=True):
    """Write a generic .gitignore file, useful for git repositories.
    @param dest: destination filename
    @param overwrite: flag to decide if an already present file has to be kept
                      or not (default is False)
    @param extra: list of extra patterns to add
    @param selfignore: if the .gitignore should include itself
    """
    import logging

    if overwrite or not os.path.exists(dest):
        logging.debug("Creating '%s'", dest)
        patterns = [
            "/InstallArea/",
            "/build.*/",
            "*.pyc",
            "*~",
            ".*.swp",
            "/.clang-format",
        ]
        if selfignore:
            patterns.insert(0, "/.gitignore")  # I like it as first entry
        if extra:
            patterns.extend(extra)

        with open(dest, "w") as f:
            f.write("\n".join(patterns))
            f.write("\n")
        return True
    return False


def createClangFormat(dest, overwrite=False):
    """Add `.clang-format` file.
    @param dest: destination filename
    @param overwrite: flag to decide if an already present file has to be kept
                      or not (default is False)
    """
    import logging

    if overwrite or not os.path.exists(dest):
        logging.debug("Creating '%s'", dest)
        with open(dest, "w") as f:
            f.writelines(open(os.path.join(DATA_DIR, "default.clang-format")))
        return True
    return False


def initProject(path, overwrite=False, ignore_pre_commit=False):
    """
    Initialize the sources for an LHCb project for building.

    Create the (generic) special files required for building LHCb/Gaudi
    projects.

    @param path: path to the root directory of the project
    @param overwrite: whether existing files should be overwritten, set it to
                      True to overwrite all of them or to a list of filenames
    @param ignore_pre_commit: to not call "pre-commit install" even if
                              .pre-commit-config.yaml is present
    """
    extraignore = []
    factories = [
        ("Makefile", createProjectMakefile),
        ("toolchain.cmake", createToolchainFile),
        (".clang-format", createClangFormat),
        (  # this has to be last to take into account what was added
            ".gitignore",
            lambda dest, overwrite: createGitIgnore(dest, overwrite, extraignore),
        ),
    ]

    # handle the possible values of overwrite to always have a set of names
    if overwrite in (False, None):
        overwrite = set()
    elif overwrite is True:
        overwrite = {f[0] for f in factories}
    elif isinstance(overwrite, six.string_types):
        overwrite = {overwrite}
    else:
        overwrite = set(overwrite)

    for filename, factory in factories:
        if factory(os.path.join(path, filename), overwrite=filename in overwrite):
            extraignore.append("/" + filename)

    if os.path.exists(os.path.join(path, ".pre-commit-config.yaml")):
        import logging

        if not ignore_pre_commit:
            from subprocess import run

            logging.debug(
                run(
                    ["pre-commit", "install"], cwd=path, capture_output=True
                ).stdout.decode()
            )
        else:
            logging.warning("ignoring .pre-commit-config.yaml (pre-commit not invoked)")
