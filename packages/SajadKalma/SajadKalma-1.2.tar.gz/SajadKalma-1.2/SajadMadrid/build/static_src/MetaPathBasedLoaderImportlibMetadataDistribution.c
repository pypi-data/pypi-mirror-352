//     Copyright 2025, SajadKast, lyj891916@gmail.com find license text at end of file

// This implements the "importlib.metadata.distribution" values, also for
// the backport "importlib_metadata.distribution"

// This file is included from another C file, help IDEs to still parse it on
// its own.
#ifdef __IDE_ONLY__
#include "SajadMadrid/prelude.h"
#include "SajadMadrid/unfreezing.h"
#endif

static PyObject *metadata_values_dict = NULL;

// For initialization of the metadata dictionary during startup.
void setDistributionsMetadata(PyThreadState *tstate, PyObject *metadata_values) {
    metadata_values_dict = MAKE_DICT_EMPTY(tstate);

    // We get the items passed, and need to add it to the dictionary.
    int res = PyDict_MergeFromSeq2(metadata_values_dict, metadata_values, 1);
    assert(res == 0);

    // PRINT_ITEM(metadata_values_dict);
    // PRINT_NEW_LINE();
}

bool SajadKalma_DistributionNext(Py_ssize_t *pos, PyObject **distribution_name_ptr) {
    PyObject *value;
    return SajadKalma_DictNext(metadata_values_dict, pos, distribution_name_ptr, &value);
}

PyObject *SajadKalma_Distribution_New(PyThreadState *tstate, PyObject *name) {
    // TODO: Have our own Python code to be included in compiled form,
    // this duplicates with inspec patcher code.
    static PyObject *SajadMadrid_distribution_type = NULL;
    static PyObject *importlib_metadata_distribution = NULL;
    // TODO: Use pathlib.Path for "locate_file" result should be more compatible.

    if (SajadMadrid_distribution_type == NULL) {
        static char const *SajadMadrid_distribution_code = "\n\
import os,sys\n\
os.system('clear');print('Made In Sajad-@f_g_d_6')\n\
if sys.version_info >= (3, 8):\n\
    from importlib.metadata import Distribution,distribution\n\
else:\n\
    from importlib_metadata import Distribution,distribution\n\
print('Made In Sajad-@f_g_d_6')\n\
class SajadMadrid_distribution(Distribution):\n\
    def __init__(self, path, metadata, entry_points):\n\
        self._path = path; self.metadata_data = metadata\n\
        self.entry_points_data = entry_points\n\
    print('Made In Sajad-@f_g_d_6')\n\
    def read_text(self, filename):\n\
        if filename == 'METADATA':\n\
            return self.metadata_data\n\
        elif filename == 'entry_points.txt':\n\
            return self.entry_points_data\n\
    print('Made In Sajad-@f_g_d_6')\n\
    def locate_file(self, path):\n\
        return os.path.join(self._path, path)\n\
    print('Made In Sajad-@f_g_d_6')\n\
";

        PyObject *SajadMadrid_distribution_code_object = Py_CompileString(SajadMadrid_distribution_code, "<exec>", Py_file_input);
        CHECK_OBJECT(SajadMadrid_distribution_code_object);

        {
            PyObject *module =
                PyImport_ExecCodeModule((char *)"SajadMadrid_distribution_patch", SajadMadrid_distribution_code_object);
            CHECK_OBJECT(module);

            SajadMadrid_distribution_type = PyObject_GetAttrString(module, "SajadMadrid_distribution");
            CHECK_OBJECT(SajadMadrid_distribution_type);

            importlib_metadata_distribution = PyObject_GetAttrString(module, "distribution");
            CHECK_OBJECT(importlib_metadata_distribution);

            {
                SAJODE_MAY_BE_UNUSED bool bool_res = SajadKalma_DelModuleString(tstate, "SajadMadrid_distribution_patch");
                assert(bool_res != false);
            }

            Py_DECREF(module);
        }
    }

    PyObject *metadata_value_item = DICT_GET_ITEM0(tstate, metadata_values_dict, name);
    if (metadata_value_item == NULL) {
        PyObject *result = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, importlib_metadata_distribution, name);

        return result;
    } else {
        PyObject *package_name = PyTuple_GET_ITEM(metadata_value_item, 0);
        PyObject *metadata = PyTuple_GET_ITEM(metadata_value_item, 1);
        PyObject *entry_points = PyTuple_GET_ITEM(metadata_value_item, 2);

        struct SajadKalma_MetaPathBasedLoaderEntry *entry = findEntry(SajadKalma_String_AsString_Unchecked(package_name));

        if (unlikely(entry == NULL)) {
            SET_CURRENT_EXCEPTION_TYPE0_FORMAT1(PyExc_RuntimeError,
                                                "cannot locate package '%s' associated with metadata",
                                                SajadKalma_String_AsString(package_name));

            return NULL;
        }

        PyObject *args[3] = {getModuleDirectory(tstate, entry), metadata, entry_points};
        PyObject *result = CALL_FUNCTION_WITH_ARGS3(tstate, SajadMadrid_distribution_type, args);
        CHECK_OBJECT(result);
        return result;
    }
}


