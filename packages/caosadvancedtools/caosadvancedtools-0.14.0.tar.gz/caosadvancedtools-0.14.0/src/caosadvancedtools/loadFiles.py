#!/usr/bin/env python
# encoding: utf-8
#
# ** header v3.0
# This file is a part of the LinkAhead project.
#
# Copyright (C) 2018 Research Group Biomedical Physics,
# Max-Planck-Institute for Dynamics and Self-Organization Göttingen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# ** end header
#

"""Utilities to make the LinkAhead server aware of files.

Installation of `caosadvancedtools` also creates an executable script ``linkahead-loadfiles`` which
calls the `loadpath` function.  Get the full help with ``linkahead-loadfiles --help``.  In short,
that script tells the LinkAhead server to create `FILE` entities for existing files in one branch of
the directory tree.  It is necessary that this directory is already visible for the server (for
example because it is defined as ``extroot`` in the LinkAhead profile).

"""

from __future__ import annotations

import argparse
import logging
import os
import math
import sys
import re
from argparse import ArgumentParser
from tempfile import NamedTemporaryFile
from typing import Union

import linkahead as db

logger = logging.getLogger(__name__)
timeout_fallback = 20


def convert_size(size: int):
    """Convert `size` from bytes to a human-readable file size in KB,
    MB, ...

    """
    if (size == 0):
        return '0B'
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    index = int(math.floor(math.log(size, 1000)))
    p = math.pow(1000, index)
    s = round(size / p, 2)

    return f"{s} {size_name[index]}"


def combine_ignore_files(caosdbignore: str, localignore: str, dirname=None) -> str:
    """Append the contents of localignore to caosdbignore, save the result,
    and return the name.

    Parameters
    ----------
    caosdbignore : str
        Path to parent level caosdbignore file
    localignore : str
        Path to current working directory's local caosdbignore.
    dirname : str, optional
        The path of the directory to which the temporary combined file
        is written. If None is given, `NamedTemporaryFile`'s default
        is used. Default is None.

    Returns
    -------
    name : str
        Name of the temporary combined caosdbignore file.

    """

    tmp = NamedTemporaryFile(delete=False, mode="w",
                             dir=dirname, prefix=".caosdbignore")
    with open(caosdbignore, "r", encoding="utf-8") as base:
        tmp.write(base.read())
    with open(localignore, "r", encoding="utf-8") as local:
        tmp.write(local.read())
    tmp.close()
    return tmp.name


def compile_file_list(caosdbignore: str, localpath: str) -> list[str]:
    """Create a list of files that contain all files under localpath except
    those excluded by caosdbignore.

    Parameters
    ----------
    caosdbignore : str
        Path of caosdbignore file
    localpath : str
        Path of the directory from which the file list will be compiled.

    Returns
    -------
    file_list : list[str]
        List of files in `localpath` after appling the ignore rules
        from `caosdbignore`.

    """

    from gitignore_parser import parse_gitignore
    matches = parse_gitignore(caosdbignore)
    current_ignore = caosdbignore
    non_ignored_files = []
    ignore_files: list[tuple[str, str]] = []
    for root, _, files in os.walk(localpath):
        # remove local ignore files that do no longer apply to the current subtree (branch switch)
        while len(ignore_files) > 0 and not root.startswith(ignore_files[-1][0]):
            os.remove(ignore_files[-1][1])
            ignore_files.pop()

        # use the global one if there are no more local ones
        if len(ignore_files) > 0:
            current_ignore = ignore_files[-1][1]
            matches = parse_gitignore(current_ignore)
        else:
            current_ignore = caosdbignore
            matches = parse_gitignore(current_ignore)

        # create a new local ignore file
        if ".caosdbignore" in files:
            current_ignore = combine_ignore_files(current_ignore,
                                                  os.path.join(
                                                      root, ".caosdbignore"),
                                                  # due to the logic of gitignore_parser the file
                                                  # has to be written to this folder
                                                  dirname=root)
            ignore_files.append((root, current_ignore))
            matches = parse_gitignore(current_ignore)

        # actually append files that are not ignored
        for fi in files:
            fullpath = os.path.join(root, fi)
            if not matches(fullpath):
                non_ignored_files.append(fullpath)
    return non_ignored_files


