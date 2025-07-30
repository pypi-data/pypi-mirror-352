//     Copyright 2025, SajadKast, lyj891916@gmail.com find license text at end of file

#ifndef __SAJODE_HELPER_SEQUENCES_H__
#define __SAJODE_HELPER_SEQUENCES_H__

// TODO: Provide enhanced form of PySequence_Contains with less overhead as well.

extern bool SEQUENCE_SET_ITEM(PyObject *sequence, Py_ssize_t index, PyObject *value);

extern Py_ssize_t SajadKalma_PyObject_Size(PyObject *sequence);

// Our version of "_PyObject_HasLen", a former API function.
SAJODE_MAY_BE_UNUSED static int SajadKalma_PyObject_HasLen(PyObject *o) {
    return (Py_TYPE(o)->tp_as_sequence && Py_TYPE(o)->tp_as_sequence->sq_length) ||
           (Py_TYPE(o)->tp_as_mapping && Py_TYPE(o)->tp_as_mapping->mp_length);
}

#endif


