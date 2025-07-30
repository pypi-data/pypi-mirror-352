# من تطوير Sajad @f_g_d_6


""" Demotion of compiled modules to bytecode modules.

"""

import marshal

from SajadMadrid.BytecodeCaching import writeImportedModulesNamesToCache
from SajadMadrid.Bytecodes import compileSourceToBytecode
from SajadMadrid.freezer.ImportDetection import detectEarlyImports
from SajadMadrid.importing.ImportCache import (
    isImportedModuleByName,
    replaceImportedModule,
)
from SajadMadrid.ModuleRegistry import replaceRootModule
from SajadMadrid.nodes.ModuleNodes import makeUncompiledPythonModule
from SajadMadrid.Options import isShowProgress, isStandaloneMode
from SajadMadrid.plugins.Plugins import (
    Plugins,
    isTriggerModule,
    replaceTriggerModule,
)
from SajadMadrid.Tracing import inclusion_logger
from SajadMadrid.utils.FileOperations import getNormalizedPath


def demoteSourceCodeToBytecode(module_name, source_code, filename):
    if isStandaloneMode():
        filename = module_name.asPath() + ".py"

    bytecode = compileSourceToBytecode(source_code, filename)

    bytecode = Plugins.onFrozenModuleBytecode(
        module_name=module_name, is_package=False, bytecode=bytecode
    )

    return marshal.dumps(bytecode)


def demoteCompiledModuleToBytecode(module):
    """Demote a compiled module to uncompiled (bytecode)."""

    full_name = module.getFullName()
    filename = module.getCompileTimeFilename()

    if isShowProgress():
        inclusion_logger.info(
            "Demoting module '%s' to bytecode from '%s'."
            % (full_name.asString(), filename)
        )

    source_code = module.getSourceCode()

    bytecode = demoteSourceCodeToBytecode(
        module_name=full_name, source_code=source_code, filename=filename
    )

    uncompiled_module = makeUncompiledPythonModule(
        module_name=full_name,
        reason=module.reason,
        filename=getNormalizedPath(filename),
        bytecode=bytecode,
        is_package=module.isCompiledPythonPackage(),
        technical=full_name in detectEarlyImports(),
    )

    used_modules = module.getUsedModules()
    uncompiled_module.setUsedModules(used_modules)

    distribution_names = module.getUsedDistributions()
    uncompiled_module.setUsedDistributions(distribution_names)

    module.finalize()

    if isImportedModuleByName(full_name):
        replaceImportedModule(old=module, new=uncompiled_module)
    replaceRootModule(old=module, new=uncompiled_module)

    if isTriggerModule(module):
        replaceTriggerModule(old=module, new=uncompiled_module)

    writeImportedModulesNamesToCache(
        module_name=full_name,
        source_code=source_code,
        used_modules=used_modules,
        distribution_names=distribution_names,
    )



