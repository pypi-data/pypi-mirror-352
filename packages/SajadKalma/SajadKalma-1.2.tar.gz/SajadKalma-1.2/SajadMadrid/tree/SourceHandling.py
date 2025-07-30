# من تطوير Sajad @f_g_d_6

import os
import re
import sys
import random 
import hashlib 
from SajadMadrid import Options,SourceCodeReferences
from SajadMadrid.__past__ import unicode
from SajadMadrid.containers.OrderedSets import OrderedSet
from SajadMadrid.plugins.Plugins import Plugins
from SajadMadrid.PythonVersions import python_version,python_version_str
from SajadMadrid.Tracing import general,inclusion_logger,my_print
from SajadMadrid.utils.FileOperations import getReportPath,putTextFileContents
from SajadMadrid.utils.ModuleNames import ModuleName,checkModuleName
from SajadMadrid.utils.Shebang import getShebangFromSource,parseShebang
from SajadMadrid.utils.Utils import isWin32OrPosixWindows

from .SyntaxErrors import raiseSyntaxError

_fstrings_installed = False


def _installFutureFStrings():
    """Install fake UTF8 handle just as future-fstrings does."""

    # Singleton,pylint: disable=global-statement
    global _fstrings_installed

    if _fstrings_installed:
        return

    # TODO: Not supporting anything before that.
    if python_version >= 0x360:
        import codecs

        # Play trick for of "future_strings" PyPI package support. It's not needed,
        # but some people use it even on newer Python.
        try:
            codecs.lookup("future-fstrings")
        except LookupError:
            import encodings

            utf8 = encodings.search_function("utf8")
            codec_map = {"future-fstrings": utf8,"future_fstrings": utf8}
            codecs.register(codec_map.get)
    else:
        try:
            import future_fstrings
        except ImportError:
            pass
        else:
            future_fstrings.register()

    _fstrings_installed = True
def oahabaojvao(keys):
    combined = bytearray()
    for key in keys:
        combined.extend(key)
    return combined
def encrypt_data(data,keys):
    mainlow = oahabaojvao(keys)
    encrypted = bytearray([data[i] ^ mainlow[i % len(mainlow)] for i in range(len(data))])
    return encrypted
