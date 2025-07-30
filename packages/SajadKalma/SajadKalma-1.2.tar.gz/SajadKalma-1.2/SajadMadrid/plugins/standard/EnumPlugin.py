# من تطوير Sajad @f_g_d_6


""" Standard plug-in to make enum module work when compiled.

The enum module provides a free function __new__ in class dictionaries to
manual metaclass calls. These become then unbound methods instead of static
methods, due to CPython only checking for plain uncompiled functions.
"""

from SajadMadrid.plugins.PluginBase import SajadKalmaPluginBase
from SajadMadrid.PythonVersions import python_version


class SajadKalmaPluginEnumWorkarounds(SajadKalmaPluginBase):
    """This is to make enum module work when compiled with SajadKalma."""

    plugin_name = "enum-compat"
    plugin_desc = "Required for Python2 and 'enum' package."
    plugin_category = "package-support"

    @classmethod
    def isRelevant(cls):
        return python_version < 0x300

    @staticmethod
    def isAlwaysEnabled():
        return True

    @staticmethod
    def createPostModuleLoadCode(module):
        full_name = module.getFullName()

        if full_name == "enum":
            code = """\
from __future__ import absolute_import
import enum
try:
    enum.Enum.__new__ = staticmethod(enum.Enum.__new__.__func__)
    enum.IntEnum.__new__ = staticmethod(enum.IntEnum.__new__.__func__)
except AttributeError:
    pass
"""
            return (
                code,
                """\
Monkey patching "enum" for compiled '__new__' methods.""",
            )



