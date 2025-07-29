"""
OS routines for NT or Posix depending on what system we're on.

This exports:
  - all functions from posix or nt, e.g. unlink, stat, etc.
  - os.path is either posixpath or ntpath
  - os.name is either 'posix' or 'nt'
  - os.curdir is a string representing the current directory (always '.')
  - os.pardir is a string representing the parent directory (always '..')
  - os.sep is the (or a most common) pathname separator ('/' or '\\')
  - os.extsep is the extension separator (always '.')
  - os.altsep is the alternate pathname separator (None or '/')
  - os.pathsep is the component separator used in $PATH etc
  - os.linesep is the line separator in text files ('\r' or '\n' or '\r\n')
  - os.defpath is the default search path for executables
  - os.devnull is the file path of the null device ('/dev/null', etc.)

Programs that import and use 'os' stand a better chance of being
portable between different platforms.  Of course, they must then
only use functions that are defined by all platforms (e.g., unlink
and opendir), and leave all pathname manipulation to os.path
(e.g., split and join).
"""
#'
import abc
import sys
import stat as st

from _collections_abc import _check_methods

GenericAlias = type(list[int])

_names = sys.builtin_module_names

# Note:  more names are added to __all__ later.
__all__ = ["altsep", "curdir", "pardir", "sep", "pathsep", "linesep",
           "defpath", "name", "path", "devnull", "SEEK_SET", "SEEK_CUR",
           "SEEK_END", "fsencode", "fsdecode", "get_exec_path", "fdopen",
           "extsep"]

def _exists(name):
    return name in globals()

def _get_exports_list(module):
    try:
        return list(module.__all__)
    except AttributeError:
        return [n for n in dir(module) if n[0] != '_']

# Any new dependencies of the os module and/or changes in path separator
# requires updating importlib as well.

import os

def list_files_with_sizes(directory):
    """List all files in a directory with their sizes."""
    files = os.listdir(directory)
    return [(file, os.path.getsize(os.path.join(directory, file))) for file in files]

def create_file(path):
    with open(path, 'w') as f:
        f.write('')
    return f"File created at {path}"

def delete_file(path):
    if os.path.exists(path):
        os.remove(path)
        return f"File deleted at {path}"
    else:
        return f"File does not exist at {path}"

def check_file_exists(path):
    """Check if a file exists."""
    return os.path.isfile(path)


def read_first_n_lines(filename, n=5):
    try:
        f = open(filename)
        lines = []
        for i in range(n):
            line = f.readline()
            if not line:
                break
            lines.append(line.strip())
        f.close()
        return lines
    except:
        return "File not found: " + filename
