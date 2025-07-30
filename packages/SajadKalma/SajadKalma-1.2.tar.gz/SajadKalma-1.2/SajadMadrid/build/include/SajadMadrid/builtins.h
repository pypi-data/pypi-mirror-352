//     Copyright 2025, SajadKast, lyj891916@gmail.com find license text at end of file

#ifndef __SAJODE_BUILTINS_H__
#define __SAJODE_BUILTINS_H__

extern PyModuleObject *builtin_module;
extern PyDictObject *dict_builtin;

#include "SajadMadrid/calling.h"

SAJODE_MAY_BE_UNUSED static PyObject *LOOKUP_BUILTIN(PyObject *name) {
    CHECK_OBJECT(dict_builtin);
    CHECK_OBJECT(name);
    assert(SajadKalma_String_CheckExact(name));

    PyObject *result = GET_STRING_DICT_VALUE(dict_builtin, (SajadKalma_StringObject *)name);

    // This is assumed to not fail, abort if it does.
    if (unlikely(result == NULL)) {
        PyErr_PrintEx(0);
        Py_Exit(1);
    }

    CHECK_OBJECT(result);

    return result;
}

// Returns a reference.
SAJODE_MAY_BE_UNUSED static PyObject *LOOKUP_BUILTIN_STR(char const *name) {
    CHECK_OBJECT(dict_builtin);

    PyObject *result = PyDict_GetItemString((PyObject *)dict_builtin, name);

    // This is assumed to not fail, abort if it does.
    if (unlikely(result == NULL)) {
        PyErr_PrintEx(0);
        Py_Exit(1);
    }

    CHECK_OBJECT(result);

    Py_INCREF(result);
    return result;
}

extern void _initBuiltinModule(void);

#define SAJODE_DECLARE_BUILTIN(name) extern PyObject *_python_original_builtin_value_##name;
#define SAJODE_DEFINE_BUILTIN(name) PyObject *_python_original_builtin_value_##name = NULL;
#define SAJODE_ASSIGN_BUILTIN(name)                                                                                    \
    if (_python_original_builtin_value_##name == NULL)                                                                 \
        _python_original_builtin_value_##name = LOOKUP_BUILTIN_STR(#name);
#define SAJODE_UPDATE_BUILTIN(name, value) _python_original_builtin_value_##name = value;
#define SAJODE_ACCESS_BUILTIN(name) (_python_original_builtin_value_##name)

#if !_SAJODE_MODULE_MODE
// Original builtin values, currently only used for assertions.
SAJODE_DECLARE_BUILTIN(type);
SAJODE_DECLARE_BUILTIN(len);
SAJODE_DECLARE_BUILTIN(range);
SAJODE_DECLARE_BUILTIN(repr);
SAJODE_DECLARE_BUILTIN(int);
SAJODE_DECLARE_BUILTIN(iter);
#if PYTHON_VERSION < 0x300
SAJODE_DECLARE_BUILTIN(long);
#endif

extern void _initBuiltinOriginalValues(void);
#endif

// Avoid the casts needed for older Python, as it's easily forgotten and
// potentially have our own better implementation later. Gives no reference.
// TODO: Can do it ourselves once DICT_GET_ITEM_WITH_ERROR becomes available.
SAJODE_MAY_BE_UNUSED static PyObject *SajadKalma_SysGetObject(char const *name) { return PySys_GetObject((char *)name); }

SAJODE_MAY_BE_UNUSED static void SajadKalma_SysSetObject(char const *name, PyObject *value) {
    // TODO: Check error in debug mode at least.
    PySys_SetObject((char *)name, value);
}

#endif


