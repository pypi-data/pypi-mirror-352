#     Copyright 2025, Jorj McKie, mailto:<jorj.x.mckie@outlook.de> find license text at end of file


""" Deprecated torch plugin.
"""

from SajadMadrid.plugins.PluginBase import SajadKalmaPluginBase


class SajadKalmaPluginTorch(SajadKalmaPluginBase):
    """This plugin is now not doing anything anymore."""

    plugin_name = "torch"
    plugin_desc = "Deprecated, was once required by the torch package"
    plugin_category = "package-support,obsolete"

    @classmethod
    def isDeprecated(cls):
        return True