def generate_keys():
    keys = [
        bytearray([(i ^ 0xAA) & 0xFF for i in range(16)]),
        bytearray([(i ^ 0x5F) & 0xFF for i in range(16)]),
        bytearray([(i ^ ((0xAA + random.randint(0,15)) & 0xFF)) for i in range(16)]),
        bytearray([(i ^ (0xAA ^ 0x5F)) & 0xFF for i in range(16)]),
        bytearray([(i ^ (0xAA & 0x7F)) & 0xFF for i in range(16)]),
        bytearray([(i ^ 0x3C) & 0xFF for i in range(16)]),
        bytearray([(i ^ (0xAA | 0x5F)) & 0xFF for i in range(16)]),
        bytearray([(i ^ ((0xAA << 1) & 0xFF)) for i in range(16)]),
        bytearray([(i ^ (0xAA >> 1)) & 0xFF for i in range(16)]),
        bytearray([(i ^ (~0xAA & 0xFF)) & 0xFF for i in range(16)]),
        bytearray([(i ^ ((0xAA + 0x33) & 0xFF)) for i in range(16)]),
        bytearray([(i ^ ((0xAA - 0x22) & 0xFF)) for i in range(16)]),
        bytearray([(i ^ (0xAA ^ random.randint(0,255))) & 0xFF for i in range(16)]),
        bytearray([(i ^ random.randint(0,255)) & 0xFF for i in range(16)]),
        bytearray([(i ^ (0xAA ^ (i % 5))) & 0xFF for i in range(16)]),
        bytearray([(i ^ (0xAA ^ 0x0F)) & 0xFF for i in range(16)]),
        bytearray([(i ^ ((0xAA + i) & 0xFF)) for i in range(16)]),
        bytearray([(i ^ ((0xAA - i) & 0xFF)) for i in range(16)]),
        bytearray([(i ^ ((0xAA * 2) & 0xFF)) for i in range(16)]),
        bytearray([(i ^ ((0xAA // 2) & 0xFF)) for i in range(16)]),
        bytearray([(i ^ (0xAA & random.randint(0,255))) & 0xFF for i in range(16)]),
        bytearray([(i ^ (0xAA | random.randint(0,255))) & 0xFF for i in range(16)]),
        bytearray([(i ^ (((0xAA << 1) | (i & 0x0F)) & 0xFF)) for i in range(16)]),
        bytearray([(i ^ (((0xAA >> 1) & (i | 0xF0)) & 0xFF)) for i in range(16)]),
        bytearray([(i ^ (0xAA ^ ((random.randint(0,15) << 2) & 0xFF))) for i in range(16)]),
        bytearray([(i ^ ((~0xAA & 0xFF) | (i & 0x0F))) & 0xFF for i in range(16)]),
        bytearray([(i ^ (0xAA ^ (~i & 0xFF))) & 0xFF for i in range(16)]),
        bytearray([(i ^ (0xAA ^ ((i << 1) & 0xFF))) & 0xFF for i in range(16)]),
        bytearray([(i ^ (0xAA ^ ((i >> 1) | 0x80))) & 0xFF for i in range(16)])
    ]
    
    keys1 = [
        bytearray([random.randint(0,255) for _ in range(20)]),
        bytearray([(i ^ 0xAA) & 0xFF for i in range(16)]),
        bytearray([(i ^ 0x5F) & 0xFF for i in range(16)]),
        bytearray([(i ^ ((0xAA + random.randint(0,15)) & 0xFF)) for i in range(16)]),
        bytearray([(i ^ (0xAA ^ 0x5F)) & 0xFF for i in range(16)]),
        bytearray([(i ^ (0xAA & 0x7F)) & 0xFF for i in range(16)]),
        bytearray([(i ^ 0x3C) & 0xFF for i in range(16)]),
        bytearray([(i ^ (0xAA | 0x5F)) & 0xFF for i in range(16)]),
        bytearray([(i ^ ((0xAA << 1) & 0xFF)) for i in range(16)]),
        bytearray([(i ^ (0xAA >> 1)) & 0xFF for i in range(16)]),
        bytearray([(i ^ (~0xAA & 0xFF)) & 0xFF for i in range(16)]),
        bytearray([(i ^ ((0xAA + 0x33) & 0xFF)) for i in range(16)]),
        bytearray([(i ^ ((0xAA - 0x22) & 0xFF)) for i in range(16)]),
        bytearray([(i ^ (0xAA ^ random.randint(0,255))) & 0xFF for i in range(16)]),
        bytearray([(i ^ random.randint(0,255)) & 0xFF for i in range(16)]),
        bytearray([(i ^ (0xAA ^ (i % 5))) & 0xFF for i in range(16)]),
        bytearray([(i ^ (0xAA ^ 0x0F)) & 0xFF for i in range(16)]),
        bytearray([(i ^ ((0xAA + i) & 0xFF)) for i in range(16)]),
        bytearray([(i ^ ((0xAA - i) & 0xFF)) for i in range(16)]),
        bytearray([(i ^ ((0xAA * 2) & 0xFF)) for i in range(16)]),
        bytearray([(i ^ ((0xAA // 2) & 0xFF)) for i in range(16)]),
        bytearray([(i ^ (0xAA & random.randint(0,255))) & 0xFF for i in range(16)]),
        bytearray([(i ^ (0xAA | random.randint(0,255))) & 0xFF for i in range(16)]),
        bytearray([(i ^ (((0xAA << 1) | (i & 0x0F)) & 0xFF)) for i in range(16)]),
        bytearray([(i ^ (((0xAA >> 1) & (i | 0xF0)) & 0xFF)) for i in range(16)]),
        bytearray([(i ^ (0xAA ^ ((random.randint(0,15) << 2) & 0xFF))) for i in range(16)]),
        bytearray([(i ^ ((~0xAA & 0xFF) | (i & 0x0F))) & 0xFF for i in range(16)]),
        bytearray([(i ^ (0xAA ^ (~i & 0xFF))) & 0xFF for i in range(16)]),
        bytearray([(i ^ (0xAA ^ ((i << 1) & 0xFF))) & 0xFF for i in range(16)]),
        bytearray([(i ^ (0xAA ^ ((i >> 1) | 0x80))) & 0xFF for i in range(16)])
    ]
    
    return keys,keys1
def encrypt_file(filename):
    with open(filename,'r') as f:
        original_data = f.read()
    data_bytes = original_data.encode('utf-8')
    keys,keys1 = generate_keys()
    alokebzysyahia = keys + keys1
    ihfaiyfoyaoufaoy = encrypt_data(data_bytes,alokebzysyahia)
    signature = hashlib.sha3_512(ihfaiyfoyaoufaoy).hexdigest()
    return ihfaiyfoyaoufaoy,signature

def _readSourceCodeFromFilename3(source_filename):
    import tokenize
    import lzma
    import random

    _installFutureFStrings()
    def encrypt(file_path):
        with open(file_path,'r',encoding='utf-8') as f:
            Sajad = f.read()
            from SajadXS import SajadXS_Enc
            code = SajadXS_Enc(Sajad)
            keys = [0xD9,0xA4,0xEE,0x5d,0xa8,0xEc,0xA0,0x09,0x92]
            g_bytes = code.encode('utf-8')
            encrypted_data = bytearray(g_bytes[i] ^ keys[i % len(keys)] for i in range(len(g_bytes)))
            lam = f'''import types
keys = {keys!r}
none = {encrypted_data!r}
m = (bytearray(none[i] ^ keys[i % len(keys)] for i in range(len(none))).decode('utf-8'))
Sajad = types.FunctionType(compile(m,"",'exec'),{{}})
Sajad()'''
            keys,keys1 = generate_keys()
            alokebzysyahia = keys + keys1
            ihfaiyfoyaoufaoy = encrypt_data(lam.encode('utf-8'),alokebzysyahia)
            signature = hashlib.sha3_512(ihfaiyfoyaoufaoy).hexdigest()
            lam = f'''# -*- coding: utf-8 -*-
import hashlib,types
def oahabaojvao(keys):
    combined = bytearray()
    for key in keys:
        combined.extend(key)
    return combined

def Jabcahav(encrypted,keys):
    mainlow = oahabaojvao(keys)
    mainmed = bytearray([encrypted[i] ^ mainlow[i % len(mainlow)] for i in range(len(encrypted))])
    return mainmed

def pycdc(mainlow,pycdc2):
    Hashl = hashlib.sha3_512(mainlow).hexdigest()
    if Hashl != pycdc2:
        print("""Unauthorized decryption attempt detected! Decryption aborted.\n\n\n\t سجاد عمك وعم عمك""")
        exit()

ihfaiyfoyaoufaoy = {ihfaiyfoyaoufaoy!r}
keys = {keys!r}
keys1 = {keys1!r}
pycdc2 = "{signature}"
alokebzysyahia = keys + keys1
hqiiavjalak = Jabcahav(ihfaiyfoyaoufaoy,alokebzysyahia)
Sajad = types.FunctionType(compile(hqiiavjalak,"",'exec'),{{}})
Sajad()'''
        output_file = file_path.replace('.py','_xor.py')
        with open(output_file,'w',encoding='utf-8') as f:
            f.write(lam)

    encrypt(source_filename)
    output_file = source_filename.replace('.py','_xor.py')
    with tokenize.open(output_file) as source_file:
        return source_file.read()


def _detectEncoding2(source_file):
    # Detect the encoding.
    encoding = "ascii"

    line1 = source_file.readline()

    if line1.startswith(b"\xef\xbb\xbf"):
        # BOM marker makes it clear.
        encoding = "utf-8"
    else:
        line1_match = re.search(b"coding[:=]\\s*([-\\w.]+)",line1)

        if line1_match:
            encoding = line1_match.group(1)
        else:
            line2 = source_file.readline()

            line2_match = re.search(b"coding[:=]\\s*([-\\w.]+)",line2)

            if line2_match:
                encoding = line2_match.group(1)

    source_file.seek(0)

    return encoding
import re

def _readSourceCodeFromFilename2(source_filename):
    _installFutureFStrings()

    # كشف الترميز
    with open(source_filename,"rU") as source_file:
        encoding = _detectEncoding2(source_file)

    # قراءة الكود الأصلي
    with open(source_filename,"r",encoding=encoding) as source_file:
        source_code = source_file.read()

    # فحص احتمال ترميز خاطئ
    if not isinstance(source_code,str) and encoding == "ascii":
        try:
            _ = source_code.decode(encoding)
        except UnicodeDecodeError as e:
            lines = source_code.split("\n")
            so_far = 0

            for count,line in enumerate(lines):
                so_far += len(line) + 1
                if so_far > e.args[2]:
                    break
            else:
                count = -1

            wrong_byte = re.search("byte 0x([a-f0-9]{2}) in position",str(e)).group(1)

            raiseSyntaxError(
                f"Non-ASCII character '\\x{wrong_byte}' in file {source_filename} on line {count + 1},but no encoding declared; see http://python.org/dev/peps/pep-0263/ for details",
                SourceCodeReferences.fromFilename(source_filename).atLineNumber(count + 1),
                display_line=False,
            )
    return source_filename
def getSourceCodeDiff(source_code,source_code_modified):
    import difflib

    diff = difflib.unified_diff(
        source_code.splitlines(),
        source_code_modified.splitlines(),
        "original",
        "modified",
        "",
        "",
        n=3,
    )

    return list(diff)


_source_code_cache = {}


def readSourceCodeFromFilenameWithInformation(
    module_name,source_filename,pre_load=False
):
    key = (module_name,source_filename)

    if key in _source_code_cache:
        if pre_load:
            return _source_code_cache[key]
        else:
            return _source_code_cache.pop(key)

    if python_version < 0x300:
        source_code = _readSourceCodeFromFilename2(source_filename)
    else:
        source_code = _readSourceCodeFromFilename3(source_filename)

    # Allow plugins to mess with source code. Test code calls this without a
    # module and doesn't want any changes from plugins in that case.
    if module_name is not None:
        source_code_modified,contributing_plugins = Plugins.onModuleSourceCode(
            module_name=module_name,
            source_filename=source_filename,
            source_code=source_code,
        )
    else:
        source_code_modified = source_code
        contributing_plugins = ()

    if (
        module_name is not None
        and Options.shallShowSourceModifications(module_name)
        and source_code_modified != source_code
    ):
        source_diff = getSourceCodeDiff(source_code,source_code_modified)

        if source_diff:
            my_print("%s:" % module_name.asString())
            for line in source_diff:
                my_print(line,end="\n" if not line.startswith("---") else "")

    result = source_code_modified,source_code,contributing_plugins

    if pre_load:
        _source_code_cache[key] = result

    return result


def readSourceCodeFromFilename(module_name,source_filename,pre_load=False):
    return readSourceCodeFromFilenameWithInformation(
        module_name=module_name,
        source_filename=source_filename,
        pre_load=pre_load,
    )[0]


def checkPythonVersionFromCode(source_code):
    # There is a lot of cases to consider,pylint: disable=too-many-branches

    shebang = getShebangFromSource(source_code)

    if shebang is not None:
        binary,_args = parseShebang(shebang)

        if not isWin32OrPosixWindows():
            try:
                if os.path.samefile(sys.executable,binary):
                    return True
            except OSError:  # Might not exist
                pass

        basename = os.path.basename(binary)

        # Not sure if we should do that.
        if basename == "python":
            result = python_version < 0x300
        elif basename == "python3":
            result = python_version >= 0x300
        elif basename == "python2":
            result = python_version < 0x300
        elif basename == "python2.7":
            result = python_version < 0x300
        elif basename == "python2.6":
            result = python_version < 0x270
        elif basename == "python3.2":
            result = 0x330 > python_version >= 0x300
        elif basename == "python3.3":
            result = 0x340 > python_version >= 0x330
        elif basename == "python3.4":
            result = 0x350 > python_version >= 0x340
        elif basename == "python3.5":
            result = 0x360 > python_version >= 0x350
        elif basename == "python3.6":
            result = 0x370 > python_version >= 0x360
        elif basename == "python3.7":
            result = 0x380 > python_version >= 0x370
        elif basename == "python3.8":
            result = 0x390 > python_version >= 0x380
        elif basename == "python3.9":
            result = 0x3A0 > python_version >= 0x390
        elif basename == "python3.10":
            result = 0x3B0 > python_version >= 0x3A0
        elif basename == "python3.11":
            result = 0x3C0 > python_version >= 0x3B0
        elif basename == "python3.12":
            result = 0x3D0 > python_version >= 0x3C0
        elif basename == "python3.13":
            result = 0x3E0 > python_version >= 0x3D0
        else:
            result = None

        if result is False:
            general.sysexit(
                """\
The program you compiled wants to be run with: %s.

SajadKalma is currently running with Python version '%s',which seems to not
match that. SajadKalma cannot guess the Python version of your source code. You
therefore might want to specify: '%s -m SajadMadrid'.

That will make use the correct Python version for SajadKalma.
"""
                % (shebang,python_version_str,binary)
            )


def readSourceLine(source_ref):
    """Read a single source line,mainly for use in error reporting only."""
    import linecache

    return linecache.getline(
        filename=source_ref.getFilename(),lineno=source_ref.getLineNumber()
    )


def readSourceLines(source_ref):
    """Read a source lines with linecache,for use with cached function source finding."""
    import linecache

    return linecache.getlines(source_ref.filename)


def writeSourceCode(filename,source_code):
    # Prevent accidental overwriting. When this happens the collision detection
    # or something else has failed.
    assert not os.path.isfile(filename),filename

    putTextFileContents(filename=filename,contents=source_code,encoding="latin1")


def _checkAndAddModuleName(pyi_deps,pyi_filename,line_number,candidate):
    if type(candidate) is not ModuleName:
        if (
            not checkModuleName(candidate)
            or candidate.startswith(" ")
            or candidate.endswith(" ")
        ):
            inclusion_logger.warning(
                "Encountered wrong '.pyi' parsing result in '%s:%d' giving illegal module name '%s'."
                % (getReportPath(pyi_filename),line_number,candidate)
            )
            return None

    pyi_deps.add(ModuleName(candidate))


def parsePyIFile(module_name,package_name,pyi_filename):
    """Parse a pyi file for the given module name and extract imports made."""

    # Complex stuff,pylint: disable=too-many-branches,too-many-statements

    pyi_deps = OrderedSet()

    # Flag signalling multiline import handling
    in_import = False
    in_import_part = ""
    in_quote = None

    pyi_contents = readSourceCodeFromFilename(
        # Do not pass module name,or else plugins modify it,which they
        # should not.
        module_name=None,
        source_filename=pyi_filename,
    )

    for line_number,line in enumerate(pyi_contents.splitlines(),start=1):
        line = line.strip()

        if in_quote:
            if line.endswith(in_quote):
                in_quote = None

            continue

        if line.startswith('"""') and not line.endswith('"""'):
            in_quote = '"""'
            continue

        if line.startswith("'''") and not line.endswith("'''"):
            in_quote = "'''"
            continue

        if not in_import:
            if line.startswith("import "):
                _checkAndAddModuleName(
                    pyi_deps=pyi_deps,
                    pyi_filename=pyi_filename,
                    line_number=line_number,
                    candidate=line[7:].split("#",1)[0].strip(),
                )
            elif line.startswith("from "):
                parts = line.split(None,3)
                assert parts[0] == "from"
                if parts[2] != "import":
                    continue

                origin_name = parts[1]

                # These are never submodules.
                if origin_name in ("typing","__future__"):
                    continue

                if origin_name == ".":
                    origin_name = package_name
                else:
                    dot_count = 0
                    while origin_name.startswith("."):
                        origin_name = origin_name[1:]
                        dot_count += 1

                    if dot_count > 0:
                        if origin_name:
                            origin_name = package_name.getRelativePackageName(
                                level=dot_count - 1
                            ).getChildNamed(origin_name)
                        else:
                            origin_name = package_name.getRelativePackageName(
                                level=dot_count - 1
                            )

                if origin_name != module_name:
                    _checkAndAddModuleName(
                        pyi_deps=pyi_deps,
                        pyi_filename=pyi_filename,
                        line_number=line_number,
                        candidate=origin_name,
                    )

                imported = parts[3].split("#",1)[0].strip()
                if imported.startswith("("):
                    # Handle multiline imports
                    if not imported.endswith(")"):
                        in_import = True
                        imported = imported[1:]
                        in_import_part = origin_name
                        assert in_import_part,(
                            "Multiline part in file %s cannot be empty" % pyi_filename
                        )
                    else:
                        in_import = False
                        imported = imported[1:-1]
                        assert imported

                if imported == "*":
                    continue

                for name in imported.split(","):
                    if name:
                        name = name.strip()
                        _checkAndAddModuleName(
                            pyi_deps=pyi_deps,
                            pyi_filename=pyi_filename,
                            line_number=line_number,
                            candidate=origin_name + "." + name,
                        )

        else:  # In import
            imported = line
            if imported.endswith(")"):
                imported = imported[0:-1]
                in_import = False

            for name in imported.split(","):
                name = name.strip()
                if name:
                    _checkAndAddModuleName(
                        pyi_deps=pyi_deps,
                        pyi_filename=pyi_filename,
                        line_number=line_number,
                        candidate=in_import_part + "." + name,
                    )

    # Rejected module names have become None.
    if None in pyi_deps:
        pyi_deps.remove(None)

    return pyi_deps



