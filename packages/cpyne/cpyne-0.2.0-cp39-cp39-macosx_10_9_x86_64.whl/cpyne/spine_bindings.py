r"""Wrapper for manual_binding.h

Generated with:
/Library/Frameworks/Python.framework/Versions/Current/bin/ctypesgen manual_binding.h -I src/spine-c/include/spine -L src/cpyne -lspine -o src/cpyne/spine_bindings.py

Do not modify this file.
"""

__docformat__ = "restructuredtext"

# Begin preamble for Python

import ctypes
import sys
from ctypes import *  # noqa: F401, F403

_int_types = (ctypes.c_int16, ctypes.c_int32)
if hasattr(ctypes, "c_int64"):
    # Some builds of ctypes apparently do not have ctypes.c_int64
    # defined; it's a pretty good bet that these builds do not
    # have 64-bit pointers.
    _int_types += (ctypes.c_int64,)
for t in _int_types:
    if ctypes.sizeof(t) == ctypes.sizeof(ctypes.c_size_t):
        c_ptrdiff_t = t
del t
del _int_types



class UserString:
    def __init__(self, seq):
        if isinstance(seq, bytes):
            self.data = seq
        elif isinstance(seq, UserString):
            self.data = seq.data[:]
        else:
            self.data = str(seq).encode()

    def __bytes__(self):
        return self.data

    def __str__(self):
        return self.data.decode()

    def __repr__(self):
        return repr(self.data)

    def __int__(self):
        return int(self.data.decode())

    def __long__(self):
        return int(self.data.decode())

    def __float__(self):
        return float(self.data.decode())

    def __complex__(self):
        return complex(self.data.decode())

    def __hash__(self):
        return hash(self.data)

    def __le__(self, string):
        if isinstance(string, UserString):
            return self.data <= string.data
        else:
            return self.data <= string

    def __lt__(self, string):
        if isinstance(string, UserString):
            return self.data < string.data
        else:
            return self.data < string

    def __ge__(self, string):
        if isinstance(string, UserString):
            return self.data >= string.data
        else:
            return self.data >= string

    def __gt__(self, string):
        if isinstance(string, UserString):
            return self.data > string.data
        else:
            return self.data > string

    def __eq__(self, string):
        if isinstance(string, UserString):
            return self.data == string.data
        else:
            return self.data == string

    def __ne__(self, string):
        if isinstance(string, UserString):
            return self.data != string.data
        else:
            return self.data != string

    def __contains__(self, char):
        return char in self.data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.__class__(self.data[index])

    def __getslice__(self, start, end):
        start = max(start, 0)
        end = max(end, 0)
        return self.__class__(self.data[start:end])

    def __add__(self, other):
        if isinstance(other, UserString):
            return self.__class__(self.data + other.data)
        elif isinstance(other, bytes):
            return self.__class__(self.data + other)
        else:
            return self.__class__(self.data + str(other).encode())

    def __radd__(self, other):
        if isinstance(other, bytes):
            return self.__class__(other + self.data)
        else:
            return self.__class__(str(other).encode() + self.data)

    def __mul__(self, n):
        return self.__class__(self.data * n)

    __rmul__ = __mul__

    def __mod__(self, args):
        return self.__class__(self.data % args)

    # the following methods are defined in alphabetical order:
    def capitalize(self):
        return self.__class__(self.data.capitalize())

    def center(self, width, *args):
        return self.__class__(self.data.center(width, *args))

    def count(self, sub, start=0, end=sys.maxsize):
        return self.data.count(sub, start, end)

    def decode(self, encoding=None, errors=None):  # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.decode(encoding, errors))
            else:
                return self.__class__(self.data.decode(encoding))
        else:
            return self.__class__(self.data.decode())

    def encode(self, encoding=None, errors=None):  # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.encode(encoding, errors))
            else:
                return self.__class__(self.data.encode(encoding))
        else:
            return self.__class__(self.data.encode())

    def endswith(self, suffix, start=0, end=sys.maxsize):
        return self.data.endswith(suffix, start, end)

    def expandtabs(self, tabsize=8):
        return self.__class__(self.data.expandtabs(tabsize))

    def find(self, sub, start=0, end=sys.maxsize):
        return self.data.find(sub, start, end)

    def index(self, sub, start=0, end=sys.maxsize):
        return self.data.index(sub, start, end)

    def isalpha(self):
        return self.data.isalpha()

    def isalnum(self):
        return self.data.isalnum()

    def isdecimal(self):
        return self.data.isdecimal()

    def isdigit(self):
        return self.data.isdigit()

    def islower(self):
        return self.data.islower()

    def isnumeric(self):
        return self.data.isnumeric()

    def isspace(self):
        return self.data.isspace()

    def istitle(self):
        return self.data.istitle()

    def isupper(self):
        return self.data.isupper()

    def join(self, seq):
        return self.data.join(seq)

    def ljust(self, width, *args):
        return self.__class__(self.data.ljust(width, *args))

    def lower(self):
        return self.__class__(self.data.lower())

    def lstrip(self, chars=None):
        return self.__class__(self.data.lstrip(chars))

    def partition(self, sep):
        return self.data.partition(sep)

    def replace(self, old, new, maxsplit=-1):
        return self.__class__(self.data.replace(old, new, maxsplit))

    def rfind(self, sub, start=0, end=sys.maxsize):
        return self.data.rfind(sub, start, end)

    def rindex(self, sub, start=0, end=sys.maxsize):
        return self.data.rindex(sub, start, end)

    def rjust(self, width, *args):
        return self.__class__(self.data.rjust(width, *args))

    def rpartition(self, sep):
        return self.data.rpartition(sep)

    def rstrip(self, chars=None):
        return self.__class__(self.data.rstrip(chars))

    def split(self, sep=None, maxsplit=-1):
        return self.data.split(sep, maxsplit)

    def rsplit(self, sep=None, maxsplit=-1):
        return self.data.rsplit(sep, maxsplit)

    def splitlines(self, keepends=0):
        return self.data.splitlines(keepends)

    def startswith(self, prefix, start=0, end=sys.maxsize):
        return self.data.startswith(prefix, start, end)

    def strip(self, chars=None):
        return self.__class__(self.data.strip(chars))

    def swapcase(self):
        return self.__class__(self.data.swapcase())

    def title(self):
        return self.__class__(self.data.title())

    def translate(self, *args):
        return self.__class__(self.data.translate(*args))

    def upper(self):
        return self.__class__(self.data.upper())

    def zfill(self, width):
        return self.__class__(self.data.zfill(width))


class MutableString(UserString):
    """mutable string objects

    Python strings are immutable objects.  This has the advantage, that
    strings may be used as dictionary keys.  If this property isn't needed
    and you insist on changing string values in place instead, you may cheat
    and use MutableString.

    But the purpose of this class is an educational one: to prevent
    people from inventing their own mutable string class derived
    from UserString and than forget thereby to remove (override) the
    __hash__ method inherited from UserString.  This would lead to
    errors that would be very hard to track down.

    A faster and better solution is to rewrite your program using lists."""

    def __init__(self, string=""):
        self.data = string

    def __hash__(self):
        raise TypeError("unhashable type (it is mutable)")

    def __setitem__(self, index, sub):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data):
            raise IndexError
        self.data = self.data[:index] + sub + self.data[index + 1 :]

    def __delitem__(self, index):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data):
            raise IndexError
        self.data = self.data[:index] + self.data[index + 1 :]

    def __setslice__(self, start, end, sub):
        start = max(start, 0)
        end = max(end, 0)
        if isinstance(sub, UserString):
            self.data = self.data[:start] + sub.data + self.data[end:]
        elif isinstance(sub, bytes):
            self.data = self.data[:start] + sub + self.data[end:]
        else:
            self.data = self.data[:start] + str(sub).encode() + self.data[end:]

    def __delslice__(self, start, end):
        start = max(start, 0)
        end = max(end, 0)
        self.data = self.data[:start] + self.data[end:]

    def immutable(self):
        return UserString(self.data)

    def __iadd__(self, other):
        if isinstance(other, UserString):
            self.data += other.data
        elif isinstance(other, bytes):
            self.data += other
        else:
            self.data += str(other).encode()
        return self

    def __imul__(self, n):
        self.data *= n
        return self


class String(MutableString, ctypes.Union):

    _fields_ = [("raw", ctypes.POINTER(ctypes.c_char)), ("data", ctypes.c_char_p)]

    def __init__(self, obj=b""):
        if isinstance(obj, (bytes, UserString)):
            self.data = bytes(obj)
        else:
            self.raw = obj

    def __len__(self):
        return self.data and len(self.data) or 0

    def from_param(cls, obj):
        # Convert None or 0
        if obj is None or obj == 0:
            return cls(ctypes.POINTER(ctypes.c_char)())

        # Convert from String
        elif isinstance(obj, String):
            return obj

        # Convert from bytes
        elif isinstance(obj, bytes):
            return cls(obj)

        # Convert from str
        elif isinstance(obj, str):
            return cls(obj.encode())

        # Convert from c_char_p
        elif isinstance(obj, ctypes.c_char_p):
            return obj

        # Convert from POINTER(ctypes.c_char)
        elif isinstance(obj, ctypes.POINTER(ctypes.c_char)):
            return obj

        # Convert from raw pointer
        elif isinstance(obj, int):
            return cls(ctypes.cast(obj, ctypes.POINTER(ctypes.c_char)))

        # Convert from ctypes.c_char array
        elif isinstance(obj, ctypes.c_char * len(obj)):
            return obj

        # Convert from object
        else:
            return String.from_param(obj._as_parameter_)

    from_param = classmethod(from_param)


def ReturnString(obj, func=None, arguments=None):
    return String.from_param(obj)


# As of ctypes 1.0, ctypes does not support custom error-checking
# functions on callbacks, nor does it support custom datatypes on
# callbacks, so we must ensure that all callbacks return
# primitive datatypes.
#
# Non-primitive return values wrapped with UNCHECKED won't be
# typechecked, and will be converted to ctypes.c_void_p.
def UNCHECKED(type):
    if hasattr(type, "_type_") and isinstance(type._type_, str) and type._type_ != "P":
        return type
    else:
        return ctypes.c_void_p


# ctypes doesn't have direct support for variadic functions, so we have to write
# our own wrapper class
class _variadic_function(object):
    def __init__(self, func, restype, argtypes, errcheck):
        self.func = func
        self.func.restype = restype
        self.argtypes = argtypes
        if errcheck:
            self.func.errcheck = errcheck

    def _as_parameter_(self):
        # So we can pass this variadic function as a function pointer
        return self.func

    def __call__(self, *args):
        fixed_args = []
        i = 0
        for argtype in self.argtypes:
            # Typecheck what we can
            fixed_args.append(argtype.from_param(args[i]))
            i += 1
        return self.func(*fixed_args + list(args[i:]))


def ord_if_char(value):
    """
    Simple helper used for casts to simple builtin types:  if the argument is a
    string type, it will be converted to it's ordinal value.

    This function will raise an exception if the argument is string with more
    than one characters.
    """
    return ord(value) if (isinstance(value, bytes) or isinstance(value, str)) else value

# End preamble

_libs = {}
_libdirs = ['src/cpyne']

# Begin loader

"""
Load libraries - appropriately for all our supported platforms
"""
# ----------------------------------------------------------------------------
# Copyright (c) 2008 David James
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

import ctypes
import ctypes.util
import glob
import os.path
import platform
import re
import sys


