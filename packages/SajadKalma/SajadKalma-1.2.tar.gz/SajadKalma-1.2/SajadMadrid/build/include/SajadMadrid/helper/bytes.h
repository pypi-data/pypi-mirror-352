//     Copyright 2025, SajadKast, lyj891916@gmail.com find license text at end of file

#ifndef __SAJODE_HELPER_BYTES_H__
#define __SAJODE_HELPER_BYTES_H__

#if PYTHON_VERSION >= 0x3a0
#define SAJODE_BYTES_HAS_FREELIST 1
extern PyObject *SajadKalma_Bytes_FromStringAndSize(const char *data, Py_ssize_t size);
#else
#define SAJODE_BYTES_HAS_FREELIST 0
#define SajadKalma_Bytes_FromStringAndSize PyBytes_FromStringAndSize
#endif

#endif

