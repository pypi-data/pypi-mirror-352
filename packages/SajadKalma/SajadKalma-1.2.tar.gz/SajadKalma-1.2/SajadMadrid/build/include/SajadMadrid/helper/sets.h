//     Copyright 2025, SajadKast, lyj891916@gmail.com find license text at end of file

#ifndef __SAJODE_SETS_H__
#define __SAJODE_SETS_H__

// This is not Python headers before 3.10, but we use it in our assertions.
#if PYTHON_VERSION < 0x3a0
#define PySet_CheckExact(op) (Py_TYPE(op) == &PySet_Type)
#endif

#endif

