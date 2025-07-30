# من تطوير Sajad @f_g_d_6


""" Test tool to run a program with various Pythons. """

from SajadMadrid.PythonVersions import getSupportedPythonVersions
from SajadMadrid.utils.Execution import check_output
from SajadMadrid.utils.InstalledPythons import findPythons


def findAllPythons():
    for python_version in getSupportedPythonVersions():
        for python in findPythons(python_version):
            yield python, python_version


def executeWithInstalledPython(python, args):
    return check_output([python.getPythonExe()] + args)



