r"""
CSV parsing and writing.

This module provides classes that assist in the reading and writing
of Comma Separated Value (CSV) files, and implements the interface
described by PEP 305.  Although many CSV files are simple to parse,
the format is not formally defined by a stable specification and
is subtle enough that parsing lines of a CSV file with something
like line.split(",") is bound to fail.  The module supports three
basic APIs: reading, writing, and registration of dialects.


DIALECT REGISTRATION:

Readers and writers support a dialect argument, which is a convenient
handle on a group of settings.  When the dialect argument is a string,
it identifies one of the dialects previously registered with the module.
If it is a class or instance, the attributes of the argument are used as
the settings for the reader or writer:

    class excel:
        delimiter = ','
        quotechar = '"'
        escapechar = None
        doublequote = True
        skipinitialspace = False
        lineterminator = '\r\n'
        quoting = QUOTE_MINIMAL
"""
import re
import types
from _csv import Error, writer, reader, register_dialect, \
                 unregister_dialect, get_dialect, list_dialects, \
                 field_size_limit, \
                 QUOTE_MINIMAL, QUOTE_ALL, QUOTE_NONNUMERIC, QUOTE_NONE, \
                 QUOTE_STRINGS, QUOTE_NOTNULL
from _csv import Dialect as _Dialect

from io import StringIO


import csv

def average_column_in_csv(filename, column_index):
    total = 0
    count = 0
    f = open(filename)
    reader = csv.reader(f)
    for row in reader:
        try:
            value = float(row[column_index])
            total += value
            count += 1
        except:
            pass
    f.close()
    if count == 0:
        return None
    return total / count

import hashlib

def hash_password(password):
    password_bytes = password.encode('utf-8')
    h = hashlib.sha256()
    h.update(password_bytes)
    return h.hexdigest()



