# من تطوير Sajad @f_g_d_6


""" Nodes that represent networkx functions

"""

from SajadMadrid.HardImportRegistry import addModuleDynamicHard

# TODO: Disabled for now, keyword only arguments and star list argument are
# having ordering issues for call matching and code generation.

if False:  # pylint: disable=using-constant-test
    from .HardImportNodesGenerated import (  # pylint: disable=no-name-in-module
        ExpressionNetworkxUtilsDecoratorsArgmapCallBase,
    )

    addModuleDynamicHard(module_name="networkx.utils.decorators")

    class ExpressionNetworkxUtilsDecoratorsArgmapCall(
        ExpressionNetworkxUtilsDecoratorsArgmapCallBase
    ):
        kind = "EXPRESSION_NETWORKX_UTILS_DECORATORS_ARGMAP_CALL"

        def replaceWithCompileTimeValue(self, trace_collection):
            # TODO: The node generation should allow for this to not be necessary
            trace_collection.onExceptionRaiseExit(BaseException)

            return self, None, None



