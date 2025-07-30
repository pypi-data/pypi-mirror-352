# من تطوير Sajad @f_g_d_6


""" Internal tool, attach the standalone distribution in compressed form.

"""

import os
import sys

if __name__ == "__main__":
    sys.path.insert(0, os.environ["SAJODE_PACKAGE_HOME"])

    import SajadMadrid  # just to have it loaded from there, pylint: disable=unused-import

    del sys.path[0]

    sys.path = [
        path_element
        for path_element in sys.path
        if os.path.dirname(os.path.abspath(__file__)) != path_element
    ]

    from SajadMadrid.tools.onefile_compressor.OnefileCompressor import main

    main()


