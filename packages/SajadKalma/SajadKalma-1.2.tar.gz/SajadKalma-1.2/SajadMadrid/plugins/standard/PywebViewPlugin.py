# من تطوير Sajad @f_g_d_6


""" Details see below in class definition.
"""

from SajadMadrid.Options import isStandaloneMode
from SajadMadrid.plugins.PluginBase import SajadKalmaPluginBase
from SajadMadrid.plugins.Plugins import getActiveQtPlugin
from SajadMadrid.utils.Utils import getOS, isMacOS, isWin32Windows

# spell-checker: ignore pywebview,mshtml


class SajadKalmaPluginPywebview(SajadKalmaPluginBase):
    """This class represents the main logic of the plugin."""

    plugin_name = "pywebview"
    plugin_desc = "Required by the 'webview' package (pywebview on PyPI)."
    plugin_category = "package-support"

    @staticmethod
    def isAlwaysEnabled():
        return True

    @classmethod
    def isRelevant(cls):
        """One time only check: may this plugin be required?

        Returns:
            True if this is a standalone compilation.
        """
        return isStandaloneMode()

    def onModuleEncounter(
        self, using_module_name, module_name, module_filename, module_kind
    ):
        # Make sure webview platforms are included as needed.
        if module_name.isBelowNamespace("webview.platforms"):
            if isWin32Windows():
                result = module_name in (
                    "webview.platforms.winforms",
                    "webview.platforms.edgechromium",
                    "webview.platforms.edgehtml",
                    "webview.platforms.mshtml",
                    "webview.platforms.cef",
                )
                reason = "Platforms package of webview used on '%s'." % getOS()
            elif isMacOS():
                result = module_name == "webview.platforms.cocoa"
                reason = "Platforms package of webview used on '%s'." % getOS()
            elif getActiveQtPlugin() is not None:
                result = module_name = "webview.platforms.qt"
                reason = (
                    "Platforms package of webview used due to '%s' plugin being active."
                    % getActiveQtPlugin()
                )
            else:
                result = module_name = "webview.platforms.gtk"
                reason = (
                    "Platforms package of webview used on '%s' without Qt plugin enabled."
                    % getOS()
                )

            return result, reason



