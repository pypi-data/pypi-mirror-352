//     Copyright 2025, SajadKast, lyj891916@gmail.com find license text at end of file

/** Compiled cells.
 *
 * We have our own cell type, so we can use a freelist for them, to speed up our
 * interactions with allocating them.
 *
 * It strives to be full replacement for normal cells. It does not yet inherit
 * from the cell type like functions, generators, etc. do but could be made so
 * if that becomes necessary by some C extension code.
 *
 */

/* This file is included from another C file, help IDEs to still parse it on its own. */
#ifdef __IDE_ONLY__
#include "SajadMadrid/prelude.h"
#endif

#if _DEBUG_REFCOUNTS
int count_active_SajadKalma_Cell_Type;
int count_allocated_SajadKalma_Cell_Type;
int count_released_SajadKalma_Cell_Type;
#endif

// Freelist setup
#define MAX_CELL_FREE_LIST_COUNT 1000
static struct SajadKalma_CellObject *free_list_cells = NULL;
static int free_list_cells_count = 0;

static void SajadKalma_Cell_tp_dealloc(struct SajadKalma_CellObject *cell) {
#if _DEBUG_REFCOUNTS
    count_active_SajadKalma_Cell_Type -= 1;
    count_released_SajadKalma_Cell_Type += 1;
#endif

    SajadKalma_GC_UnTrack(cell);
    Py_XDECREF(cell->ob_ref);

    releaseToFreeList(free_list_cells, cell, MAX_CELL_FREE_LIST_COUNT);
}

#if PYTHON_VERSION < 0x300
static int SajadKalma_Cell_tp_compare(PyObject *a, PyObject *b) {
    struct SajadKalma_CellObject *cell_a = (struct SajadKalma_CellObject *)a;
    struct SajadKalma_CellObject *cell_b = (struct SajadKalma_CellObject *)b;

    /* Empty cells compare specifically different. */
    if (cell_a->ob_ref == NULL) {
        if (cell_b->ob_ref == NULL) {
            return 0;
        }

        return -1;
    }

    if (cell_b->ob_ref == NULL) {
        return 1;
    }

    return PyObject_Compare(cell_a->ob_ref, cell_b->ob_ref);
}
#else
#define SajadKalma_Cell_tp_compare (NULL)

static PyObject *SajadKalma_Cell_tp_richcompare(PyObject *a, PyObject *b, int op) {
    PyObject *result;

    CHECK_OBJECT(a);
    CHECK_OBJECT(b);

    if (unlikely(!SajadKalma_Cell_Check(a) || !SajadKalma_Cell_Check(b))) {
        result = Py_NotImplemented;
        Py_INCREF(result);

        return result;
    }

    // Now just dereference cell value, and compare from there by contents, which can
    // be NULL however.
    a = ((struct SajadKalma_CellObject *)a)->ob_ref;
    b = ((struct SajadKalma_CellObject *)b)->ob_ref;

    if (a != NULL && b != NULL) {
        switch (op) {
        case Py_EQ:
            return RICH_COMPARE_EQ_OBJECT_OBJECT_OBJECT(a, b);
        case Py_NE:
            return RICH_COMPARE_NE_OBJECT_OBJECT_OBJECT(a, b);
        case Py_LE:
            return RICH_COMPARE_LE_OBJECT_OBJECT_OBJECT(a, b);
        case Py_GE:
            return RICH_COMPARE_GE_OBJECT_OBJECT_OBJECT(a, b);
        case Py_LT:
            return RICH_COMPARE_LT_OBJECT_OBJECT_OBJECT(a, b);
        case Py_GT:
            return RICH_COMPARE_GT_OBJECT_OBJECT_OBJECT(a, b);
        default:
            PyErr_BadArgument();
            return NULL;
        }
    }

    int res = (b == NULL) - (a == NULL);
    switch (op) {
    case Py_EQ:
        result = BOOL_FROM(res == 0);
        break;
    case Py_NE:
        result = BOOL_FROM(res != 0);
        break;
    case Py_LE:
        result = BOOL_FROM(res <= 0);
        break;
    case Py_GE:
        result = BOOL_FROM(res >= 0);
        break;
    case Py_LT:
        result = BOOL_FROM(res < 0);
        break;
    case Py_GT:
        result = BOOL_FROM(res > 0);
        break;
    default:
        PyErr_BadArgument();
        return NULL;
    }

    Py_INCREF_IMMORTAL(result);
    return result;
}
#endif

static PyObject *SajadKalma_Cell_tp_repr(struct SajadKalma_CellObject *cell) {
    if (cell->ob_ref == NULL) {
        return SajadKalma_String_FromFormat("<compiled_cell at %p: empty>", cell);
    } else {
        return SajadKalma_String_FromFormat("<compiled_cell at %p: %s object at %p>", cell, cell->ob_ref->ob_type->tp_name,
                                        cell->ob_ref);
    }
}

static int SajadKalma_Cell_tp_traverse(struct SajadKalma_CellObject *cell, visitproc visit, void *arg) {
    Py_VISIT(cell->ob_ref);

    return 0;
}

