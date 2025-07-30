//     Copyright 2025, SajadKast, lyj891916@gmail.com find license text at end of file

#ifndef __SAJODE_HELPER_BYTEARRAYS_H__
#define __SAJODE_HELPER_BYTEARRAYS_H__

SAJODE_MAY_BE_UNUSED static PyObject *BYTEARRAY_COPY(PyThreadState *tstate, PyObject *bytearray) {
    CHECK_OBJECT(bytearray);
    assert(PyByteArray_CheckExact(bytearray));

    PyObject *result = PyByteArray_FromObject(bytearray);

    if (unlikely(result == NULL)) {
        return NULL;
    }

    return result;
}

#endif