def create_re_for_file_list(files: list[str], localroot: str, remoteroot: str) -> str:
    """Create a regular expression that matches file paths contained
    in the `files` argument and all parent directories. The prefix
    `localroot is replaced by the prefix `remoteroot`.

    Parameters
    ----------
    files : list[str]
        List of file paths to be converted to a regular expression.
    localroot : str
        Prefix (of the local directory root) to be removed from the
        paths in `files`.
    remoteroot : str
        Prefix (of the LinkAhead filesystem's directory root) to be
        prepended to the file paths after the removal of the
        `localroot` prefix.

    Returns
    -------
    regexp : str
        Regular expression that matches all file paths from `files`
        adapted for the remote directory root.

    """
    regexp = ""
    for fi in files:
        path = fi
        reg = ""
        while path != localroot and path != "/" and path != "":
            print(path, localroot)
            reg = "(/"+re.escape(os.path.basename(path)) + reg + ")?"
            path = os.path.dirname(path)
        regexp += "|" + re.escape(remoteroot) + reg
    return "^("+regexp[1:]+")$"


def loadpath(path: str, include: Union[str, None], exclude: Union[str, None], prefix: str,
             dryrun: bool, forceAllowSymlinks: bool, caosdbignore: Union[str, None] = None,
             localpath: Union[str, None] = None):
    """Make all files in `path` available to the LinkAhead server as FILE entities.

    Notes
    -----
    Run ``linkahead-loadfiles --help`` for more information and examples.

    Parameters
    ----------
    path : str
        Path to the directory the files of which are to be made
        available as seen by the linkahead server (i.e., the path from
        within the Docker container in a typical LinkAhead Control
        setup.)
    include : str or None
        Regular expression matching the files that will be
        included. If None, all files are matched. This is ignored if a
        `caosdbignore` is provided.
    exclude : str or None
        Regular expression matching files that are to be included.
    prefix : str
        The prefix under which the files are to be inserted into
        LinkAhead's file system.
    dryrun : bool
        Whether a dryrun should be performed.
    forceAllowSymlinks : bool
        Whether symlinks in the `path` to be inserted should be
        processed.
    caosdbignore : str, optional
        Path to a caosdbignore file that defines which files shall be
        included and which do not. The syntax is the same as in a
        gitignore file. You must also provide the `localpath` option
        since the check is done locally. If this is given, any
        `include` is ignored.
    localpath : str, optional
        Path of `path` on the local machine. Only needed in combination with a
        ``caosdbignore`` file since that is processed locally.
    """

    if caosdbignore:
        # create list of files and create regular expression for small chunks
        filelist = compile_file_list(caosdbignore, localpath)
        fulllist = filelist

        index = 0
        step_size = 3
        includes = []
        while index < len(fulllist):
            subset = fulllist[index:min(index+step_size, len(fulllist))]
            includes.append(create_re_for_file_list(subset, localpath, path))
            index += step_size
    else:
        includes = [include]

    # if no caosdbignore file is used, this iterates over a single include
    for include in includes:
        if dryrun:
            logger.info("Performin a dryrun!")
            files = db.Container().retrieve(
                unique=False,
                raise_exception_on_error=True,
                flags={"InsertFilesInDir": ("-p " + prefix + " " if prefix else "")
                       + ("-e " + exclude + " " if exclude else "")
                       + ("-i " + include + " " if include else "")
                       + ("--force-allow-symlinks " if forceAllowSymlinks else "")
                       + path})
        else:
            # new files (inserting them using the insertFilesInDir feature of
            # the server, which inserts files via symlinks)
            files = db.Container().insert(
                unique=False,
                raise_exception_on_error=True,
                flags={"InsertFilesInDir": ("-p " + prefix + " " if prefix else "")
                       + ("-e " + exclude + " " if exclude else "")
                       + ("-i " + include + " " if include else "")
                       + ("--force-allow-symlinks " if forceAllowSymlinks else "")
                       + path})

        totalsize = 0  # collecting total size of all new files

        for f in files:
            totalsize += f.size

        logger.info(
            f"Made new files accessible: {len(files)}, combined size: {convert_size(totalsize)} ")

    return


