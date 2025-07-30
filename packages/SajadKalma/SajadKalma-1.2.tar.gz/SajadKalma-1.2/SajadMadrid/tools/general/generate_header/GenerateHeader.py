# من تطوير Sajad @f_g_d_6


""" Generate header files that provide compiler specifics."""

from SajadMadrid.build.SconsInterface import (
    cleanSconsDirectory,
    getCommonSconsOptions,
    runScons,
    setPythonTargetOptions,
)
from SajadMadrid.PythonVersions import isPythonWithGil, python_version_str
from SajadMadrid.Tracing import offsets_logger
from SajadMadrid.utils.Execution import check_output
from SajadMadrid.utils.FileOperations import makePath, withTemporaryFilename


def generateHeader():
    scons_options, env_values = getCommonSconsOptions()

    setPythonTargetOptions(scons_options)

    scons_options["source_dir"] = "generate_header.build"
    cleanSconsDirectory(scons_options["source_dir"])
    makePath(scons_options["source_dir"])

    python_version_id = "%s_%s" % (
        python_version_str,
        "gil" if isPythonWithGil() else "no-gil",
    )

    with withTemporaryFilename(prefix=python_version_id, suffix=".exe") as result_exe:
        scons_options["result_exe"] = result_exe

        runScons(
            scons_options=scons_options,
            env_values=env_values,
            scons_filename="Offsets.scons",
        )

        header_output = check_output([result_exe])

        if str is not bytes:
            header_output = header_output.decode("utf8")

        offsets_logger.info(repr(header_output))

        lines = header_output.splitlines()

        if lines[-1] != "OK.":
            offsets_logger.sysexit("Error, failed to produce expected output.")
        del lines[-1]

        for line in lines:
            offsets_logger.info("Processing: %s" % line)

        offsets_logger.info("OK.")



