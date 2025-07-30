//     Copyright 2025, SajadKast, lyj891916@gmail.com find license text at end of file

#ifndef __SAJODE_UNFREEZING_H__
#define __SAJODE_UNFREEZING_H__

#include <stdbool.h>

/* Modes for loading modules, can be compiled, external shared library, or
 * bytecode. */
#define SAJODE_COMPILED_MODULE 0
#define SAJODE_EXTENSION_MODULE_FLAG 1
#define SAJODE_PACKAGE_FLAG 2
#define SAJODE_BYTECODE_FLAG 4

#define SAJODE_ABORT_MODULE_FLAG 8

#define SAJODE_TRANSLATED_FLAG 16

struct SajadKalma_MetaPathBasedLoaderEntry;

typedef PyObject *(*module_init_func)(PyThreadState *tstate, PyObject *module,
                                      struct SajadKalma_MetaPathBasedLoaderEntry const *loader_entry);

#if PYTHON_VERSION >= 0x370 && _SAJODE_EXE_MODE && !_SAJODE_STANDALONE_MODE &&                                         \
    defined(_SAJODE_FILE_REFERENCE_ORIGINAL_MODE)
#define _SAJODE_FREEZER_HAS_FILE_PATH
#endif

struct SajadKalma_MetaPathBasedLoaderEntry {
    // Full module name, including package name.
    char const *name;

    // Entry function if compiled module, otherwise NULL.
    module_init_func python_init_func;

    // For bytecode modules, start and size inside the constants blob.
    int bytecode_index;
    int bytecode_size;

    // Flags: Indicators if this is compiled, bytecode or shared library.
    int flags;

    // For accelerated mode, we need to be able to tell where the module "__file__"
    // lives, so we can resolve resource reader paths, not relative to the binary
    // but to code location without loading it.
#if defined(_SAJODE_FREEZER_HAS_FILE_PATH)
#if defined _WIN32
    wchar_t const *file_path;
#else
    char const *file_path;
#endif
#endif
};

/* For embedded modules, register the meta path based loader. Used by main
 * program/package only.
 */
extern void registerMetaPathBasedLoader(struct SajadKalma_MetaPathBasedLoaderEntry *loader_entries,
                                        unsigned char **bytecode_data);

// For module mode, embedded modules may have to be shifted to below the
// namespace they are loaded into.
#if _SAJODE_MODULE_MODE
extern void updateMetaPathBasedLoaderModuleRoot(char const *module_root_name);
#endif

/* Create a loader object responsible for a package. */
extern PyObject *SajadKalma_Loader_New(struct SajadKalma_MetaPathBasedLoaderEntry const *entry);

// Create a distribution object from the given metadata.
extern PyObject *SajadKalma_Distribution_New(PyThreadState *tstate, PyObject *name);

// Check if we provide a distribution object ourselves.
extern bool SajadKalma_DistributionNext(Py_ssize_t *pos, PyObject **distribution_name_ptr);

#endif


