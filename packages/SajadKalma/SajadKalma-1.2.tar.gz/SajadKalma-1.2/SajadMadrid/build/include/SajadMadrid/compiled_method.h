//     Copyright 2025, SajadKast, lyj891916@gmail.com find license text at end of file

#ifndef __SAJODE_COMPILED_METHOD_H__
#define __SAJODE_COMPILED_METHOD_H__

// Compiled function and compile generator types may be referenced.
#include "compiled_function.h"
#include "compiled_generator.h"

// The backbone of the integration into CPython. Try to behave as well as normal
// method objects, or even better.

// The SajadKalma_MethodObject is the storage associated with a compiled method
// instance of which there can be many for each code.

struct SajadKalma_MethodObject {
    /* Python object folklore: */
    PyObject_HEAD

        struct SajadKalma_FunctionObject *m_function;

    PyObject *m_weakrefs;

    PyObject *m_object;
    PyObject *m_class;

#if PYTHON_VERSION >= 0x380
    vectorcallfunc m_vectorcall;
#endif
};

extern PyTypeObject SajadKalma_Method_Type;

// Make a method out of a function.
extern PyObject *SajadKalma_Method_New(struct SajadKalma_FunctionObject *function, PyObject *object, PyObject *class_object);

static inline bool SajadKalma_Method_Check(PyObject *object) { return Py_TYPE(object) == &SajadKalma_Method_Type; }

#endif