def _environ_path(name):
    """Split an environment variable into a path-like list elements"""
    if name in os.environ:
        return os.environ[name].split(":")
    return []


class LibraryLoader:
    """
    A base class For loading of libraries ;-)
    Subclasses load libraries for specific platforms.
    """

    # library names formatted specifically for platforms
    name_formats = ["%s"]

    class Lookup:
        """Looking up calling conventions for a platform"""

        mode = ctypes.DEFAULT_MODE

        def __init__(self, path):
            super(LibraryLoader.Lookup, self).__init__()
            self.access = dict(cdecl=ctypes.CDLL(path, self.mode))

        def get(self, name, calling_convention="cdecl"):
            """Return the given name according to the selected calling convention"""
            if calling_convention not in self.access:
                raise LookupError(
                    "Unknown calling convention '{}' for function '{}'".format(
                        calling_convention, name
                    )
                )
            return getattr(self.access[calling_convention], name)

        def has(self, name, calling_convention="cdecl"):
            """Return True if this given calling convention finds the given 'name'"""
            if calling_convention not in self.access:
                return False
            return hasattr(self.access[calling_convention], name)

        def __getattr__(self, name):
            return getattr(self.access["cdecl"], name)

    def __init__(self):
        self.other_dirs = []

    def __call__(self, libname):
        """Given the name of a library, load it."""
        paths = self.getpaths(libname)

        for path in paths:
            # noinspection PyBroadException
            try:
                return self.Lookup(path)
            except Exception:  # pylint: disable=broad-except
                pass

        raise ImportError("Could not load %s." % libname)

    def getpaths(self, libname):
        """Return a list of paths where the library might be found."""
        if os.path.isabs(libname):
            yield libname
        else:
            # search through a prioritized series of locations for the library

            # we first search any specific directories identified by user
            for dir_i in self.other_dirs:
                for fmt in self.name_formats:
                    # dir_i should be absolute already
                    yield os.path.join(dir_i, fmt % libname)

            # check if this code is even stored in a physical file
            try:
                this_file = __file__
            except NameError:
                this_file = None

            # then we search the directory where the generated python interface is stored
            if this_file is not None:
                for fmt in self.name_formats:
                    yield os.path.abspath(os.path.join(os.path.dirname(__file__), fmt % libname))

            # now, use the ctypes tools to try to find the library
            for fmt in self.name_formats:
                path = ctypes.util.find_library(fmt % libname)
                if path:
                    yield path

            # then we search all paths identified as platform-specific lib paths
            for path in self.getplatformpaths(libname):
                yield path

            # Finally, we'll try the users current working directory
            for fmt in self.name_formats:
                yield os.path.abspath(os.path.join(os.path.curdir, fmt % libname))

    def getplatformpaths(self, _libname):  # pylint: disable=no-self-use
        """Return all the library paths available in this platform"""
        return []


# Darwin (Mac OS X)


class DarwinLibraryLoader(LibraryLoader):
    """Library loader for MacOS"""

    name_formats = [
        "lib%s.dylib",
        "lib%s.so",
        "lib%s.bundle",
        "%s.dylib",
        "%s.so",
        "%s.bundle",
        "%s",
    ]

    class Lookup(LibraryLoader.Lookup):
        """
        Looking up library files for this platform (Darwin aka MacOS)
        """

        # Darwin requires dlopen to be called with mode RTLD_GLOBAL instead
        # of the default RTLD_LOCAL.  Without this, you end up with
        # libraries not being loadable, resulting in "Symbol not found"
        # errors
        mode = ctypes.RTLD_GLOBAL

    def getplatformpaths(self, libname):
        if os.path.pathsep in libname:
            names = [libname]
        else:
            names = [fmt % libname for fmt in self.name_formats]

        for directory in self.getdirs(libname):
            for name in names:
                yield os.path.join(directory, name)

    @staticmethod
    def getdirs(libname):
        """Implements the dylib search as specified in Apple documentation:

        http://developer.apple.com/documentation/DeveloperTools/Conceptual/
            DynamicLibraries/Articles/DynamicLibraryUsageGuidelines.html

        Before commencing the standard search, the method first checks
        the bundle's ``Frameworks`` directory if the application is running
        within a bundle (OS X .app).
        """

        dyld_fallback_library_path = _environ_path("DYLD_FALLBACK_LIBRARY_PATH")
        if not dyld_fallback_library_path:
            dyld_fallback_library_path = [
                os.path.expanduser("~/lib"),
                "/usr/local/lib",
                "/usr/lib",
            ]

        dirs = []

        if "/" in libname:
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
        else:
            dirs.extend(_environ_path("LD_LIBRARY_PATH"))
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
            dirs.extend(_environ_path("LD_RUN_PATH"))

        if hasattr(sys, "frozen") and getattr(sys, "frozen") == "macosx_app":
            dirs.append(os.path.join(os.environ["RESOURCEPATH"], "..", "Frameworks"))

        dirs.extend(dyld_fallback_library_path)

        return dirs


# Posix


class PosixLibraryLoader(LibraryLoader):
    """Library loader for POSIX-like systems (including Linux)"""

    _ld_so_cache = None

    _include = re.compile(r"^\s*include\s+(?P<pattern>.*)")

    name_formats = ["lib%s.so", "%s.so", "%s"]

    class _Directories(dict):
        """Deal with directories"""

        def __init__(self):
            dict.__init__(self)
            self.order = 0

        def add(self, directory):
            """Add a directory to our current set of directories"""
            if len(directory) > 1:
                directory = directory.rstrip(os.path.sep)
            # only adds and updates order if exists and not already in set
            if not os.path.exists(directory):
                return
            order = self.setdefault(directory, self.order)
            if order == self.order:
                self.order += 1

        def extend(self, directories):
            """Add a list of directories to our set"""
            for a_dir in directories:
                self.add(a_dir)

        def ordered(self):
            """Sort the list of directories"""
            return (i[0] for i in sorted(self.items(), key=lambda d: d[1]))

    def _get_ld_so_conf_dirs(self, conf, dirs):
        """
        Recursive function to help parse all ld.so.conf files, including proper
        handling of the `include` directive.
        """

        try:
            with open(conf) as fileobj:
                for dirname in fileobj:
                    dirname = dirname.strip()
                    if not dirname:
                        continue

                    match = self._include.match(dirname)
                    if not match:
                        dirs.add(dirname)
                    else:
                        for dir2 in glob.glob(match.group("pattern")):
                            self._get_ld_so_conf_dirs(dir2, dirs)
        except IOError:
            pass

    def _create_ld_so_cache(self):
        # Recreate search path followed by ld.so.  This is going to be
        # slow to build, and incorrect (ld.so uses ld.so.cache, which may
        # not be up-to-date).  Used only as fallback for distros without
        # /sbin/ldconfig.
        #
        # We assume the DT_RPATH and DT_RUNPATH binary sections are omitted.

        directories = self._Directories()
        for name in (
            "LD_LIBRARY_PATH",
            "SHLIB_PATH",  # HP-UX
            "LIBPATH",  # OS/2, AIX
            "LIBRARY_PATH",  # BE/OS
        ):
            if name in os.environ:
                directories.extend(os.environ[name].split(os.pathsep))

        self._get_ld_so_conf_dirs("/etc/ld.so.conf", directories)

        bitage = platform.architecture()[0]

        unix_lib_dirs_list = []
        if bitage.startswith("64"):
            # prefer 64 bit if that is our arch
            unix_lib_dirs_list += ["/lib64", "/usr/lib64"]

        # must include standard libs, since those paths are also used by 64 bit
        # installs
        unix_lib_dirs_list += ["/lib", "/usr/lib"]
        if sys.platform.startswith("linux"):
            # Try and support multiarch work in Ubuntu
            # https://wiki.ubuntu.com/MultiarchSpec
            if bitage.startswith("32"):
                # Assume Intel/AMD x86 compat
                unix_lib_dirs_list += ["/lib/i386-linux-gnu", "/usr/lib/i386-linux-gnu"]
            elif bitage.startswith("64"):
                # Assume Intel/AMD x86 compatible
                unix_lib_dirs_list += [
                    "/lib/x86_64-linux-gnu",
                    "/usr/lib/x86_64-linux-gnu",
                ]
            else:
                # guess...
                unix_lib_dirs_list += glob.glob("/lib/*linux-gnu")
        directories.extend(unix_lib_dirs_list)

        cache = {}
        lib_re = re.compile(r"lib(.*)\.s[ol]")
        # ext_re = re.compile(r"\.s[ol]$")
        for our_dir in directories.ordered():
            try:
                for path in glob.glob("%s/*.s[ol]*" % our_dir):
                    file = os.path.basename(path)

                    # Index by filename
                    cache_i = cache.setdefault(file, set())
                    cache_i.add(path)

                    # Index by library name
                    match = lib_re.match(file)
                    if match:
                        library = match.group(1)
                        cache_i = cache.setdefault(library, set())
                        cache_i.add(path)
            except OSError:
                pass

        self._ld_so_cache = cache

    def getplatformpaths(self, libname):
        if self._ld_so_cache is None:
            self._create_ld_so_cache()

        result = self._ld_so_cache.get(libname, set())
        for i in result:
            # we iterate through all found paths for library, since we may have
            # actually found multiple architectures or other library types that
            # may not load
            yield i


# Windows


class WindowsLibraryLoader(LibraryLoader):
    """Library loader for Microsoft Windows"""

    name_formats = ["%s.dll", "lib%s.dll", "%slib.dll", "%s"]

    class Lookup(LibraryLoader.Lookup):
        """Lookup class for Windows libraries..."""

        def __init__(self, path):
            super(WindowsLibraryLoader.Lookup, self).__init__(path)
            self.access["stdcall"] = ctypes.windll.LoadLibrary(path)


# Platform switching

# If your value of sys.platform does not appear in this dict, please contact
# the Ctypesgen maintainers.

loaderclass = {
    "darwin": DarwinLibraryLoader,
    "cygwin": WindowsLibraryLoader,
    "win32": WindowsLibraryLoader,
    "msys": WindowsLibraryLoader,
}

load_library = loaderclass.get(sys.platform, PosixLibraryLoader)()


def add_library_search_dirs(other_dirs):
    """
    Add libraries to search paths.
    If library paths are relative, convert them to absolute with respect to this
    file's directory
    """
    for path in other_dirs:
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        load_library.other_dirs.append(path)


del loaderclass

# End loader

add_library_search_dirs(['src/cpyne'])

# Begin libraries
_libs["spine"] = load_library("spine")

# 1 libraries
# End libraries

