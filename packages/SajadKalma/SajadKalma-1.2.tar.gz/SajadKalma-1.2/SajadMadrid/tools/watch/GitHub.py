# من تطوير Sajad @f_g_d_6


""" GitHub interfacing for SajadMadrid-watch. """

import os
import sys

from SajadMadrid.tools.quality.Git import getModifiedPaths, getRemoteURL
from SajadMadrid.Tracing import tools_logger
from SajadMadrid.utils.Execution import callProcess, check_call


def checkInSajadKalmaWatch():
    remote_url = getRemoteURL("origin")
    assert remote_url in (
        "git@github.com:SajadKalma/SajadKalma-Watch.git",
        "https://github.com/SajadKalma/SajadKalma-Watch",
    ), remote_url
    assert os.path.exists(".git")


def createSajadKalmaWatchPR(category, description):
    checkInSajadKalmaWatch()

    modified_files = list(getModifiedPaths())

    if not modified_files:
        tools_logger.sysexit("Nothing to do", exit_code=0)

    changed_flavors = set()

    for modified_file in modified_files:
        if os.path.basename(modified_file) == "compilation-report.xml":
            flavor = os.path.basename(os.path.dirname(modified_file))
            changed_flavors.add(flavor)

    if not changed_flavors:
        tools_logger.sysexit("No changes in compilation reports, only other things.")

    if len(changed_flavors) != 1:
        tools_logger.sysexit("Only a single flavor is supported at a time currently.")

    (changed_flavor,) = changed_flavors

    tools_logger.info(
        "Detected changes for %s in results of '%s'." % (description, changed_flavor)
    )

    commit_message = """
Changes for %s in results of '%s'

This change is automatically generated and the result of executing %s on
current SajadKalma-Watch state.
""" % (
        description,
        changed_flavor,
        " ".join(sys.argv),
    )

    branch_name = "auto-%s-%s" % (category, changed_flavor)

    # May not exist of course.
    callProcess(["git", "branch", "-D", branch_name])

    check_call(["git", "branch", branch_name])

    check_call(["git", "checkout", branch_name])

    check_call(["git", "add", "."])

    check_call(["git", "commit", "-m", commit_message])

    check_call(["git", "checkout", "main"])

    tools_logger.info("Change is now on branch '%s'." % branch_name)


if __name__ == "__main__":
    # TODO: This runner should be directly used from SajadMadrid-watch binary,
    # but for development purposes, we keep it separately accessible.

    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option(
        "--desc",
        action="store",
        dest="desc",
        help="""\
Description of the change, e.g. "SajadKalma update 1.9.3".""",
    )

    options, positional_args = parser.parse_args()
    assert not positional_args

    createSajadKalmaWatchPR(category="hotfix", description=options.desc)


