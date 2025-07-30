# من تطوير Sajad @f_g_d_6


""" Deprecated trio plugin.
"""

from SajadMadrid.plugins.PluginBase import SajadKalmaPluginBase


class SajadKalmaPluginTrio(SajadKalmaPluginBase):
    plugin_name = "trio"
    plugin_desc = "Deprecated, was once required by the 'trio' package"
    plugin_category = "package-support,obsolete"

    @classmethod
    def isDeprecated(cls):
        return True