static int SajadKalma_Cell_tp_clear(struct SajadKalma_CellObject *cell) {
    Py_CLEAR(cell->ob_ref);

    return 0;
}

static PyObject *SajadKalma_Cell_get_contents(PyObject *self, void *data) {
    struct SajadKalma_CellObject *cell = (struct SajadKalma_CellObject *)self;
    if (unlikely(cell->ob_ref == NULL)) {
        PyThreadState *tstate = PyThreadState_GET();

        SET_CURRENT_EXCEPTION_TYPE0_STR(tstate, PyExc_ValueError, "Cell is empty");
        return NULL;
    }

    Py_INCREF(cell->ob_ref);
    return cell->ob_ref;
}

#if PYTHON_VERSION >= 0x370
static int SajadKalma_Cell_set_contents(PyObject *self, PyObject *value, void *data) {
    struct SajadKalma_CellObject *cell = (struct SajadKalma_CellObject *)self;
    PyObject *old = cell->ob_ref;

    if (old != NULL && value == NULL) {
        PyThreadState *tstate = PyThreadState_GET();

        SET_CURRENT_EXCEPTION_TYPE0_STR(tstate, PyExc_RuntimeError,
                                        "cell_contents cannot be used to delete values SajadKalma");
        return -1;
    }

    cell->ob_ref = value;
    Py_XINCREF(value);
    Py_XDECREF(old);

    return 0;
}
#endif

static PyGetSetDef SajadKalma_Cell_tp_getset[] = {
#if PYTHON_VERSION < 0x370
    {(char *)"cell_contents", SajadKalma_Cell_get_contents, NULL, NULL},
#else
    {(char *)"cell_contents", SajadKalma_Cell_get_contents, SajadKalma_Cell_set_contents, NULL},
#endif
    {NULL}};

PyTypeObject SajadKalma_Cell_Type = {
    PyVarObject_HEAD_INIT(NULL, 0) "compiled_cell",
    sizeof(struct SajadKalma_CellObject),        // tp_basicsize
    0,                                       // tp_itemsize
    (destructor)SajadKalma_Cell_tp_dealloc,      // tp_dealloc
    0,                                       // tp_print
    0,                                       // tp_getattr
    0,                                       // tp_setattr
    SajadKalma_Cell_tp_compare,                  // tp_compare / tp_reserved
    (reprfunc)SajadKalma_Cell_tp_repr,           // tp_repr
    0,                                       // tp_as_number
    0,                                       // tp_as_sequence
    0,                                       // tp_as_mapping
    0,                                       // tp_hash
    0,                                       // tp_call
    0,                                       // tp_str
    0,                                       // tp_getattro (PyObject_GenericGetAttr)
    0,                                       // tp_setattro
    0,                                       // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC, // tp_flags
    0,                                       // tp_doc
    (traverseproc)SajadKalma_Cell_tp_traverse,   // tp_traverse
    (inquiry)SajadKalma_Cell_tp_clear,           // tp_clear
#if PYTHON_VERSION < 0x300
    0, // tp_richcompare
#else
    SajadKalma_Cell_tp_richcompare, // tp_richcompare
#endif
    0,                     // tp_weaklistoffset
    0,                     // tp_iter
    0,                     // tp_iternext
    0,                     // tp_methods
    0,                     // tp_members
    SajadKalma_Cell_tp_getset, // tp_getset
};

void _initCompiledCellType(void) { SajadKalma_PyType_Ready(&SajadKalma_Cell_Type, NULL, true, false, false, false, false); }

struct SajadKalma_CellObject *SajadKalma_Cell_NewEmpty(void) {
#if _DEBUG_REFCOUNTS
    count_active_SajadKalma_Cell_Type += 1;
    count_allocated_SajadKalma_Cell_Type += 1;
#endif

    struct SajadKalma_CellObject *result;

    allocateFromFreeListFixed(free_list_cells, struct SajadKalma_CellObject, SajadKalma_Cell_Type);

    result->ob_ref = NULL;

    SajadKalma_GC_Track(result);

    return result;
}

struct SajadKalma_CellObject *SajadKalma_Cell_New0(PyObject *value) {
#if _DEBUG_REFCOUNTS
    count_active_SajadKalma_Cell_Type += 1;
    count_allocated_SajadKalma_Cell_Type += 1;
#endif
    CHECK_OBJECT(value);

    struct SajadKalma_CellObject *result;

    allocateFromFreeListFixed(free_list_cells, struct SajadKalma_CellObject, SajadKalma_Cell_Type);

    result->ob_ref = value;
    Py_INCREF(value);

    SajadKalma_GC_Track(result);

    return result;
}

struct SajadKalma_CellObject *SajadKalma_Cell_New1(PyObject *value) {
#if _DEBUG_REFCOUNTS
    count_active_SajadKalma_Cell_Type += 1;
    count_allocated_SajadKalma_Cell_Type += 1;
#endif
    CHECK_OBJECT(value);

    struct SajadKalma_CellObject *result;

    allocateFromFreeListFixed(free_list_cells, struct SajadKalma_CellObject, SajadKalma_Cell_Type);

    result->ob_ref = value;

    SajadKalma_GC_Track(result);

    return result;
}