# No modules

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 90
class struct_spColor(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 95
class struct_spFloatArray(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 101
class struct_spShortArray(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 107
class struct_spIntArray(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 113
class struct_spUnsignedShortArray(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 119
class struct_spArrayFloatArray(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 125
class struct_spArrayShortArray(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 131
class struct_spBoneDataArray(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 137
class struct_spIkConstraintDataArray(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 143
class struct_spTransformConstraintDataArray(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 149
class struct_spPathConstraintDataArray(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 155
class struct_spTrackEntryArray(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 162
class struct_spAttachment(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 170
class struct_spVertexAttachment(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 181
class struct_spRegionAttachment(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 194
class struct_spMeshAttachment(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 217
class struct_spPointAttachment(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 223
class struct_spClippingAttachment(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 228
class struct_spPathAttachment(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 235
class struct_spBoundingBoxAttachment(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 239
class struct_spBoneData(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 249
class struct_spSlotData(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 259
class struct_spEventData(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 269
class struct_spEvent(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 279
class struct_spTimeline(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 284
class struct_spCurveTimeline(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 289
class struct_spBaseTimeline(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 296
class struct_spColorTimeline(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 303
class struct_spTwoColorTimeline(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 310
class struct_spAttachmentTimeline(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 318
class struct_spEventTimeline(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 325
class struct_spDrawOrderTimeline(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 333
class struct_spDeformTimeline(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 343
class struct_spIkConstraintTimeline(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 350
class struct_spTransformConstraintTimeline(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 357
class struct_spPathConstraintPositionTimeline(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 364
class struct_spPathConstraintSpacingTimeline(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 371
class struct_spPathConstraintMixTimeline(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 378
class struct_spAnimation(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 385
class struct_spBone(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 400
class struct_spSlot(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 412
class struct_spPathConstraintData(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 426
class struct_spPathConstraint(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 446
class struct_spTransformConstraintData(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 459
class struct_spTransformConstraint(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 468
class struct_spIkConstraintData(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 483
class struct_spIkConstraint(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 496
class struct_spSkeleton(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 517
class struct_spAttachmentLoader(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 523
class struct_spAtlasAttachmentLoader(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 528
class struct__Entry(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 535
class struct__SkinHashTableEntry(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 540
class struct_spSkin(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 548
class struct__spSkin(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 554
class struct_spVertexEffect(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 560
class struct_spJitterVertexEffect(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 566
class struct_spSwirlVertexEffect(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 576
class struct_spSkeletonData(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 601
class struct_spSkeletonJson(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 607
class struct_spSkeletonBinary(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 613
class struct_spAnimationStateData(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 619
class struct_spPolygon(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 625
class struct_spSkeletonBounds(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 632
class struct_spTriangulator(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 642
class struct_spSkeletonClipping(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 82
class struct_spAnimationState(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 659
class struct_spTrackEntry(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 721
class struct_spAtlasPage(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 732
class struct_spAtlasRegion(Structure):
    pass

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 748
class struct_spAtlas(Structure):
    pass

struct_spColor.__slots__ = [
    'r',
    'g',
    'b',
    'a',
]
struct_spColor._fields_ = [
    ('r', c_float),
    ('g', c_float),
    ('b', c_float),
    ('a', c_float),
]

spColor = struct_spColor# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 92

struct_spFloatArray.__slots__ = [
    'items',
    'size',
    'capacity',
]
struct_spFloatArray._fields_ = [
    ('items', POINTER(c_float)),
    ('size', c_int),
    ('capacity', c_int),
]

spFloatArray = struct_spFloatArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 99

struct_spShortArray.__slots__ = [
    'items',
    'size',
    'capacity',
]
struct_spShortArray._fields_ = [
    ('items', POINTER(c_short)),
    ('size', c_int),
    ('capacity', c_int),
]

spShortArray = struct_spShortArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 105

struct_spIntArray.__slots__ = [
    'items',
    'size',
    'capacity',
]
struct_spIntArray._fields_ = [
    ('items', POINTER(c_int)),
    ('size', c_int),
    ('capacity', c_int),
]

spIntArray = struct_spIntArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 111

struct_spUnsignedShortArray.__slots__ = [
    'items',
    'size',
    'capacity',
]
struct_spUnsignedShortArray._fields_ = [
    ('items', POINTER(c_ushort)),
    ('size', c_int),
    ('capacity', c_int),
]

spUnsignedShortArray = struct_spUnsignedShortArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 117

struct_spArrayFloatArray.__slots__ = [
    'items',
    'size',
    'capacity',
]
struct_spArrayFloatArray._fields_ = [
    ('items', POINTER(POINTER(spFloatArray))),
    ('size', c_int),
    ('capacity', c_int),
]

spArrayFloatArray = struct_spArrayFloatArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 123

struct_spArrayShortArray.__slots__ = [
    'items',
    'size',
    'capacity',
]
struct_spArrayShortArray._fields_ = [
    ('items', POINTER(POINTER(spShortArray))),
    ('size', c_int),
    ('capacity', c_int),
]

spArrayShortArray = struct_spArrayShortArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 129

struct_spBoneDataArray.__slots__ = [
    'items',
    'size',
    'capacity',
]
struct_spBoneDataArray._fields_ = [
    ('items', POINTER(POINTER(struct_spBoneData))),
    ('size', c_int),
    ('capacity', c_int),
]

spBoneDataArray = struct_spBoneDataArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 135

struct_spIkConstraintDataArray.__slots__ = [
    'items',
    'size',
    'capacity',
]
struct_spIkConstraintDataArray._fields_ = [
    ('items', POINTER(POINTER(struct_spIkConstraintData))),
    ('size', c_int),
    ('capacity', c_int),
]

spIkConstraintDataArray = struct_spIkConstraintDataArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 141

struct_spTransformConstraintDataArray.__slots__ = [
    'items',
    'size',
    'capacity',
]
struct_spTransformConstraintDataArray._fields_ = [
    ('items', POINTER(POINTER(struct_spTransformConstraintData))),
    ('size', c_int),
    ('capacity', c_int),
]

spTransformConstraintDataArray = struct_spTransformConstraintDataArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 147

struct_spPathConstraintDataArray.__slots__ = [
    'items',
    'size',
    'capacity',
]
struct_spPathConstraintDataArray._fields_ = [
    ('items', POINTER(POINTER(struct_spPathConstraintData))),
    ('size', c_int),
    ('capacity', c_int),
]

spPathConstraintDataArray = struct_spPathConstraintDataArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 153

struct_spTrackEntryArray.__slots__ = [
    'items',
    'size',
    'capacity',
]
struct_spTrackEntryArray._fields_ = [
    ('items', POINTER(POINTER(struct_spTrackEntry))),
    ('size', c_int),
    ('capacity', c_int),
]

spTrackEntryArray = struct_spTrackEntryArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 159

struct_spAttachment.__slots__ = [
    'name',
    'type',
    'vtable',
    'refCount',
    'attachmentLoader',
]
struct_spAttachment._fields_ = [
    ('name', String),
    ('type', c_int),
    ('vtable', POINTER(None)),
    ('refCount', c_int),
    ('attachmentLoader', POINTER(struct_spAttachmentLoader)),
]

spAttachment = struct_spAttachment# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 168

struct_spVertexAttachment.__slots__ = [
    'super',
    'id',
    'bonesCount',
    'bones',
    'verticesCount',
    'vertices',
    'worldVerticesLength',
    'deformAttachment',
]
struct_spVertexAttachment._fields_ = [
    ('super', spAttachment),
    ('id', c_int),
    ('bonesCount', c_int),
    ('bones', POINTER(c_int)),
    ('verticesCount', c_int),
    ('vertices', POINTER(c_float)),
    ('worldVerticesLength', c_int),
    ('deformAttachment', POINTER(struct_spVertexAttachment)),
]

spVertexAttachment = struct_spVertexAttachment# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 179

struct_spRegionAttachment.__slots__ = [
    'super',
    'path',
    'x',
    'y',
    'scaleX',
    'scaleY',
    'rotation',
    'width',
    'height',
    'color',
    'rendererObject',
    'regionOffsetX',
    'regionOffsetY',
    'regionWidth',
    'regionHeight',
    'regionOriginalWidth',
    'regionOriginalHeight',
    'offset',
    'uvs',
]
struct_spRegionAttachment._fields_ = [
    ('super', spAttachment),
    ('path', String),
    ('x', c_float),
    ('y', c_float),
    ('scaleX', c_float),
    ('scaleY', c_float),
    ('rotation', c_float),
    ('width', c_float),
    ('height', c_float),
    ('color', spColor),
    ('rendererObject', POINTER(None)),
    ('regionOffsetX', c_int),
    ('regionOffsetY', c_int),
    ('regionWidth', c_int),
    ('regionHeight', c_int),
    ('regionOriginalWidth', c_int),
    ('regionOriginalHeight', c_int),
    ('offset', c_float * int(8)),
    ('uvs', c_float * int(8)),
]

spRegionAttachment = struct_spRegionAttachment# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 192

struct_spMeshAttachment.__slots__ = [
    'super',
    'path',
    'regionUVs',
    'uvs',
    'trianglesCount',
    'triangles',
    'r',
    'g',
    'b',
    'a',
    'hullLength',
    'worldVerticesLength',
    'edgesCount',
    'edges',
    'width',
    'height',
    'rendererObject',
    'regionOffsetX',
    'regionOffsetY',
    'regionWidth',
    'regionHeight',
    'regionOriginalWidth',
    'regionOriginalHeight',
    'regionU',
    'regionV',
    'regionU2',
    'regionV2',
    'regionRotate',
    'regionDegrees',
    'parentMesh',
]
struct_spMeshAttachment._fields_ = [
    ('super', spVertexAttachment),
    ('path', String),
    ('regionUVs', POINTER(c_float)),
    ('uvs', POINTER(c_float)),
    ('trianglesCount', c_int),
    ('triangles', POINTER(c_ushort)),
    ('r', c_float),
    ('g', c_float),
    ('b', c_float),
    ('a', c_float),
    ('hullLength', c_int),
    ('worldVerticesLength', c_int),
    ('edgesCount', c_int),
    ('edges', POINTER(c_int)),
    ('width', c_int),
    ('height', c_int),
    ('rendererObject', POINTER(None)),
    ('regionOffsetX', c_int),
    ('regionOffsetY', c_int),
    ('regionWidth', c_int),
    ('regionHeight', c_int),
    ('regionOriginalWidth', c_int),
    ('regionOriginalHeight', c_int),
    ('regionU', c_float),
    ('regionV', c_float),
    ('regionU2', c_float),
    ('regionV2', c_float),
    ('regionRotate', c_int),
    ('regionDegrees', c_int),
    ('parentMesh', POINTER(struct_spMeshAttachment)),
]

spMeshAttachment = struct_spMeshAttachment# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 215

struct_spPointAttachment.__slots__ = [
    'super',
    'x',
    'y',
    'rotation',
    'color',
]
struct_spPointAttachment._fields_ = [
    ('super', spAttachment),
    ('x', c_float),
    ('y', c_float),
    ('rotation', c_float),
    ('color', spColor),
]

spPointAttachment = struct_spPointAttachment# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 221

struct_spClippingAttachment.__slots__ = [
    'super',
    'endSlot',
]
struct_spClippingAttachment._fields_ = [
    ('super', spVertexAttachment),
    ('endSlot', POINTER(struct_spSlotData)),
]

spClippingAttachment = struct_spClippingAttachment# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 226

struct_spPathAttachment.__slots__ = [
    'super',
    'lengthsLength',
    'lengths',
    'closed',
    'constantSpeed',
]
struct_spPathAttachment._fields_ = [
    ('super', spVertexAttachment),
    ('lengthsLength', c_int),
    ('lengths', POINTER(c_float)),
    ('closed', c_int),
    ('constantSpeed', c_int),
]

spPathAttachment = struct_spPathAttachment# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 233

struct_spBoundingBoxAttachment.__slots__ = [
    'super',
]
struct_spBoundingBoxAttachment._fields_ = [
    ('super', spVertexAttachment),
]

spBoundingBoxAttachment = struct_spBoundingBoxAttachment# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 237

struct_spBoneData.__slots__ = [
    'index',
    'name',
    'parent',
    'length',
    'x',
    'y',
    'rotation',
    'scaleX',
    'scaleY',
    'shearX',
    'shearY',
    'transformMode',
    'skinRequired',
]
struct_spBoneData._fields_ = [
    ('index', c_int),
    ('name', String),
    ('parent', POINTER(struct_spBoneData)),
    ('length', c_float),
    ('x', c_float),
    ('y', c_float),
    ('rotation', c_float),
    ('scaleX', c_float),
    ('scaleY', c_float),
    ('shearX', c_float),
    ('shearY', c_float),
    ('transformMode', c_int),
    ('skinRequired', c_int),
]

spBoneData = struct_spBoneData# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 247

struct_spSlotData.__slots__ = [
    'index',
    'name',
    'boneData',
    'attachmentName',
    'color',
    'darkColor',
    'blendMode',
]
struct_spSlotData._fields_ = [
    ('index', c_int),
    ('name', String),
    ('boneData', POINTER(struct_spBoneData)),
    ('attachmentName', String),
    ('color', spColor),
    ('darkColor', POINTER(spColor)),
    ('blendMode', c_int),
]

spSlotData = struct_spSlotData# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 257

struct_spEventData.__slots__ = [
    'name',
    'intValue',
    'floatValue',
    'stringValue',
    'audioPath',
    'volume',
    'balance',
]
struct_spEventData._fields_ = [
    ('name', String),
    ('intValue', c_int),
    ('floatValue', c_float),
    ('stringValue', String),
    ('audioPath', String),
    ('volume', c_float),
    ('balance', c_float),
]

spEventData = struct_spEventData# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 267

struct_spEvent.__slots__ = [
    'data',
    'time',
    'intValue',
    'floatValue',
    'stringValue',
    'volume',
    'balance',
]
struct_spEvent._fields_ = [
    ('data', POINTER(spEventData)),
    ('time', c_float),
    ('intValue', c_int),
    ('floatValue', c_float),
    ('stringValue', String),
    ('volume', c_float),
    ('balance', c_float),
]

spEvent = struct_spEvent# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 277

struct_spTimeline.__slots__ = [
    'propertyId',
    'apply',
]
struct_spTimeline._fields_ = [
    ('propertyId', c_int),
    ('apply', CFUNCTYPE(UNCHECKED(None), POINTER(None), c_float, c_float, POINTER(c_float), c_float, c_float, c_int, c_int, POINTER(None))),
]

spTimeline = struct_spTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 282

struct_spCurveTimeline.__slots__ = [
    'super',
    'curves',
]
struct_spCurveTimeline._fields_ = [
    ('super', spTimeline),
    ('curves', POINTER(c_float)),
]

spCurveTimeline = struct_spCurveTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 287

struct_spBaseTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'boneIndex',
]
struct_spBaseTimeline._fields_ = [
    ('super', spCurveTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('boneIndex', c_int),
]

spBaseTimeline = struct_spBaseTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 294

struct_spColorTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'slotIndex',
]
struct_spColorTimeline._fields_ = [
    ('super', spCurveTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('slotIndex', c_int),
]

spColorTimeline = struct_spColorTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 301

struct_spTwoColorTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'slotIndex',
]
struct_spTwoColorTimeline._fields_ = [
    ('super', spCurveTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('slotIndex', c_int),
]

spTwoColorTimeline = struct_spTwoColorTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 308

struct_spAttachmentTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'slotIndex',
    'attachmentNames',
]
struct_spAttachmentTimeline._fields_ = [
    ('super', spTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('slotIndex', c_int),
    ('attachmentNames', POINTER(POINTER(c_char))),
]

spAttachmentTimeline = struct_spAttachmentTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 316

struct_spEventTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'events',
]
struct_spEventTimeline._fields_ = [
    ('super', spTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('events', POINTER(POINTER(spEvent))),
]

spEventTimeline = struct_spEventTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 323

struct_spDrawOrderTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'drawOrders',
    'slotsCount',
]
struct_spDrawOrderTimeline._fields_ = [
    ('super', spTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('drawOrders', POINTER(POINTER(c_int))),
    ('slotsCount', c_int),
]

spDrawOrderTimeline = struct_spDrawOrderTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 331

struct_spDeformTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'frameVerticesCount',
    'frameVertices',
    'slotIndex',
    'attachment',
]
struct_spDeformTimeline._fields_ = [
    ('super', spCurveTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('frameVerticesCount', c_int),
    ('frameVertices', POINTER(POINTER(c_float))),
    ('slotIndex', c_int),
    ('attachment', POINTER(spAttachment)),
]

spDeformTimeline = struct_spDeformTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 341

struct_spIkConstraintTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'ikConstraintIndex',
]
struct_spIkConstraintTimeline._fields_ = [
    ('super', spCurveTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('ikConstraintIndex', c_int),
]

spIkConstraintTimeline = struct_spIkConstraintTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 348

struct_spTransformConstraintTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'transformConstraintIndex',
]
struct_spTransformConstraintTimeline._fields_ = [
    ('super', spCurveTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('transformConstraintIndex', c_int),
]

spTransformConstraintTimeline = struct_spTransformConstraintTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 355

struct_spPathConstraintPositionTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'pathConstraintIndex',
]
struct_spPathConstraintPositionTimeline._fields_ = [
    ('super', spCurveTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('pathConstraintIndex', c_int),
]

spPathConstraintPositionTimeline = struct_spPathConstraintPositionTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 362

struct_spPathConstraintSpacingTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'pathConstraintIndex',
]
struct_spPathConstraintSpacingTimeline._fields_ = [
    ('super', spCurveTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('pathConstraintIndex', c_int),
]

spPathConstraintSpacingTimeline = struct_spPathConstraintSpacingTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 369

struct_spPathConstraintMixTimeline.__slots__ = [
    'super',
    'framesCount',
    'frames',
    'pathConstraintIndex',
]
struct_spPathConstraintMixTimeline._fields_ = [
    ('super', spCurveTimeline),
    ('framesCount', c_int),
    ('frames', POINTER(c_float)),
    ('pathConstraintIndex', c_int),
]

spPathConstraintMixTimeline = struct_spPathConstraintMixTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 376

struct_spAnimation.__slots__ = [
    'name',
    'duration',
    'timelinesCount',
    'timelines',
]
struct_spAnimation._fields_ = [
    ('name', String),
    ('duration', c_float),
    ('timelinesCount', c_int),
    ('timelines', POINTER(POINTER(spTimeline))),
]

spAnimation = struct_spAnimation# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 383

struct_spBone.__slots__ = [
    'data',
    'skeleton',
    'parent',
    'childrenCount',
    'children',
    'x',
    'y',
    'rotation',
    'scaleX',
    'scaleY',
    'shearX',
    'shearY',
    'ax',
    'ay',
    'arotation',
    'ascaleX',
    'ascaleY',
    'ashearX',
    'ashearY',
    'appliedValid',
    'a',
    'b',
    'worldX',
    'c',
    'd',
    'worldY',
    'sorted',
    'active',
]
struct_spBone._fields_ = [
    ('data', POINTER(spBoneData)),
    ('skeleton', POINTER(struct_spSkeleton)),
    ('parent', POINTER(struct_spBone)),
    ('childrenCount', c_int),
    ('children', POINTER(POINTER(struct_spBone))),
    ('x', c_float),
    ('y', c_float),
    ('rotation', c_float),
    ('scaleX', c_float),
    ('scaleY', c_float),
    ('shearX', c_float),
    ('shearY', c_float),
    ('ax', c_float),
    ('ay', c_float),
    ('arotation', c_float),
    ('ascaleX', c_float),
    ('ascaleY', c_float),
    ('ashearX', c_float),
    ('ashearY', c_float),
    ('appliedValid', c_int),
    ('a', c_float),
    ('b', c_float),
    ('worldX', c_float),
    ('c', c_float),
    ('d', c_float),
    ('worldY', c_float),
    ('sorted', c_int),
    ('active', c_int),
]

spBone = struct_spBone# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 398

struct_spSlot.__slots__ = [
    'data',
    'bone',
    'color',
    'darkColor',
    'attachment',
    'attachmentState',
    'deformCapacity',
    'deformCount',
    'deform',
]
struct_spSlot._fields_ = [
    ('data', POINTER(spSlotData)),
    ('bone', POINTER(struct_spBone)),
    ('color', spColor),
    ('darkColor', POINTER(spColor)),
    ('attachment', POINTER(spAttachment)),
    ('attachmentState', c_int),
    ('deformCapacity', c_int),
    ('deformCount', c_int),
    ('deform', POINTER(c_float)),
]

spSlot = struct_spSlot# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 410

struct_spPathConstraintData.__slots__ = [
    'name',
    'order',
    'skinRequired',
    'bonesCount',
    'bones',
    'target',
    'positionMode',
    'spacingMode',
    'rotateMode',
    'offsetRotation',
    'position',
    'spacing',
    'rotateMix',
    'translateMix',
]
struct_spPathConstraintData._fields_ = [
    ('name', String),
    ('order', c_int),
    ('skinRequired', c_int),
    ('bonesCount', c_int),
    ('bones', POINTER(POINTER(spBoneData))),
    ('target', POINTER(struct_spSlotData)),
    ('positionMode', c_int),
    ('spacingMode', c_int),
    ('rotateMode', c_int),
    ('offsetRotation', c_float),
    ('position', c_float),
    ('spacing', c_float),
    ('rotateMix', c_float),
    ('translateMix', c_float),
]

spPathConstraintData = struct_spPathConstraintData# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 424

struct_spPathConstraint.__slots__ = [
    'data',
    'bonesCount',
    'bones',
    'target',
    'position',
    'spacing',
    'rotateMix',
    'translateMix',
    'spacesCount',
    'spaces',
    'positionsCount',
    'positions',
    'worldCount',
    'world',
    'curvesCount',
    'curves',
    'lengthsCount',
    'lengths',
    'segments',
    'active',
]
struct_spPathConstraint._fields_ = [
    ('data', POINTER(spPathConstraintData)),
    ('bonesCount', c_int),
    ('bones', POINTER(POINTER(struct_spBone))),
    ('target', POINTER(struct_spSlot)),
    ('position', c_float),
    ('spacing', c_float),
    ('rotateMix', c_float),
    ('translateMix', c_float),
    ('spacesCount', c_int),
    ('spaces', POINTER(c_float)),
    ('positionsCount', c_int),
    ('positions', POINTER(c_float)),
    ('worldCount', c_int),
    ('world', POINTER(c_float)),
    ('curvesCount', c_int),
    ('curves', POINTER(c_float)),
    ('lengthsCount', c_int),
    ('lengths', POINTER(c_float)),
    ('segments', c_float * int(10)),
    ('active', c_int),
]

spPathConstraint = struct_spPathConstraint# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 444

struct_spTransformConstraintData.__slots__ = [
    'name',
    'order',
    'skinRequired',
    'bonesCount',
    'bones',
    'target',
    'rotateMix',
    'translateMix',
    'scaleMix',
    'shearMix',
    'offsetRotation',
    'offsetX',
    'offsetY',
    'offsetScaleX',
    'offsetScaleY',
    'offsetShearY',
    'relative',
    'local',
]
struct_spTransformConstraintData._fields_ = [
    ('name', String),
    ('order', c_int),
    ('skinRequired', c_int),
    ('bonesCount', c_int),
    ('bones', POINTER(POINTER(spBoneData))),
    ('target', POINTER(spBoneData)),
    ('rotateMix', c_float),
    ('translateMix', c_float),
    ('scaleMix', c_float),
    ('shearMix', c_float),
    ('offsetRotation', c_float),
    ('offsetX', c_float),
    ('offsetY', c_float),
    ('offsetScaleX', c_float),
    ('offsetScaleY', c_float),
    ('offsetShearY', c_float),
    ('relative', c_int),
    ('local', c_int),
]

spTransformConstraintData = struct_spTransformConstraintData# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 457

struct_spTransformConstraint.__slots__ = [
    'data',
    'bonesCount',
    'bones',
    'target',
    'rotateMix',
    'translateMix',
    'scaleMix',
    'shearMix',
    'active',
]
struct_spTransformConstraint._fields_ = [
    ('data', POINTER(spTransformConstraintData)),
    ('bonesCount', c_int),
    ('bones', POINTER(POINTER(struct_spBone))),
    ('target', POINTER(struct_spBone)),
    ('rotateMix', c_float),
    ('translateMix', c_float),
    ('scaleMix', c_float),
    ('shearMix', c_float),
    ('active', c_int),
]

spTransformConstraint = struct_spTransformConstraint# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 466

struct_spIkConstraintData.__slots__ = [
    'name',
    'order',
    'skinRequired',
    'bonesCount',
    'bones',
    'target',
    'bendDirection',
    'compress',
    'stretch',
    'uniform',
    'mix',
    'softness',
]
struct_spIkConstraintData._fields_ = [
    ('name', String),
    ('order', c_int),
    ('skinRequired', c_int),
    ('bonesCount', c_int),
    ('bones', POINTER(POINTER(spBoneData))),
    ('target', POINTER(spBoneData)),
    ('bendDirection', c_int),
    ('compress', c_int),
    ('stretch', c_int),
    ('uniform', c_int),
    ('mix', c_float),
    ('softness', c_float),
]

spIkConstraintData = struct_spIkConstraintData# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 481

struct_spIkConstraint.__slots__ = [
    'data',
    'bonesCount',
    'bones',
    'target',
    'bendDirection',
    'compress',
    'stretch',
    'mix',
    'softness',
    'active',
]
struct_spIkConstraint._fields_ = [
    ('data', POINTER(spIkConstraintData)),
    ('bonesCount', c_int),
    ('bones', POINTER(POINTER(struct_spBone))),
    ('target', POINTER(struct_spBone)),
    ('bendDirection', c_int),
    ('compress', c_int),
    ('stretch', c_int),
    ('mix', c_float),
    ('softness', c_float),
    ('active', c_int),
]

spIkConstraint = struct_spIkConstraint# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 494

struct_spSkeleton.__slots__ = [
    'data',
    'bonesCount',
    'bones',
    'root',
    'slotsCount',
    'slots',
    'drawOrder',
    'ikConstraintsCount',
    'ikConstraints',
    'transformConstraintsCount',
    'transformConstraints',
    'pathConstraintsCount',
    'pathConstraints',
    'skin',
    'color',
    'time',
    'scaleX',
    'scaleY',
    'x',
    'y',
]
struct_spSkeleton._fields_ = [
    ('data', POINTER(struct_spSkeletonData)),
    ('bonesCount', c_int),
    ('bones', POINTER(POINTER(struct_spBone))),
    ('root', POINTER(struct_spBone)),
    ('slotsCount', c_int),
    ('slots', POINTER(POINTER(struct_spSlot))),
    ('drawOrder', POINTER(POINTER(struct_spSlot))),
    ('ikConstraintsCount', c_int),
    ('ikConstraints', POINTER(POINTER(struct_spIkConstraint))),
    ('transformConstraintsCount', c_int),
    ('transformConstraints', POINTER(POINTER(struct_spTransformConstraint))),
    ('pathConstraintsCount', c_int),
    ('pathConstraints', POINTER(POINTER(struct_spPathConstraint))),
    ('skin', POINTER(struct_spSkin)),
    ('color', spColor),
    ('time', c_float),
    ('scaleX', c_float),
    ('scaleY', c_float),
    ('x', c_float),
    ('y', c_float),
]

spSkeleton = struct_spSkeleton# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 515

struct_spAttachmentLoader.__slots__ = [
    'error1',
    'error2',
    'vtable',
]
struct_spAttachmentLoader._fields_ = [
    ('error1', String),
    ('error2', String),
    ('vtable', POINTER(None)),
]

spAttachmentLoader = struct_spAttachmentLoader# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 521

struct_spAtlasAttachmentLoader.__slots__ = [
    'super',
    'atlas',
]
struct_spAtlasAttachmentLoader._fields_ = [
    ('super', spAttachmentLoader),
    ('atlas', POINTER(struct_spAtlas)),
]

spAtlasAttachmentLoader = struct_spAtlasAttachmentLoader# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 526

struct__Entry.__slots__ = [
    'slotIndex',
    'name',
    'attachment',
    'next',
]
struct__Entry._fields_ = [
    ('slotIndex', c_int),
    ('name', String),
    ('attachment', POINTER(spAttachment)),
    ('next', POINTER(struct__Entry)),
]

_Entry = struct__Entry# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 533

struct__SkinHashTableEntry.__slots__ = [
    'entry',
    'next',
]
struct__SkinHashTableEntry._fields_ = [
    ('entry', POINTER(_Entry)),
    ('next', POINTER(struct__SkinHashTableEntry)),
]

_SkinHashTableEntry = struct__SkinHashTableEntry# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 538

struct_spSkin.__slots__ = [
    'name',
    'bones',
    'ikConstraints',
    'transformConstraints',
    'pathConstraints',
]
struct_spSkin._fields_ = [
    ('name', String),
    ('bones', POINTER(struct_spBoneDataArray)),
    ('ikConstraints', POINTER(struct_spIkConstraintDataArray)),
    ('transformConstraints', POINTER(struct_spTransformConstraintDataArray)),
    ('pathConstraints', POINTER(struct_spPathConstraintDataArray)),
]

spSkin = struct_spSkin# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 546

struct__spSkin.__slots__ = [
    'super',
    'entries',
    'entriesHashTable',
]
struct__spSkin._fields_ = [
    ('super', struct_spSkin),
    ('entries', POINTER(_Entry)),
    ('entriesHashTable', POINTER(_SkinHashTableEntry) * int(101)),
]

_spSkin = struct__spSkin# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 552

struct_spVertexEffect.__slots__ = [
    'begin',
    'transform',
    'end',
]
struct_spVertexEffect._fields_ = [
    ('begin', CFUNCTYPE(UNCHECKED(None), POINTER(None))),
    ('transform', CFUNCTYPE(UNCHECKED(None), POINTER(None), POINTER(c_float), c_int)),
    ('end', CFUNCTYPE(UNCHECKED(None), POINTER(None))),
]

spVertexEffect = struct_spVertexEffect# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 558

struct_spJitterVertexEffect.__slots__ = [
    'super',
    'jitterX',
    'jitterY',
]
struct_spJitterVertexEffect._fields_ = [
    ('super', spVertexEffect),
    ('jitterX', c_float),
    ('jitterY', c_float),
]

spJitterVertexEffect = struct_spJitterVertexEffect# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 564

struct_spSwirlVertexEffect.__slots__ = [
    'super',
    'centerX',
    'centerY',
    'radius',
    'angle',
    'worldX',
    'worldY',
]
struct_spSwirlVertexEffect._fields_ = [
    ('super', spVertexEffect),
    ('centerX', c_float),
    ('centerY', c_float),
    ('radius', c_float),
    ('angle', c_float),
    ('worldX', c_float),
    ('worldY', c_float),
]

spSwirlVertexEffect = struct_spSwirlVertexEffect# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 574

struct_spSkeletonData.__slots__ = [
    'version',
    'hash',
    'x',
    'y',
    'width',
    'height',
    'stringsCount',
    'strings',
    'bonesCount',
    'bones',
    'slotsCount',
    'slots',
    'skinsCount',
    'skins',
    'defaultSkin',
    'eventsCount',
    'events',
    'animationsCount',
    'animations',
    'ikConstraintsCount',
    'ikConstraints',
    'transformConstraintsCount',
    'transformConstraints',
    'pathConstraintsCount',
    'pathConstraints',
]
struct_spSkeletonData._fields_ = [
    ('version', String),
    ('hash', String),
    ('x', c_float),
    ('y', c_float),
    ('width', c_float),
    ('height', c_float),
    ('stringsCount', c_int),
    ('strings', POINTER(POINTER(c_char))),
    ('bonesCount', c_int),
    ('bones', POINTER(POINTER(struct_spBoneData))),
    ('slotsCount', c_int),
    ('slots', POINTER(POINTER(struct_spSlotData))),
    ('skinsCount', c_int),
    ('skins', POINTER(POINTER(struct_spSkin))),
    ('defaultSkin', POINTER(struct_spSkin)),
    ('eventsCount', c_int),
    ('events', POINTER(POINTER(struct_spEventData))),
    ('animationsCount', c_int),
    ('animations', POINTER(POINTER(struct_spAnimation))),
    ('ikConstraintsCount', c_int),
    ('ikConstraints', POINTER(POINTER(struct_spIkConstraintData))),
    ('transformConstraintsCount', c_int),
    ('transformConstraints', POINTER(POINTER(struct_spTransformConstraintData))),
    ('pathConstraintsCount', c_int),
    ('pathConstraints', POINTER(POINTER(struct_spPathConstraintData))),
]

spSkeletonData = struct_spSkeletonData# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 599

struct_spSkeletonJson.__slots__ = [
    'scale',
    'attachmentLoader',
    'error',
]
struct_spSkeletonJson._fields_ = [
    ('scale', c_float),
    ('attachmentLoader', POINTER(struct_spAttachmentLoader)),
    ('error', String),
]

spSkeletonJson = struct_spSkeletonJson# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 605

struct_spSkeletonBinary.__slots__ = [
    'scale',
    'attachmentLoader',
    'error',
]
struct_spSkeletonBinary._fields_ = [
    ('scale', c_float),
    ('attachmentLoader', POINTER(struct_spAttachmentLoader)),
    ('error', String),
]

spSkeletonBinary = struct_spSkeletonBinary# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 611

struct_spAnimationStateData.__slots__ = [
    'skeletonData',
    'defaultMix',
    'entries',
]
struct_spAnimationStateData._fields_ = [
    ('skeletonData', POINTER(struct_spSkeletonData)),
    ('defaultMix', c_float),
    ('entries', POINTER(None)),
]

spAnimationStateData = struct_spAnimationStateData# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 617

struct_spPolygon.__slots__ = [
    'vertices',
    'count',
    'capacity',
]
struct_spPolygon._fields_ = [
    ('vertices', POINTER(c_float)),
    ('count', c_int),
    ('capacity', c_int),
]

spPolygon = struct_spPolygon# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 623

struct_spSkeletonBounds.__slots__ = [
    'count',
    'boundingBoxes',
    'polygons',
    'minX',
    'minY',
    'maxX',
    'maxY',
]
struct_spSkeletonBounds._fields_ = [
    ('count', c_int),
    ('boundingBoxes', POINTER(POINTER(struct_spBoundingBoxAttachment))),
    ('polygons', POINTER(POINTER(struct_spPolygon))),
    ('minX', c_float),
    ('minY', c_float),
    ('maxX', c_float),
    ('maxY', c_float),
]

spSkeletonBounds = struct_spSkeletonBounds# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 630

struct_spTriangulator.__slots__ = [
    'convexPolygons',
    'convexPolygonsIndices',
    'indicesArray',
    'isConcaveArray',
    'triangles',
    'polygonPool',
    'polygonIndicesPool',
]
struct_spTriangulator._fields_ = [
    ('convexPolygons', POINTER(struct_spArrayFloatArray)),
    ('convexPolygonsIndices', POINTER(struct_spArrayShortArray)),
    ('indicesArray', POINTER(struct_spShortArray)),
    ('isConcaveArray', POINTER(struct_spIntArray)),
    ('triangles', POINTER(struct_spShortArray)),
    ('polygonPool', POINTER(struct_spArrayFloatArray)),
    ('polygonIndicesPool', POINTER(struct_spArrayShortArray)),
]

spTriangulator = struct_spTriangulator# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 640

struct_spSkeletonClipping.__slots__ = [
    'triangulator',
    'clippingPolygon',
    'clipOutput',
    'clippedVertices',
    'clippedUVs',
    'clippedTriangles',
    'scratch',
    'clipAttachment',
    'clippingPolygons',
]
struct_spSkeletonClipping._fields_ = [
    ('triangulator', POINTER(struct_spTriangulator)),
    ('clippingPolygon', POINTER(struct_spFloatArray)),
    ('clipOutput', POINTER(struct_spFloatArray)),
    ('clippedVertices', POINTER(struct_spFloatArray)),
    ('clippedUVs', POINTER(struct_spFloatArray)),
    ('clippedTriangles', POINTER(struct_spUnsignedShortArray)),
    ('scratch', POINTER(struct_spFloatArray)),
    ('clipAttachment', POINTER(struct_spClippingAttachment)),
    ('clippingPolygons', POINTER(struct_spArrayFloatArray)),
]

spSkeletonClipping = struct_spSkeletonClipping# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 652

spAnimationState = struct_spAnimationState# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 654

spTrackEntry = struct_spTrackEntry# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 655

spAnimationStateListener = CFUNCTYPE(UNCHECKED(None), POINTER(struct_spAnimationState), c_int, POINTER(struct_spTrackEntry), POINTER(struct_spEvent))# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 657

struct_spTrackEntry.__slots__ = [
    'animation',
    'next',
    'mixingFrom',
    'mixingTo',
    'listener',
    'trackIndex',
    'loop',
    'holdPrevious',
    'eventThreshold',
    'attachmentThreshold',
    'drawOrderThreshold',
    'animationStart',
    'animationEnd',
    'animationLast',
    'nextAnimationLast',
    'delay',
    'trackTime',
    'trackLast',
    'nextTrackLast',
    'trackEnd',
    'timeScale',
    'alpha',
    'mixTime',
    'mixDuration',
    'interruptAlpha',
    'totalAlpha',
    'mixBlend',
    'timelineMode',
    'timelineHoldMix',
    'timelinesRotation',
    'timelinesRotationCount',
    'rendererObject',
    'userData',
]
struct_spTrackEntry._fields_ = [
    ('animation', POINTER(struct_spAnimation)),
    ('next', POINTER(struct_spTrackEntry)),
    ('mixingFrom', POINTER(struct_spTrackEntry)),
    ('mixingTo', POINTER(struct_spTrackEntry)),
    ('listener', spAnimationStateListener),
    ('trackIndex', c_int),
    ('loop', c_int),
    ('holdPrevious', c_int),
    ('eventThreshold', c_float),
    ('attachmentThreshold', c_float),
    ('drawOrderThreshold', c_float),
    ('animationStart', c_float),
    ('animationEnd', c_float),
    ('animationLast', c_float),
    ('nextAnimationLast', c_float),
    ('delay', c_float),
    ('trackTime', c_float),
    ('trackLast', c_float),
    ('nextTrackLast', c_float),
    ('trackEnd', c_float),
    ('timeScale', c_float),
    ('alpha', c_float),
    ('mixTime', c_float),
    ('mixDuration', c_float),
    ('interruptAlpha', c_float),
    ('totalAlpha', c_float),
    ('mixBlend', c_int),
    ('timelineMode', POINTER(struct_spIntArray)),
    ('timelineHoldMix', POINTER(struct_spTrackEntryArray)),
    ('timelinesRotation', POINTER(c_float)),
    ('timelinesRotationCount', c_int),
    ('rendererObject', POINTER(None)),
    ('userData', POINTER(None)),
]

enum_spAttachmentType = c_int# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 695

SP_ATTACHMENT_REGION = 0# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 695

SP_ATTACHMENT_BOUNDING_BOX = (SP_ATTACHMENT_REGION + 1)# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 695

SP_ATTACHMENT_MESH = (SP_ATTACHMENT_BOUNDING_BOX + 1)# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 695

SP_ATTACHMENT_LINKED_MESH = (SP_ATTACHMENT_MESH + 1)# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 695

SP_ATTACHMENT_PATH = (SP_ATTACHMENT_LINKED_MESH + 1)# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 695

SP_ATTACHMENT_POINT = (SP_ATTACHMENT_PATH + 1)# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 695

SP_ATTACHMENT_CLIPPING = (SP_ATTACHMENT_POINT + 1)# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 695

spAttachmentType = enum_spAttachmentType# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 695

enum_spAtlasFormat = c_int# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 706

SP_ATLAS_UNKNOWN_FORMAT = 0# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 706

SP_ATLAS_ALPHA = (SP_ATLAS_UNKNOWN_FORMAT + 1)# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 706

SP_ATLAS_INTENSITY = (SP_ATLAS_ALPHA + 1)# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 706

SP_ATLAS_LUMINANCE_ALPHA = (SP_ATLAS_INTENSITY + 1)# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 706

SP_ATLAS_RGB565 = (SP_ATLAS_LUMINANCE_ALPHA + 1)# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 706

SP_ATLAS_RGBA4444 = (SP_ATLAS_RGB565 + 1)# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 706

SP_ATLAS_RGB888 = (SP_ATLAS_RGBA4444 + 1)# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 706

SP_ATLAS_RGBA8888 = (SP_ATLAS_RGB888 + 1)# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 706

spAtlasFormat = enum_spAtlasFormat# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 706

enum_anon_1 = c_int# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 711

SP_MIX_DIRECTION_IN = 0# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 711

SP_MIX_DIRECTION_OUT = (SP_MIX_DIRECTION_IN + 1)# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 711

spMixDirection = enum_anon_1# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 711

CreateTextureCallback = CFUNCTYPE(UNCHECKED(None), POINTER(struct_spAtlasPage), String)# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 713

DisposeTextureCallback = CFUNCTYPE(UNCHECKED(None), POINTER(struct_spAtlasPage))# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 714

spTimelineApplyFunc = CFUNCTYPE(UNCHECKED(None), POINTER(None), c_float, c_float, POINTER(c_float), c_float, c_float, c_int, c_int, POINTER(None))# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 715

spVertexEffectBeginFunc = CFUNCTYPE(UNCHECKED(None), POINTER(None))# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 716

spVertexEffectTransformFunc = CFUNCTYPE(UNCHECKED(None), POINTER(None), POINTER(c_float), c_int)# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 717

spVertexEffectEndFunc = CFUNCTYPE(UNCHECKED(None), POINTER(None))# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 718

struct_spAtlasPage.__slots__ = [
    'atlas',
    'name',
    'format',
    'minFilter',
    'magFilter',
    'uWrap',
    'vWrap',
    'rendererObject',
    'width',
    'height',
    'next',
]
struct_spAtlasPage._fields_ = [
    ('atlas', POINTER(struct_spAtlas)),
    ('name', String),
    ('format', spAtlasFormat),
    ('minFilter', c_int),
    ('magFilter', c_int),
    ('uWrap', c_int),
    ('vWrap', c_int),
    ('rendererObject', POINTER(None)),
    ('width', c_int),
    ('height', c_int),
    ('next', POINTER(struct_spAtlasPage)),
]

spAtlasPage = struct_spAtlasPage# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 730

struct_spAtlasRegion.__slots__ = [
    'name',
    'x',
    'y',
    'width',
    'height',
    'u',
    'v',
    'u2',
    'v2',
    'offsetX',
    'offsetY',
    'originalWidth',
    'originalHeight',
    'index',
    'rotate',
    'degrees',
    'flip',
    'splits',
    'pads',
    'page',
    'next',
]
struct_spAtlasRegion._fields_ = [
    ('name', String),
    ('x', c_int),
    ('y', c_int),
    ('width', c_int),
    ('height', c_int),
    ('u', c_float),
    ('v', c_float),
    ('u2', c_float),
    ('v2', c_float),
    ('offsetX', c_int),
    ('offsetY', c_int),
    ('originalWidth', c_int),
    ('originalHeight', c_int),
    ('index', c_int),
    ('rotate', c_int),
    ('degrees', c_int),
    ('flip', c_int),
    ('splits', POINTER(c_int)),
    ('pads', POINTER(c_int)),
    ('page', POINTER(struct_spAtlasPage)),
    ('next', POINTER(struct_spAtlasRegion)),
]

spAtlasRegion = struct_spAtlasRegion# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 746

struct_spAtlas.__slots__ = [
    'regions',
    'regionsCount',
    'pages',
    'pagesCount',
    'rendererObject',
    'error',
]
struct_spAtlas._fields_ = [
    ('regions', POINTER(struct_spAtlasRegion)),
    ('regionsCount', c_int),
    ('pages', POINTER(struct_spAtlasPage)),
    ('pagesCount', c_int),
    ('rendererObject', POINTER(None)),
    ('error', String),
]

spAtlas = struct_spAtlas# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 755

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 758
if _libs["spine"].has("spAtlas_createFromFile", "cdecl"):
    spAtlas_createFromFile = _libs["spine"].get("spAtlas_createFromFile", "cdecl")
    spAtlas_createFromFile.argtypes = [String, POINTER(None)]
    spAtlas_createFromFile.restype = POINTER(struct_spAtlas)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 759
if _libs["spine"].has("spAtlas_dispose", "cdecl"):
    spAtlas_dispose = _libs["spine"].get("spAtlas_dispose", "cdecl")
    spAtlas_dispose.argtypes = [POINTER(struct_spAtlas)]
    spAtlas_dispose.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 760
if _libs["spine"].has("spAtlasPage_set_createTexture", "cdecl"):
    spAtlasPage_set_createTexture = _libs["spine"].get("spAtlasPage_set_createTexture", "cdecl")
    spAtlasPage_set_createTexture.argtypes = [CreateTextureCallback]
    spAtlasPage_set_createTexture.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 761
if _libs["spine"].has("spAtlasPage_set_disposeTexture", "cdecl"):
    spAtlasPage_set_disposeTexture = _libs["spine"].get("spAtlasPage_set_disposeTexture", "cdecl")
    spAtlasPage_set_disposeTexture.argtypes = [DisposeTextureCallback]
    spAtlasPage_set_disposeTexture.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 762
if _libs["spine"].has("spAtlasAttachmentLoader_create", "cdecl"):
    spAtlasAttachmentLoader_create = _libs["spine"].get("spAtlasAttachmentLoader_create", "cdecl")
    spAtlasAttachmentLoader_create.argtypes = [POINTER(struct_spAtlas)]
    spAtlasAttachmentLoader_create.restype = POINTER(struct_spAttachmentLoader)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 763
if _libs["spine"].has("spAttachmentLoader_dispose", "cdecl"):
    spAttachmentLoader_dispose = _libs["spine"].get("spAttachmentLoader_dispose", "cdecl")
    spAttachmentLoader_dispose.argtypes = [POINTER(struct_spAttachmentLoader)]
    spAttachmentLoader_dispose.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 764
if _libs["spine"].has("spSkeletonJson_create", "cdecl"):
    spSkeletonJson_create = _libs["spine"].get("spSkeletonJson_create", "cdecl")
    spSkeletonJson_create.argtypes = [POINTER(struct_spAtlas)]
    spSkeletonJson_create.restype = POINTER(struct_spSkeletonJson)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 765
if _libs["spine"].has("spSkeletonJson_createWithLoader", "cdecl"):
    spSkeletonJson_createWithLoader = _libs["spine"].get("spSkeletonJson_createWithLoader", "cdecl")
    spSkeletonJson_createWithLoader.argtypes = [POINTER(struct_spAttachmentLoader)]
    spSkeletonJson_createWithLoader.restype = POINTER(struct_spSkeletonJson)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 766
if _libs["spine"].has("spSkeletonJson_dispose", "cdecl"):
    spSkeletonJson_dispose = _libs["spine"].get("spSkeletonJson_dispose", "cdecl")
    spSkeletonJson_dispose.argtypes = [POINTER(struct_spSkeletonJson)]
    spSkeletonJson_dispose.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 767
if _libs["spine"].has("spSkeletonJson_readSkeletonDataFile", "cdecl"):
    spSkeletonJson_readSkeletonDataFile = _libs["spine"].get("spSkeletonJson_readSkeletonDataFile", "cdecl")
    spSkeletonJson_readSkeletonDataFile.argtypes = [POINTER(struct_spSkeletonJson), String]
    spSkeletonJson_readSkeletonDataFile.restype = POINTER(struct_spSkeletonData)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 768
for _lib in _libs.values():
    if not _lib.has("spSkeletonJson_setScale", "cdecl"):
        continue
    spSkeletonJson_setScale = _lib.get("spSkeletonJson_setScale", "cdecl")
    spSkeletonJson_setScale.argtypes = [POINTER(struct_spSkeletonJson), c_float]
    spSkeletonJson_setScale.restype = None
    break

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 769
if _libs["spine"].has("spSkeletonBinary_create", "cdecl"):
    spSkeletonBinary_create = _libs["spine"].get("spSkeletonBinary_create", "cdecl")
    spSkeletonBinary_create.argtypes = [POINTER(struct_spAtlas)]
    spSkeletonBinary_create.restype = POINTER(struct_spSkeletonBinary)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 770
if _libs["spine"].has("spSkeletonBinary_dispose", "cdecl"):
    spSkeletonBinary_dispose = _libs["spine"].get("spSkeletonBinary_dispose", "cdecl")
    spSkeletonBinary_dispose.argtypes = [POINTER(struct_spSkeletonBinary)]
    spSkeletonBinary_dispose.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 771
if _libs["spine"].has("spSkeletonBinary_readSkeletonDataFile", "cdecl"):
    spSkeletonBinary_readSkeletonDataFile = _libs["spine"].get("spSkeletonBinary_readSkeletonDataFile", "cdecl")
    spSkeletonBinary_readSkeletonDataFile.argtypes = [POINTER(struct_spSkeletonBinary), String]
    spSkeletonBinary_readSkeletonDataFile.restype = POINTER(struct_spSkeletonData)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 772
for _lib in _libs.values():
    if not _lib.has("spSkeletonBinary_setScale", "cdecl"):
        continue
    spSkeletonBinary_setScale = _lib.get("spSkeletonBinary_setScale", "cdecl")
    spSkeletonBinary_setScale.argtypes = [POINTER(struct_spSkeletonBinary), c_float]
    spSkeletonBinary_setScale.restype = None
    break

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 773
if _libs["spine"].has("spSkeleton_create", "cdecl"):
    spSkeleton_create = _libs["spine"].get("spSkeleton_create", "cdecl")
    spSkeleton_create.argtypes = [POINTER(struct_spSkeletonData)]
    spSkeleton_create.restype = POINTER(struct_spSkeleton)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 774
if _libs["spine"].has("spSkeleton_dispose", "cdecl"):
    spSkeleton_dispose = _libs["spine"].get("spSkeleton_dispose", "cdecl")
    spSkeleton_dispose.argtypes = [POINTER(struct_spSkeleton)]
    spSkeleton_dispose.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 775
if _libs["spine"].has("spSkeleton_update", "cdecl"):
    spSkeleton_update = _libs["spine"].get("spSkeleton_update", "cdecl")
    spSkeleton_update.argtypes = [POINTER(struct_spSkeleton), c_float]
    spSkeleton_update.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 776
if _libs["spine"].has("spSkeleton_setSkinByName", "cdecl"):
    spSkeleton_setSkinByName = _libs["spine"].get("spSkeleton_setSkinByName", "cdecl")
    spSkeleton_setSkinByName.argtypes = [POINTER(struct_spSkeleton), String]
    spSkeleton_setSkinByName.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 777
if _libs["spine"].has("spSkeleton_setToSetupPose", "cdecl"):
    spSkeleton_setToSetupPose = _libs["spine"].get("spSkeleton_setToSetupPose", "cdecl")
    spSkeleton_setToSetupPose.argtypes = [POINTER(struct_spSkeleton)]
    spSkeleton_setToSetupPose.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 778
if _libs["spine"].has("spSkeleton_updateWorldTransform", "cdecl"):
    spSkeleton_updateWorldTransform = _libs["spine"].get("spSkeleton_updateWorldTransform", "cdecl")
    spSkeleton_updateWorldTransform.argtypes = [POINTER(struct_spSkeleton)]
    spSkeleton_updateWorldTransform.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 779
if _libs["spine"].has("spSkeleton_setBonesToSetupPose", "cdecl"):
    spSkeleton_setBonesToSetupPose = _libs["spine"].get("spSkeleton_setBonesToSetupPose", "cdecl")
    spSkeleton_setBonesToSetupPose.argtypes = [POINTER(struct_spSkeleton)]
    spSkeleton_setBonesToSetupPose.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 780
if _libs["spine"].has("spSkeleton_setSlotsToSetupPose", "cdecl"):
    spSkeleton_setSlotsToSetupPose = _libs["spine"].get("spSkeleton_setSlotsToSetupPose", "cdecl")
    spSkeleton_setSlotsToSetupPose.argtypes = [POINTER(struct_spSkeleton)]
    spSkeleton_setSlotsToSetupPose.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 781
if _libs["spine"].has("spSkeleton_setAttachment", "cdecl"):
    spSkeleton_setAttachment = _libs["spine"].get("spSkeleton_setAttachment", "cdecl")
    spSkeleton_setAttachment.argtypes = [POINTER(struct_spSkeleton), String, String]
    spSkeleton_setAttachment.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 782
if _libs["spine"].has("spSkeleton_findBone", "cdecl"):
    spSkeleton_findBone = _libs["spine"].get("spSkeleton_findBone", "cdecl")
    spSkeleton_findBone.argtypes = [POINTER(struct_spSkeleton), String]
    spSkeleton_findBone.restype = POINTER(struct_spBone)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 783
if _libs["spine"].has("spSkeleton_findSlot", "cdecl"):
    spSkeleton_findSlot = _libs["spine"].get("spSkeleton_findSlot", "cdecl")
    spSkeleton_findSlot.argtypes = [POINTER(struct_spSkeleton), String]
    spSkeleton_findSlot.restype = POINTER(struct_spSlot)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 784
if _libs["spine"].has("spSkeleton_getAttachmentForSlotName", "cdecl"):
    spSkeleton_getAttachmentForSlotName = _libs["spine"].get("spSkeleton_getAttachmentForSlotName", "cdecl")
    spSkeleton_getAttachmentForSlotName.argtypes = [POINTER(struct_spSkeleton), String, String]
    spSkeleton_getAttachmentForSlotName.restype = POINTER(struct_spAttachment)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 785
if _libs["spine"].has("spSkeleton_getAttachmentForSlotIndex", "cdecl"):
    spSkeleton_getAttachmentForSlotIndex = _libs["spine"].get("spSkeleton_getAttachmentForSlotIndex", "cdecl")
    spSkeleton_getAttachmentForSlotIndex.argtypes = [POINTER(struct_spSkeleton), c_int, String]
    spSkeleton_getAttachmentForSlotIndex.restype = POINTER(struct_spAttachment)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 786
if _libs["spine"].has("spAnimationStateData_create", "cdecl"):
    spAnimationStateData_create = _libs["spine"].get("spAnimationStateData_create", "cdecl")
    spAnimationStateData_create.argtypes = [POINTER(struct_spSkeletonData)]
    spAnimationStateData_create.restype = POINTER(struct_spAnimationStateData)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 787
if _libs["spine"].has("spAnimationStateData_dispose", "cdecl"):
    spAnimationStateData_dispose = _libs["spine"].get("spAnimationStateData_dispose", "cdecl")
    spAnimationStateData_dispose.argtypes = [POINTER(struct_spAnimationStateData)]
    spAnimationStateData_dispose.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 788
if _libs["spine"].has("spAnimationState_create", "cdecl"):
    spAnimationState_create = _libs["spine"].get("spAnimationState_create", "cdecl")
    spAnimationState_create.argtypes = [POINTER(struct_spAnimationStateData)]
    spAnimationState_create.restype = POINTER(struct_spAnimationState)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 789
if _libs["spine"].has("spAnimationState_dispose", "cdecl"):
    spAnimationState_dispose = _libs["spine"].get("spAnimationState_dispose", "cdecl")
    spAnimationState_dispose.argtypes = [POINTER(struct_spAnimationState)]
    spAnimationState_dispose.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 790
if _libs["spine"].has("spAnimationState_update", "cdecl"):
    spAnimationState_update = _libs["spine"].get("spAnimationState_update", "cdecl")
    spAnimationState_update.argtypes = [POINTER(struct_spAnimationState), c_float]
    spAnimationState_update.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 791
if _libs["spine"].has("spAnimationState_apply", "cdecl"):
    spAnimationState_apply = _libs["spine"].get("spAnimationState_apply", "cdecl")
    spAnimationState_apply.argtypes = [POINTER(struct_spAnimationState), POINTER(struct_spSkeleton)]
    spAnimationState_apply.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 792
if _libs["spine"].has("spAnimationState_setAnimationByName", "cdecl"):
    spAnimationState_setAnimationByName = _libs["spine"].get("spAnimationState_setAnimationByName", "cdecl")
    spAnimationState_setAnimationByName.argtypes = [POINTER(struct_spAnimationState), c_int, String, c_int]
    spAnimationState_setAnimationByName.restype = c_int

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 793
if _libs["spine"].has("spAnimationState_addAnimationByName", "cdecl"):
    spAnimationState_addAnimationByName = _libs["spine"].get("spAnimationState_addAnimationByName", "cdecl")
    spAnimationState_addAnimationByName.argtypes = [POINTER(struct_spAnimationState), c_int, String, c_int, c_float]
    spAnimationState_addAnimationByName.restype = c_int

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 794
for _lib in _libs.values():
    if not _lib.has("spAnimationState_setListener", "cdecl"):
        continue
    spAnimationState_setListener = _lib.get("spAnimationState_setListener", "cdecl")
    spAnimationState_setListener.argtypes = [POINTER(struct_spAnimationState), spAnimationStateListener]
    spAnimationState_setListener.restype = None
    break

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 795
for _lib in _libs.values():
    if not _lib.has("spAnimationState_setVertexEffect", "cdecl"):
        continue
    spAnimationState_setVertexEffect = _lib.get("spAnimationState_setVertexEffect", "cdecl")
    spAnimationState_setVertexEffect.argtypes = [POINTER(struct_spAnimationState), POINTER(struct_spVertexEffect)]
    spAnimationState_setVertexEffect.restype = None
    break

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 796
if _libs["spine"].has("spSkeletonData_findAnimation", "cdecl"):
    spSkeletonData_findAnimation = _libs["spine"].get("spSkeletonData_findAnimation", "cdecl")
    spSkeletonData_findAnimation.argtypes = [POINTER(struct_spSkeletonData), String]
    spSkeletonData_findAnimation.restype = POINTER(struct_spAnimation)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 797
if _libs["spine"].has("spSkeletonData_findSkin", "cdecl"):
    spSkeletonData_findSkin = _libs["spine"].get("spSkeletonData_findSkin", "cdecl")
    spSkeletonData_findSkin.argtypes = [POINTER(struct_spSkeletonData), String]
    spSkeletonData_findSkin.restype = POINTER(struct_spSkin)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 798
if _libs["spine"].has("spSkeleton_setSkin", "cdecl"):
    spSkeleton_setSkin = _libs["spine"].get("spSkeleton_setSkin", "cdecl")
    spSkeleton_setSkin.argtypes = [POINTER(struct_spSkeleton), POINTER(struct_spSkin)]
    spSkeleton_setSkin.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 799
if _libs["spine"].has("spSkeleton_findIkConstraint", "cdecl"):
    spSkeleton_findIkConstraint = _libs["spine"].get("spSkeleton_findIkConstraint", "cdecl")
    spSkeleton_findIkConstraint.argtypes = [POINTER(struct_spSkeleton), String]
    spSkeleton_findIkConstraint.restype = POINTER(struct_spIkConstraint)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 800
if _libs["spine"].has("spSkeleton_findTransformConstraint", "cdecl"):
    spSkeleton_findTransformConstraint = _libs["spine"].get("spSkeleton_findTransformConstraint", "cdecl")
    spSkeleton_findTransformConstraint.argtypes = [POINTER(struct_spSkeleton), String]
    spSkeleton_findTransformConstraint.restype = POINTER(struct_spTransformConstraint)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 801
if _libs["spine"].has("spSkeleton_findPathConstraint", "cdecl"):
    spSkeleton_findPathConstraint = _libs["spine"].get("spSkeleton_findPathConstraint", "cdecl")
    spSkeleton_findPathConstraint.argtypes = [POINTER(struct_spSkeleton), String]
    spSkeleton_findPathConstraint.restype = POINTER(struct_spPathConstraint)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 802
if _libs["spine"].has("spRegionAttachment_create", "cdecl"):
    spRegionAttachment_create = _libs["spine"].get("spRegionAttachment_create", "cdecl")
    spRegionAttachment_create.argtypes = [String]
    spRegionAttachment_create.restype = POINTER(struct_spRegionAttachment)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 803
if _libs["spine"].has("spMeshAttachment_create", "cdecl"):
    spMeshAttachment_create = _libs["spine"].get("spMeshAttachment_create", "cdecl")
    spMeshAttachment_create.argtypes = [String]
    spMeshAttachment_create.restype = POINTER(struct_spMeshAttachment)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 804
if _libs["spine"].has("spMeshAttachment_updateUVs", "cdecl"):
    spMeshAttachment_updateUVs = _libs["spine"].get("spMeshAttachment_updateUVs", "cdecl")
    spMeshAttachment_updateUVs.argtypes = [POINTER(struct_spMeshAttachment)]
    spMeshAttachment_updateUVs.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 805
if _libs["spine"].has("spClippingAttachment_create", "cdecl"):
    spClippingAttachment_create = _libs["spine"].get("spClippingAttachment_create", "cdecl")
    spClippingAttachment_create.argtypes = [String]
    spClippingAttachment_create.restype = POINTER(struct_spClippingAttachment)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 806
if _libs["spine"].has("spJitterVertexEffect_create", "cdecl"):
    spJitterVertexEffect_create = _libs["spine"].get("spJitterVertexEffect_create", "cdecl")
    spJitterVertexEffect_create.argtypes = [c_float, c_float]
    spJitterVertexEffect_create.restype = POINTER(struct_spVertexEffect)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 807
for _lib in _libs.values():
    if not _lib.has("spVertexEffect_dispose", "cdecl"):
        continue
    spVertexEffect_dispose = _lib.get("spVertexEffect_dispose", "cdecl")
    spVertexEffect_dispose.argtypes = [POINTER(struct_spVertexEffect)]
    spVertexEffect_dispose.restype = None
    break

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 808
if _libs["spine"].has("spSkeletonClipping_clipStart", "cdecl"):
    spSkeletonClipping_clipStart = _libs["spine"].get("spSkeletonClipping_clipStart", "cdecl")
    spSkeletonClipping_clipStart.argtypes = [POINTER(struct_spSkeletonClipping), POINTER(struct_spSlot), POINTER(struct_spClippingAttachment)]
    spSkeletonClipping_clipStart.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 809
if _libs["spine"].has("spSkeletonClipping_clipEnd", "cdecl"):
    spSkeletonClipping_clipEnd = _libs["spine"].get("spSkeletonClipping_clipEnd", "cdecl")
    spSkeletonClipping_clipEnd.argtypes = [POINTER(struct_spSkeletonClipping), POINTER(struct_spSlot)]
    spSkeletonClipping_clipEnd.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 810
if _libs["spine"].has("spSkeletonClipping_clipEnd2", "cdecl"):
    spSkeletonClipping_clipEnd2 = _libs["spine"].get("spSkeletonClipping_clipEnd2", "cdecl")
    spSkeletonClipping_clipEnd2.argtypes = [POINTER(struct_spSkeletonClipping)]
    spSkeletonClipping_clipEnd2.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 811
if _libs["spine"].has("spRegionAttachment_computeWorldVertices", "cdecl"):
    spRegionAttachment_computeWorldVertices = _libs["spine"].get("spRegionAttachment_computeWorldVertices", "cdecl")
    spRegionAttachment_computeWorldVertices.argtypes = [POINTER(struct_spRegionAttachment), POINTER(struct_spSlot), POINTER(c_float), c_int, c_int]
    spRegionAttachment_computeWorldVertices.restype = None

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 812
for _lib in _libs.values():
    if not _lib.has("spMeshAttachment_computeWorldVertices", "cdecl"):
        continue
    spMeshAttachment_computeWorldVertices = _lib.get("spMeshAttachment_computeWorldVertices", "cdecl")
    spMeshAttachment_computeWorldVertices.argtypes = [POINTER(struct_spMeshAttachment), POINTER(struct_spSlot), c_int, c_int, POINTER(c_float), c_int, c_int]
    spMeshAttachment_computeWorldVertices.restype = None
    break

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 813
if _libs["spine"].has("spEventData_create", "cdecl"):
    spEventData_create = _libs["spine"].get("spEventData_create", "cdecl")
    spEventData_create.argtypes = [String]
    spEventData_create.restype = POINTER(struct_spEventData)

# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 814
if _libs["spine"].has("spEventData_dispose", "cdecl"):
    spEventData_dispose = _libs["spine"].get("spEventData_dispose", "cdecl")
    spEventData_dispose.argtypes = [POINTER(struct_spEventData)]
    spEventData_dispose.restype = None

spColor = struct_spColor# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 90

spFloatArray = struct_spFloatArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 95

spShortArray = struct_spShortArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 101

spIntArray = struct_spIntArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 107

spUnsignedShortArray = struct_spUnsignedShortArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 113

spArrayFloatArray = struct_spArrayFloatArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 119

spArrayShortArray = struct_spArrayShortArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 125

spBoneDataArray = struct_spBoneDataArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 131

spIkConstraintDataArray = struct_spIkConstraintDataArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 137

spTransformConstraintDataArray = struct_spTransformConstraintDataArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 143

spPathConstraintDataArray = struct_spPathConstraintDataArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 149

spTrackEntryArray = struct_spTrackEntryArray# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 155

spAttachment = struct_spAttachment# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 162

spVertexAttachment = struct_spVertexAttachment# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 170

spRegionAttachment = struct_spRegionAttachment# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 181

spMeshAttachment = struct_spMeshAttachment# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 194

spPointAttachment = struct_spPointAttachment# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 217

spClippingAttachment = struct_spClippingAttachment# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 223

spPathAttachment = struct_spPathAttachment# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 228

spBoundingBoxAttachment = struct_spBoundingBoxAttachment# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 235

spBoneData = struct_spBoneData# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 239

spSlotData = struct_spSlotData# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 249

spEventData = struct_spEventData# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 259

spEvent = struct_spEvent# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 269

spTimeline = struct_spTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 279

spCurveTimeline = struct_spCurveTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 284

spBaseTimeline = struct_spBaseTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 289

spColorTimeline = struct_spColorTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 296

spTwoColorTimeline = struct_spTwoColorTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 303

spAttachmentTimeline = struct_spAttachmentTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 310

spEventTimeline = struct_spEventTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 318

spDrawOrderTimeline = struct_spDrawOrderTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 325

spDeformTimeline = struct_spDeformTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 333

spIkConstraintTimeline = struct_spIkConstraintTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 343

spTransformConstraintTimeline = struct_spTransformConstraintTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 350

spPathConstraintPositionTimeline = struct_spPathConstraintPositionTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 357

spPathConstraintSpacingTimeline = struct_spPathConstraintSpacingTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 364

spPathConstraintMixTimeline = struct_spPathConstraintMixTimeline# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 371

spAnimation = struct_spAnimation# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 378

spBone = struct_spBone# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 385

spSlot = struct_spSlot# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 400

spPathConstraintData = struct_spPathConstraintData# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 412

spPathConstraint = struct_spPathConstraint# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 426

spTransformConstraintData = struct_spTransformConstraintData# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 446

spTransformConstraint = struct_spTransformConstraint# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 459

spIkConstraintData = struct_spIkConstraintData# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 468

spIkConstraint = struct_spIkConstraint# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 483

spSkeleton = struct_spSkeleton# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 496

spAttachmentLoader = struct_spAttachmentLoader# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 517

spAtlasAttachmentLoader = struct_spAtlasAttachmentLoader# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 523

_Entry = struct__Entry# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 528

_SkinHashTableEntry = struct__SkinHashTableEntry# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 535

spSkin = struct_spSkin# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 540

_spSkin = struct__spSkin# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 548

spVertexEffect = struct_spVertexEffect# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 554

spJitterVertexEffect = struct_spJitterVertexEffect# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 560

spSwirlVertexEffect = struct_spSwirlVertexEffect# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 566

spSkeletonData = struct_spSkeletonData# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 576

spSkeletonJson = struct_spSkeletonJson# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 601

spSkeletonBinary = struct_spSkeletonBinary# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 607

spAnimationStateData = struct_spAnimationStateData# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 613

spPolygon = struct_spPolygon# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 619

spSkeletonBounds = struct_spSkeletonBounds# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 625

spTriangulator = struct_spTriangulator# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 632

spSkeletonClipping = struct_spSkeletonClipping# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 642

spAnimationState = struct_spAnimationState# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 82

spTrackEntry = struct_spTrackEntry# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 659

spAtlasPage = struct_spAtlasPage# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 721

spAtlasRegion = struct_spAtlasRegion# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 732

spAtlas = struct_spAtlas# /Users/michelleyan/Downloads/cpyne-main/spine-python-backup4/manual_binding.h: 748

# No inserted files

# No prefix-stripping

