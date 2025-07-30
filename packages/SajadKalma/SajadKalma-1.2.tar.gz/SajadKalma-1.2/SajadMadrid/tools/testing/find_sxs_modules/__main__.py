#!/usr/bin/env python
# من تطوير Sajad @f_g_d_6


""" Tool to compare find SxS using modules.

"""

import os
import sys
import tempfile

from SajadMadrid.tools.testing.Common import (
    compileLibraryTest,
    createSearchMode,
    setup,
)
from SajadMadrid.Tracing import my_print
from SajadMadrid.utils.SharedLibraries import getSxsFromDLL


def decide(root, filename):
    return (
        filename.endswith((".so", ".pyd"))
        and not filename.startswith("libpython")
        and getSxsFromDLL(os.path.join(root, filename))
    )


def action(stage_dir, root, path):
    # We need only the actual path, pylint: disable=unused-argument

    sxs = getSxsFromDLL(path)
    if sxs:
        my_print(path, sxs)


def main():
    if os.name != "nt":
        sys.exit("Error, this is only for use on Windows where SxS exists.")

    setup(needs_io_encoding=True)
    search_mode = createSearchMode()

    tmp_dir = tempfile.gettempdir()

    compileLibraryTest(
        search_mode=search_mode,
        stage_dir=os.path.join(tmp_dir, "find_sxs_modules"),
        decide=decide,
        action=action,
    )

    my_print("FINISHED, all extension modules checked.")


if __name__ == "__main__":
    main()