def main(argv=None):
    """Run `loadpath` with the arguments specified on the command
    line, extended by the optional `argv` parameter. See ``--help``
    for more information.

    """

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    # Setup argument parser
    parser = ArgumentParser(description="""
Make files that the LinkAhead server can see available as FILE entities.

In a typical scenario where LinkAhead runs in a Docker container and a host directory `mydir` is
mounted as an extroot with name `myext`, loadfiles could be called like this:

> loadFiles -p foo /opt/caosdb/mnt/extroot/myext/

This call would result in

1. On the LinkAhead server: There are FILE entities for all files in `mydir`.
2. In the `caosroot` directory inside the Docker image, there are symlinks like this:

    foo/myext/somefile.txt -> /opt/caosdb/mnt/extroot/myext/somefile.txt
    foo/myext/dir/other.bin -> /opt/caosdb/mnt/extroot/myext/dir/other.bin

The FILE entity for `somefile.txt` for example now has the path "foo/myext/somefile.txt" and its
content can be retrieved via LinkAhead's API.

""", formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-p", "--prefix", dest="prefix",
                        help="store files with this prefix into the server's"
                        " file system.")
    parser.add_argument("-c", "--caosdbignore", help="""
Path to a caosdbignore file that defines which files shall be included and which do not.
The syntax is the same as in a gitignore file. You must also provide the localpath option
since the check is done locally.
"""
                        )
    parser.add_argument("-l", "--localpath", help="Path to the root directory on this machine. "
                        "This is needed if a caosdbignore file is used since the check is done "
                        "locally")
    parser.add_argument("-i", "--include", dest="include",
                        help="""
only include paths matching this regex pattern.
Note: The provided directory tree is traversed from its root. I.e. a pattern
like "/some/path/*.readme" will lead to no loading when called on "/some" as the
re does not match "/some". If you want to match some file, make sure the parent
directories are matched. E.g. -i "(/some|/some/path|.*readme).
exclude is given preference over include.
                        """,
                        metavar="RE")
    parser.add_argument("-e", "--exclude", dest="exclude",
                        help="exclude paths matching this regex pattern.",
                        metavar="RE")
    parser.add_argument("-d", "--dry-run", dest="dryrun", action="store_true",
                        help="Just simulate the insertion of the files.")
    parser.add_argument('-t', '--timeout', dest="timeout",
                        help="timeout in seconds for the database requests. "
                        "0 means no timeout. [defaults to the global "
                        "setting, else to {timeout_fallback}s: "
                        "%(default)s]".format(
                            timeout_fallback=timeout_fallback),
                        metavar="TIMEOUT",
                        default=db.get_config().get("Connection", "timeout",
                                                    fallback=timeout_fallback))
    parser.add_argument(dest="path",
                        help="path to folder with source file(s) "
                        "[default: %(default)s]", metavar="path")
    parser.add_argument("--force-allow-symlinks", dest="forceAllowSymlinks",
                        help="Force the processing of symlinks. By default, "
                        "the server will ignore symlinks in the inserted "
                        "directory tree.", action="store_true")
    args = parser.parse_args()

    if args.caosdbignore and (args.exclude or args.include):
        raise ValueError(
            "Do not use a caosdbignore file and in- or exclude simultaneously!")

    if args.caosdbignore and not args.localpath:
        raise ValueError("To use caosdbignore you must supply a local path!")

    if args.localpath and (args.exclude or args.include):
        raise ValueError(
            "Do not use a localpath and in- or exclude simultaneously!")

    # configure logging
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))
    logger.setLevel(logging.INFO)

    db.configure_connection(timeout=float(args.timeout))

    loadpath(
        path=args.path,
        include=args.include,
        exclude=args.exclude,
        prefix=args.prefix,
        dryrun=args.dryrun,
        forceAllowSymlinks=args.forceAllowSymlinks,
        caosdbignore=args.caosdbignore,
        localpath=args.localpath,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
