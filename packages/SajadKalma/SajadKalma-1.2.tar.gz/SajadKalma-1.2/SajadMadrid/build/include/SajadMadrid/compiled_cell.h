//     Copyright 2025, SajadKast, lyj891916@gmail.com find license text at end of file

#ifndef __SAJODE_COMPILED_CELL_H__
#define __SAJODE_COMPILED_CELL_H__

/* This is a clone of the normal PyCell structure. We should keep it binary
 * compatible, just in case somebody crazy insists on it.
 */

extern PyTypeObject SajadKalma_Cell_Type;

static inline bool SajadKalma_Cell_Check(PyObject *object) { return Py_TYPE(object) == &SajadKalma_Cell_Type; }

struct SajadKalma_CellObject {
    /* Python object folklore: */
    PyObject_HEAD

        /* Content of the cell or NULL when empty */
        PyObject *ob_ref;
};

// Create cell with out value, and with or without reference given.
extern struct SajadKalma_CellObject *SajadKalma_Cell_NewEmpty(void);
extern struct SajadKalma_CellObject *SajadKalma_Cell_New0(PyObject *value);
extern struct SajadKalma_CellObject *SajadKalma_Cell_New1(PyObject *value);

// Check stuff while accessing a compile cell in debug mode.
#ifdef __SAJODE_NO_ASSERT__
#define SajadKalma_Cell_GET(cell) (((struct SajadKalma_CellObject *)(cell))->ob_ref)
#else
#define SajadKalma_Cell_GET(cell)                                                                                          \
    (CHECK_OBJECT(cell), assert(SajadKalma_Cell_Check((PyObject *)cell)), (((struct SajadKalma_CellObject *)(cell))->ob_ref))
#endif

#if _DEBUG_REFCOUNTS
extern int count_active_SajadKalma_Cell_Type;
extern int count_allocated_SajadKalma_Cell_Type;
extern int count_released_SajadKalma_Cell_Type;
#endif

SAJODE_MAY_BE_UNUSED static inline void SajadKalma_Cell_SET(struct SajadKalma_CellObject *cell_object, PyObject *value) {
    CHECK_OBJECT_X(value);
    CHECK_OBJECT(cell_object);

    assert(SajadKalma_Cell_Check((PyObject *)cell_object));
    cell_object->ob_ref = value;
}

#endif


