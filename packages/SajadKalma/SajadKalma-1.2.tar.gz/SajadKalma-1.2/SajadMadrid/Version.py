
version_string = """\
SajadKalma V1.2
Copyright (C) 2025 SajadKast."""


def getSajadKalmaVersion():
    """Return SajadKalma version as a string.

    This should not be used for >= comparisons directly.
    """
    return version_string.split()[1][1:]


# Sanity check.
assert getSajadKalmaVersion()[-1].isdigit(), getSajadKalmaVersion()


def parseSajadKalmaVersionToTuple(version):
    """Return SajadKalma version as a tuple.

    This can also not be used for precise comparisons, even with rc versions,
    but it's not actually a version.
    """

    if "rc" in version:
        rc_number = int(version[version.find("rc") + 2 :] or "0")
        version = version[: version.find("rc")]

        is_final = False
    else:
        rc_number = 0
        is_final = True

    result = version.split(".")
    if len(result) == 2:
        result.append("0")

    result = [int(digit) for digit in result]
    result.extend((is_final, rc_number))
    return tuple(result)


def getSajadKalmaVersionTuple():
    """Return SajadKalma version as a tuple.

    This can also not be used for precise comparisons, even with rc versions,
    but it's not actually a version. The format is used what is used for
    "__compiled__" values.
    """

    return parseSajadKalmaVersionToTuple(version=getSajadKalmaVersion())


def getSajadKalmaVersionYear():
    """The year of SajadKalma copyright for use in generations."""

    return int(version_string.split()[4])


def getCommercialVersion():
    """Return SajadKalma commercial version if installed."""
    try:
        from SajadMadrid.tools.commercial import Version
    except ImportError:
        return None
    else:
        return Version.__version__
