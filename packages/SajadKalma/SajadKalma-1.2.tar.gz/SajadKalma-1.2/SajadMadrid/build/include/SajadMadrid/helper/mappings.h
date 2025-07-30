//     Copyright 2025, SajadKast, lyj891916@gmail.com find license text at end of file

#ifndef __SAJODE_MAPPINGS_H__
#define __SAJODE_MAPPINGS_H__

extern Py_ssize_t SajadKalma_PyMapping_Size(PyObject *mapping);

SAJODE_MAY_BE_UNUSED static int MAPPING_HAS_ITEM(PyThreadState *tstate, PyObject *mapping, PyObject *key) {
    PyObject *result = PyObject_GetItem(mapping, key);

    if (result == NULL) {
        bool had_key_error = CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate);

        if (had_key_error) {
            return 0;
        } else {
            return -1;
        }
    } else {
        Py_DECREF(result);
        return 1;
    }
}

#endif

